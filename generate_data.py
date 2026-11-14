
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

NUM_RECORDS = 10000

sensors = {
    "SENSOR_01": "Bangalore",
    "SENSOR_02": "Mysore",
    "SENSOR_03": "Mangalore",
    "SENSOR_04": "Hubli",
    "SENSOR_05": "Belgaum"
}

data = []
start_time = datetime(2026, 1, 1)

for i in range(NUM_RECORDS):

    sensor_id = np.random.choice(list(sensors.keys()))
    location = sensors[sensor_id]

    temperature = np.random.normal(28, 5)
    humidity = np.random.uniform(30, 90)
    pm25 = np.random.exponential(25)
    pm10 = pm25 * np.random.uniform(1.2, 2.0)
    co2 = np.random.normal(450, 100)

    data.append({
        "sensor_id": sensor_id,
        "location": location,
        "timestamp": start_time + timedelta(minutes=5 * i),
        "temperature": round(np.clip(temperature, 10, 45), 2),
        "humidity": round(np.clip(humidity, 20, 100), 2),
        "pm25": round(pm25, 2),
        "pm10": round(pm10, 2),
        "co2": round(np.clip(co2, 300, 1500), 2)
    })

df = pd.DataFrame(data)

df.to_csv("sensor_readings.csv", index=False)

print("Dataset generated successfully!")
print("Total records:", len(df))
print("\nSample records:")
print(df.head())

print("\nDataset statistics:")
print(df.describe())
