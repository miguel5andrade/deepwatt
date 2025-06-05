import sqlite3
import pandas as pd
import joblib
from datetime import datetime, timedelta
import time
import logging

# === CONFIGURATION ===
DB_PATH = '../backend/instance/deepwatt.db'
MODEL_PATH = 'current_forecast_model.pkl'
SCALER_PATH = 'forecast_scaler.pkl'
DEVICE_ID = 'board-cc:50:e3:60:e6:80'
N_FORECASTS = 10  # predict next 10 minutes

# === SETUP LOGGING ===
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    filename='current-forecast.log',
                    level=logging.INFO)

# === LOAD MODEL AND SCALER ===
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# === GET LAST 15 MINUTES OF DATA ===
now = time.time()
start_time = int(now - 900)  # 15 minutes ago
end_time = int(now)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

query = """
SELECT timestamp, rms_current
FROM device_readings
WHERE device_id = ? AND timestamp >= ? AND timestamp <= ? AND rms_current IS NOT NULL
ORDER BY timestamp ASC
"""
df = pd.read_sql_query(query, conn, params=(DEVICE_ID, start_time, end_time))

if df.empty or len(df) < 10:
    logging.warning("Not enough data for forecasting.")
    conn.close()
    exit()

# === PREPROCESSING ===
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df.set_index('datetime', inplace=True)
df = df[(df['rms_current'] >= 0) & (df['rms_current'] < 200)]

# Compute feature columns
df['mean_5'] = df['rms_current'].rolling(window=5, min_periods=1).mean()
df['std_5'] = df['rms_current'].rolling(window=5, min_periods=1).std().fillna(0)
df['hour'] = df.index.hour
df['minute'] = df.index.minute
df['day_of_week'] = df.index.dayofweek

# Use the last row as the current state for forecasting
base_row = df.iloc[[-1]]  # keep as DataFrame
base_time = base_row.index[0]

# === LOOP TO PREDICT NEXT 10 MINUTES ===
features = ['rms_current', 'mean_5', 'std_5', 'hour', 'minute', 'day_of_week']
forecast_rows = []

for i in range(1, N_FORECASTS + 1):
    # Create a copy of the last known row
    future_row = base_row.copy()
    
    # Increment time by i minutes
    future_time = base_time + timedelta(minutes=i)
    future_row.index = [future_time]
    
    # Update time-based features
    future_row['hour'] = future_time.hour
    future_row['minute'] = future_time.minute
    future_row['day_of_week'] = future_time.weekday()
    
    # Scale and predict
    X_future = scaler.transform(future_row[features])
    predicted_current = float(model.predict(X_future)[0])
    
    # Store for DB insertion
    forecast_rows.append((int(time.time()), int(future_time.timestamp()), predicted_current, DEVICE_ID))

# === INSERT ALL FORECASTS INTO DB ===
cursor.executemany("""
    INSERT INTO forecasted_current (prediction_time, forecast_for_time, predicted_current, device_id)
    VALUES (?, ?, ?, ?)
""", forecast_rows)

conn.commit()
conn.close()

logging.info(f"{N_FORECASTS} forecasts inserted for device {DEVICE_ID}.")
