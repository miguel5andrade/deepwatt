import paho.mqtt.client as mqtt
import json
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# MQTT broker details
broker_address = "test.mosquitto.org"
broker_port = 1883
topic = "deepwatt/#"
#topic will have the structure: deepwatt/<device_id>

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///instance/deepwatt.db')  
Session = sessionmaker(bind=engine)

# Define the data model
class DeviceReading(Base):
    __tablename__ = 'device_readings'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String, index=True)
    rms_current = Column(Float)
    timestamp = Column(Integer, index=True)
    received_at = Column(DateTime)

# Create tables
Base.metadata.create_all(engine)

# Callback for connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        # Subscribe to the topic
        client.subscribe(topic)
    else:
        print("Connection failed with code", rc)

# Callback for message
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        device_id = message.topic[9:]  # extracts device id from the topic
        received = json.loads(payload)
        print(received)
        
        # Store in database
        session = Session()
        
        try:
            reading = DeviceReading(
                device_id=device_id,
                rms_current=received.get('rms_current'),
                timestamp=received.get('timestamp'),
                received_at = datetime.now() 
            )
            session.add(reading)
            session.commit()
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

def run_subscriber():
    # Create MQTT client with protocol version explicitly set to avoid deprecation warning
    client = mqtt.Client(protocol=mqtt.MQTTv5)

    # Assign event callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker
    client.connect(broker_address, broker_port)

    # Start the loop
    client.loop_forever()

if __name__ == '__main__':
    run_subscriber()