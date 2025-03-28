from flask import Flask, jsonify, make_response
from flask_cors import CORS 
import json
from datetime import datetime
from flask import request
from flask_sqlalchemy import SQLAlchemy
import subscriber as sub
import threading
import time
from flask_compress import Compress


DATABASE_URL = 'sqlite:///deepwatt.db'

app = Flask(__name__)
Compress(app)
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}}, supports_credentials=True)

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

class Budget(db.Model):
    __tablename__ = 'budget'
    id = db.Column(db.Integer, primary_key=True)
    monitoring_device_id = db.Column(db.String, index=True)
    feedback_device_id = db.Column(db.String)
    budget = db.Column(db.Float)
    
    def to_dict(self):
        return{
            "monitoring_device_id":self.monitoring_device_id,
            "feedback_device_id": self.feedback_device_id,
            "budget": self.budget,
        }

with app.app_context():
    db.create_all()

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


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


    return make_response(jsonify([record.to_dict() for record in filtered_data]))

@app.route('/realtime/<device_id>', methods=["GET"])
def realtime_data(device_id):
    try:
        
        with sub.deviceDataMutex:
            #check if the last stored data is recent (10 sec at max)
            if (time.time() - sub.deviceData[device_id]["timestamp"] > 10):
                return jsonify({"error": "No data available"}), 404
            data = sub.deviceData[device_id] 
        return make_response(jsonify(data))
    
    except:
        return jsonify({"error": "No data available"}), 404

@app.route('/budget/<monitoring_device_id>', methods=["GET"])
def get_budget(monitoring_device_id):
    
    record = Budget.query.filter_by(monitoring_device_id = monitoring_device_id).first()

    if not record:
        return jsonify({"error" : "No budget available"}), 404
    
    return make_response(jsonify(record.to_dict()))


@app.route('/update-budget/<monitoring_device_id>', methods=["POST"])
def change_budget(monitoring_device_id):
    data = request.get_json()
    budget = data.get('budget')
    feedback_device_id = data.get('feedback_device_id')

    record = Budget.query.filter_by(monitoring_device_id=monitoring_device_id).first()
    
    if not record:
        new_budget = Budget(
            monitoring_device_id=monitoring_device_id,
            budget=budget,
            feedback_device_id=feedback_device_id
        )
        db.session.add(new_budget)
    else:
        record.budget = budget
        record.feedback_device_id = feedback_device_id

    db.session.commit()
    return jsonify({"message": "Budget updated successfully"}), 200


def start_subscriber_thread():
    from threading import Thread
    from subscriber import run_subscriber
    thread = Thread(target=run_subscriber)
    thread.start()

if __name__ == '__main__':
    subscriber_thread = threading.Thread(target = sub.run_subscriber)
    subscriber_thread.start()
    app.run(debug=False, host='0.0.0.0', port=5501)
