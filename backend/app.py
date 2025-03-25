from flask import Flask, jsonify
from flask_cors import CORS 
import json
from datetime import datetime
from flask import request
from flask_sqlalchemy import SQLAlchemy
import subscriber as sub
import threading
import time

DATABASE_URL = 'sqlite:///deepwatt.db'

app = Flask(__name__)

CORS(app)   

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the data model
class DeviceReading(db.Model):
    __tablename__ = 'device_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String, index=True)
    rms_current = db.Column(db.Float)
    timestamp = db.Column(db.Integer, index=True)
    power = db.Column(db.Float)
    dailyEnergy = db.Column(db.Float)
    received_at = db.Column(db.DateTime)

    def to_dict(self):
        return{
            "timestamp": self.timestamp,
            "rms_current": self.rms_current,
            "power":self.power,
            "dailyEnergy":self.dailyEnergy,
        }


with app.app_context():
    db.create_all()




@app.route('/data/<device_id>', methods=['GET'])
def data(device_id):
    # Get parameters from query string instead of headers
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    
    # Convert to integers if they exist
    if start_time and end_time:
        try:
            start_time = int(start_time)
            end_time = int(end_time)
        except ValueError:
            return jsonify({"error": "Invalid time parameters"}), 400
    else:
        # Default to last 24 hours if no parameters provided
        current_time = int(time.time())
        start_time = current_time - 86400  # 24 hours ago
        end_time = current_time
        
    # Fix the filter syntax to use SQLAlchemy operators correctly
    data = DeviceReading.query.all()
    filtered_data = []

    for record in data:
        if(record.device_id == device_id and record.timestamp >= start_time and record.timestamp <= end_time):
            filtered_data.append(record)


    return jsonify([record.to_dict() for record in filtered_data])

@app.route('/realtime/<device_id>', methods=["GET"])
def realtime_data(device_id):
    try:
        
        with sub.deviceDataMutex:
            #check if the last stored data is recent (10 sec at max)
            if (time.time() - sub.deviceData[device_id]["timestamp"] > 10):
                return jsonify({"error": "No data available"}), 404
            data = sub.deviceData[device_id] 
        return data, 200
    
    except:
        return jsonify({"error": "No data available"}), 404


if __name__ == '__main__':
    subscriber_thread = threading.Thread(target = sub.run_subscriber)
    subscriber_thread.start()
    app.run(debug=False, host='0.0.0.0', port=5501)