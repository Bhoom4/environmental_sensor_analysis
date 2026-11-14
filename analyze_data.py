
from pymongo import MongoClient
from pprint import pprint

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "EnvironmentalDB"
COLLECTION_NAME = "sensor_readings"

# Demo alert thresholds (project-defined, not regulatory standards)
THRESHOLDS = {
    "temperature": 40,
    "pm25": 35,
    "pm10": 100,
    "co2": 1000
}


def main():

    client = MongoClient(MONGO_URI)

    try:
        client.admin.command("ping")

        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        print("\n===================================")
        print(" ENVIRONMENTAL SENSOR DATA ANALYSIS")
        print("===================================")

        # 1. Overall dataset statistics
        print("\n1. OVERALL ENVIRONMENTAL STATISTICS")

        overall_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_records": {"$sum": 1},
                    "avg_temperature": {"$avg": "$temperature"},
                    "max_temperature": {"$max": "$temperature"},
                    "min_temperature": {"$min": "$temperature"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "avg_pm25": {"$avg": "$pm25"},
                    "avg_pm10": {"$avg": "$pm10"},
                    "avg_co2": {"$avg": "$co2"}
                }
            }
        ]

        overall = list(collection.aggregate(overall_pipeline))

        if overall:
            pprint(overall[0])

        # 2. Sensor-wise analysis
        print("\n2. SENSOR-WISE ANALYSIS")

        sensor_pipeline = [
            {
                "$group": {
                    "_id": "$sensor_id",
                    "location": {"$first": "$location"},
                    "total_readings": {"$sum": 1},
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "avg_pm25": {"$avg": "$pm25"},
                    "avg_co2": {"$avg": "$co2"}
                }
            },
            {"$sort": {"avg_pm25": -1}}
        ]

        for result in collection.aggregate(sensor_pipeline):
            pprint(result)

        # 3. Location-wise pollution analysis
        print("\n3. LOCATION-WISE POLLUTION ANALYSIS")

        location_pipeline = [
            {
                "$group": {
                    "_id": "$location",
                    "avg_pm25": {"$avg": "$pm25"},
                    "avg_pm10": {"$avg": "$pm10"},
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_co2": {"$avg": "$co2"},
                    "total_readings": {"$sum": 1}
                }
            },
            {"$sort": {"avg_pm25": -1}}
        ]

        for result in collection.aggregate(location_pipeline):
            pprint(result)
 

        # 4. Daily environmental trends
        print("\n4. DAILY ENVIRONMENTAL TRENDS")

        daily_pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    },
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_pm25": {"$avg": "$pm25"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "avg_co2": {"$avg": "$co2"}
                }
            },
            {"$sort": {"_id": 1}},
            {"$limit": 10}
        ]

        for result in collection.aggregate(daily_pipeline):
            pprint(result)

        # 5. Data quality check
        print("\n5. DATA QUALITY ANALYSIS")

        missing_pipeline = [
            {
                "$project": {
                    "missing_count": {
                        "$add": [
                            {
                                "$cond": [
                                    {"$eq": [{"$type": "$temperature"}, "missing"]},
                                    1, 0
                                ]
                            },
                            {
                                "$cond": [
                                    {"$eq": [{"$type": "$humidity"}, "missing"]},
                                    1, 0
                                ]
                            },
                            {
                                "$cond": [
                                    {"$eq": [{"$type": "$pm25"}, "missing"]},
                                    1, 0
                                ]
                            },
                            {
                                "$cond": [
                                    {"$eq": [{"$type": "$pm10"}, "missing"]},
                                    1, 0
                                ]
                            },
                            {
                                "$cond": [
                                    {"$eq": [{"$type": "$co2"}, "missing"]},
                                    1, 0
                                ]
                            }
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_missing_values": {"$sum": "$missing_count"}
                }
            }
        ]

        quality = list(collection.aggregate(missing_pipeline))
        print("Missing environmental values:",
              quality[0]["total_missing_values"] if quality else 0)

        # 6. Anomaly detection
        print("\n6. POTENTIAL ENVIRONMENTAL ANOMALIES")

        anomaly_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"temperature": {"$gt": THRESHOLDS["temperature"]}},
                        {"pm25": {"$gt": THRESHOLDS["pm25"]}},
                        {"pm10": {"$gt": THRESHOLDS["pm10"]}},
                        {"co2": {"$gt": THRESHOLDS["co2"]}}
                    ]
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "sensor_id": 1,
                    "location": 1,
                    "timestamp": 1,
                    "temperature": 1,
                    "pm25": 1,
                    "pm10": 1,
                    "co2": 1
                }
            },
            {"$limit": 10}
        ]

        anomalies = list(collection.aggregate(anomaly_pipeline))

        print("Potential abnormal readings (showing up to 10):")
        pprint(anomalies)

 
        # 7. Pollution classification analysis
        print("\n7. POLLUTION CLASSIFICATION")

        classification_pipeline = [
            {
                "$project": {
                    "pollution_category": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {"$lte": ["$pm25", 15]},
                                    "then": "Low"
                                },
                                {
                                    "case": {"$lte": ["$pm25", 35]},
                                    "then": "Moderate"
                                },
                                {
                                    "case": {"$lte": ["$pm25", 55]},
                                    "then": "High"
                                }
                            ],
                            "default": "Very High"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$pollution_category",
                    "total_readings": {"$sum": 1}
                }
            },
            {"$sort": {"total_readings": -1}}
        ]

        for result in collection.aggregate(classification_pipeline):
            pprint(result)


        # 8. Duplicate and invalid data analysis
        print("\n8. DATA QUALITY CHECKS")

        duplicate_pipeline = [
            {
                "$group": {
                    "_id": {
                        "sensor_id": "$sensor_id",
                        "timestamp": "$timestamp"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "count": {"$gt": 1}
                }
            },
            {
                "$count": "duplicate_groups"
            }
        ]

        duplicates = list(collection.aggregate(duplicate_pipeline))

        print(
            "Duplicate sensor-timestamp groups:",
            duplicates[0]["duplicate_groups"] if duplicates else 0
        )

        invalid_count = collection.count_documents({
            "$or": [
                {"temperature": {"$lt": 10}},
                {"temperature": {"$gt": 45}},
                {"humidity": {"$lt": 20}},
                {"humidity": {"$gt": 100}},
                {"pm25": {"$lt": 0}},
                {"pm10": {"$lt": 0}},
                {"co2": {"$lt": 300}}
            ]
        })

        print("Invalid readings:", invalid_count)
        print("\nAnalysis completed successfully!")

    except Exception as error:
        print("Analysis error:", error)
    finally:
        client.close()
        

if __name__ == "__main__":
    main()
