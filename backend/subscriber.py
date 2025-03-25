import paho.mqtt.client as mqtt
import json
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import time
import threading
from dotenv import load_dotenv
import os


# MQTT broker details
load_dotenv('keys.env')
BROKER_ADDRESS = os.getenv("BROKER_ADDRESS")
BROKER_PORT = os.getenv("BROKER_PORT")
MOSQUITTO_USER = os.getenv("MOSQUITTO_USER")
MOSQUITTO_PASS = os.getenv("MOSQUITTO_PASS")

topic = "deepwatt/#"
#topic will have the structure: deepwatt/<device_id>

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///instance/deepwatt.db')  
Session = sessionmaker(bind=engine)

deviceData = {}
deviceDataMutex = threading.Lock()
# Define the data model
class DeviceReading(Base):
    __tablename__ = 'device_readings'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String, index=True)
    rms_current = Column(Float)
    power = Column(Float)
    dailyEnergy = Column(Float)
    timestamp = Column(Integer, index=True)
    received_at = Column(DateTime)

# Create tables
Base.metadata.create_all(engine)

# Callback for connection
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to broker")
        # Subscribe to the topic
        client.subscribe(topic)
        print("Subscribed to topic: " + topic)
    else:
        print("Connection failed with code", rc)

# Callback for message
def on_message(client, userdata, message):
    try:
        payload = message.payload
        device_id = message.topic[9:]  # extracts device id from the topic
        received = json.loads(payload)
        print(received)
        
        # Store in database
        session = Session()
        
        try:
            reading = DeviceReading(
                device_id=device_id,
                rms_current=received.get('rmsCurrent'),
                power = received.get('power'),
                dailyEnergy = received.get('dailyEnergy'),
                timestamp=received.get('timestamp'),
                received_at = datetime.now() 
            )
            session.add(reading)
            session.commit()
            with deviceDataMutex:
                deviceData[device_id] = {
                    "rms_current" : received.get('rmsCurrent'),
                    "timestamp": received.get('timestamp'),
                    "power": received.get('power'),
                    "dailyEnergy": received.get('dailyEnergy'),
                }
            print(f"Data from device {device_id} stored successfully")
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()
            
    except json.JSONDecodeError:
        print("Failed to decode JSON payload")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc, properties=None ,reasonCode=None ):
    print(f"Disconnected from broker, with code {rc}...")
    #retry to connect
    while(1):
        try:
            client.reconnect()
            print("Reconnected successfully!")
            return
        except Exception as err:
            print("%s. Reconnect failed. Retrying...", err)
        time.sleep(1)


def run_subscriber():
    # Create MQTT client with proper settings for MQTTv5
    client = mqtt.Client(client_id="deepwatt_subscriber2", protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    # Assign event callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Set username and password
    client.username_pw_set(username=MOSQUITTO_USER, password=MOSQUITTO_PASS)
    
    # Connect to broker
    client.connect(BROKER_ADDRESS, int(BROKER_PORT))

    # Start the loop
    client.loop_forever()

if __name__ == '__main__':
    run_subscriber()