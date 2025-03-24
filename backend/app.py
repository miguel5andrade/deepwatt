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
    received_at = db.Column(db.DateTime)

    def to_dict(self):
        return{
            "timestamp": self.timestamp,
            "rms_current": self.rms_current
        }


with app.app_context():
    db.create_all()



@app.route('/get-data')
def get_data():
    # Get headers from the request
    start_time = request.headers.get('startTime')
    end_time = request.headers.get('endTime')
    mac_address = request.headers.get('macaddress')

    data = []

    # Open the file and parse the lines
    with open('log_12_Dec_Portel.log', 'r') as file:
        for line in file:
            try:
                # Extract the timestamp and JSON part
                timestamp_end = line.find("{") - 1
                timestamp = line[:timestamp_end].strip()  # Extract the timestamp
                json_data = line[timestamp_end + 1:].strip()  # Extract the JSON string
                
                # Convert timestamp to epoch
                full_timestamp = f"2024 {timestamp}"  # Add year since it's missing
                epoch_time = int(datetime.strptime(full_timestamp, '%Y %b %d %H:%M:%S').timestamp())
                if(epoch_time < int(start_time) or epoch_time > int(end_time)):
                    continue
                
                # Filter data to send only 30 seconds from 30 seconds apart
                if len(data) > 0 and (epoch_time - data[-1]["timestamp"]) < 30:
                    continue
                # Parse JSON data
                json_data = json.loads(json_data)
                
                # Add parsed data to the list
                data.append({
                    "timestamp": epoch_time,
                    "voltage": json_data.get("system_voltage"),
                    "current": json_data.get("system_current"),
                    "soc": 0,
                    "temperature": 0,
                    "max_cell_voltage": 0,
                    "min_cell_voltage": 0
                })
            except Exception as e:
                print(f"Error parsing line: {line.strip()} -> {str(e)}")
                continue
    # Dump the data into a JSON file
    with open('output_data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return data

@app.route('/data/<device_id>', methods=['GET'])
def data(device_id):
    # Get headers from the request
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
        
    data = DeviceReading.query.filter(DeviceReading.device_id == device_id and DeviceReading.timestamp >= start_time and DeviceReading.timestamp <= end_time)

    return jsonify([record.to_dict() for record in data])

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