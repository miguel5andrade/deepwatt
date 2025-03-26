import paho.mqtt.client as mqtt
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import time
from dotenv import load_dotenv
import os


# MQTT broker details
load_dotenv('keys.env')
BROKER_ADDRESS = os.getenv("BROKER_ADDRESS")
BROKER_PORT = os.getenv("BROKER_PORT")
MOSQUITTO_USER = os.getenv("MOSQUITTO_USER")
MOSQUITTO_PASS = os.getenv("MOSQUITTO_PASS")

#topic will have the structure: deepwatt/<device_id>

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///instance/deepwatt.db')  
Session = sessionmaker(bind=engine)



class Budget(Base):
    __tablename__ = 'budget'
    id = Column(Integer, primary_key=True)
    monitoring_device_id = Column(String, index=True)
    feedback_device_id = Column(String)
    budget = Column(Float)
  
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
        
    else:
        print("Connection failed with code", rc)

# Callback for message
def on_publish(client, userdata, mid, reason_code, properties):
    print("message published")

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


def push_budget_message():
    # Create MQTT client with proper settings for MQTTv5
    client = mqtt.Client(client_id="deepwatt_subscriber2", protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    # Assign event callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    # Set username and password
    client.username_pw_set(username=MOSQUITTO_USER, password=MOSQUITTO_PASS)
    
    # Connect to broker
    client.connect(BROKER_ADDRESS, int(BROKER_PORT))

    session = Session()

    budgets = session.query(Budget).all()

    for record in budgets:
        last_reading = session.query(DeviceReading).filter_by(device_id = record.monitoring_device_id).order_by(DeviceReading.id.desc()).first()
        usage_percentage = last_reading.dailyEnergy / record.budget * 100
        print(usage_percentage)
        topic = "budget/" + record.feedback_device_id
        payload = usage_percentage
        client.publish(topic=topic,payload= payload, qos=0, retain=0, properties=None)


    client.disconnect()
    
if __name__ == '__main__':
    push_budget_message()