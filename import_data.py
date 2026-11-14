
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017"

DATABASE_NAME = "EnvironmentalDB"
COLLECTION_NAME = "sensor_readings"

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    # Verify connection
    client.admin.command("ping")
    print("MongoDB connected successfully!")

    # Select database and collection
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Read CSV dataset
    df = pd.read_csv(
        "sensor_readings.csv",
        parse_dates=["timestamp"]
    )

    print("Dataset loaded successfully!")
    print("Total records:", len(df))

    # Convert DataFrame into MongoDB documents
    records = df.to_dict("records")

    # Avoid duplicate records when rerunning this
    # initial dataset-import script.
    collection.delete_many({})

    # Insert records in batches
    batch_size = 1000

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        collection.insert_many(batch)

        print(
            f"Inserted {min(i + batch_size, len(records))}"
            f"/{len(records)} records"
        )

    # Create indexes for faster queries
    collection.create_index("sensor_id")
    collection.create_index("location")
    collection.create_index("timestamp")

    print("\nData imported successfully!")
    print("Database:", DATABASE_NAME)
    print("Collection:", COLLECTION_NAME)
    print("Total documents:", collection.count_documents({}))

except PyMongoError as error:
    print("MongoDB error:", error)

except FileNotFoundError:
    print("Error: sensor_readings.csv not found!")

except Exception as error:
    print("Unexpected error:", error)

finally:
    if "client" in locals():
        client.close()

