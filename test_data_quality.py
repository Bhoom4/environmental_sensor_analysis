
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["EnvironmentalDB"]
collection = db["sensor_readings"]

# Remove any previous test records
collection.delete_many({"test_record": True})

test_timestamp = datetime(2026, 2, 4, 23, 55)

# Test 1: Missing humidity
missing_record = {
    "sensor_id": "TEST_SENSOR_01",
    "location": "Bangalore",
    "timestamp": test_timestamp,
    "temperature": 28,
    "pm25": 20,
    "pm10": 35,
    "co2": 450,
    "test_record": True
}

# Test 2: Duplicate sensor-timestamp records
duplicate_record = {
    "sensor_id": "TEST_SENSOR_02",
    "location": "Mysore",
    "timestamp": test_timestamp,
    "temperature": 30,
    "humidity": 60,
    "pm25": 25,
    "pm10": 40,
    "co2": 500,
    "test_record": True
}

# Test 3: Invalid temperature
invalid_record = {
    "sensor_id": "TEST_SENSOR_03",
    "location": "Bangalore",
    "timestamp": test_timestamp,
    "temperature": 99,
    "humidity": 55,
    "pm25": 20,
    "pm10": 35,
    "co2": 450,
    "test_record": True
}

collection.insert_many([
    missing_record,
    duplicate_record,
    duplicate_record.copy(),
    invalid_record
])

print("Test records inserted successfully!")
print("Total test records:", collection.count_documents({
    "test_record": True
}))

client.close()
