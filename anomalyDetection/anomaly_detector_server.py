import sqlite3
import pandas as pd
import joblib
from datetime import timedelta
import time
import logging 

DB_PATH = '../backend/instance/deepwatt.db'
MODEL_PATH = 'anomaly_model.pkl'
SCALER_PATH = 'scaler.pkl'
DEVICE_ID = 'board-cc:50:e3:60:e6:80'  

# Load the model and the scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',filename='anomaly-detector.log', level=logging.INFO)

# time period of 5 min
now = time.time()
start_time = int((now - 300)) #5min = 300 sec
end_time = int(now)


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

query = """
SELECT id, timestamp, rms_current, device_id
FROM device_readings
WHERE device_id = ? AND timestamp >= ? AND timestamp <= ? AND rms_current IS NOT NULL
ORDER BY timestamp ASC
"""
df = pd.read_sql_query(query, conn, params=(DEVICE_ID, start_time, end_time))

if df.empty:
    logging.warning("No new data in the last 5 min.")
    conn.close()
    exit()

# === Pre processing ===
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df.set_index('datetime', inplace=True)
df['current_scaled'] = scaler.transform(df[['rms_current']])

# === Anomaly detection ===
df['anomaly'] = model.predict(df[['current_scaled']])  # -1 = anomaly
anomalies = df[df['anomaly'] == -1]

# Insert anomalies in the db  
inserted = 0
for _, row in anomalies.iterrows():
    # check if this anomaly was already inserted
    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE device_reading_id = ?", (int(row['id']),))
    exists = cursor.fetchone()[0]

    if exists == 0:
        #if not, insert
        cursor.execute("""
            INSERT INTO anomalies (device_reading_id, rms_current, timestamp, device_id)
            VALUES (?, ?, ?, ?)
        """, (
            int(row['id']),
            float(row['rms_current']),
            int(row['timestamp']),
            row['device_id']
        ))
        inserted += 1

conn.commit()
conn.close()

if inserted:
    logging.info(f"Inserted {inserted} new anomalies.")
else:
    logging.info("No new anomalies.")
