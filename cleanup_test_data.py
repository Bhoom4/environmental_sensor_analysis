
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

db = client["EnvironmentalDB"]
collection = db["sensor_readings"]

# Count records before cleanup
before_count = collection.count_documents({})

# Delete only temporary test records
result = collection.delete_many({
    "test_record": True
})

# Count records after cleanup
after_count = collection.count_documents({})

print("Test records removed:", result.deleted_count)
print("Records before cleanup:", before_count)
print("Records after cleanup:", after_count)

client.close()
    