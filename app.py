
import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="Environmental Sensor Analytics",
    page_icon="🌍",
    layout="wide"
)

# ----------------------------------
# MONGODB CONNECTION
# ----------------------------------

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "EnvironmentalDB"
COLLECTION_NAME = "sensor_readings"


@st.cache_resource
def get_collection():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )
    client.admin.command("ping")
    return client[DATABASE_NAME][COLLECTION_NAME]


# ----------------------------------
# LOAD DATA
# ----------------------------------

@st.cache_data(ttl=60)
def load_data():
    collection = get_collection()

    records = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    df = pd.DataFrame(records)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


# ----------------------------------
# DASHBOARD HEADER
# ----------------------------------

st.title("🌍 Environmental Sensor Data Analysis")
st.markdown(
    "### Real-time-style environmental monitoring "
    "and analytics dashboard"
)

st.caption(
    "Data source: MongoDB | "
    "Dataset: Simulated environmental sensor readings"
)

# ----------------------------------
# FETCH DATA
# ----------------------------------

try:
    df = load_data()

    if df.empty:
        st.warning("No sensor records found in MongoDB.")
        st.stop()

except Exception as error:
    st.error(f"Unable to connect to MongoDB: {error}")
    st.stop()


# ----------------------------------
# SIDEBAR FILTERS
# ----------------------------------

st.sidebar.title("Dashboard Filters")

locations = sorted(df["location"].dropna().unique())

selected_locations = st.sidebar.multiselect(
    "Select Locations",
    locations,
    default=locations
)

sensors = sorted(df["sensor_id"].dropna().unique())

selected_sensors = st.sidebar.multiselect(
    "Select Sensors",
    sensors,
    default=sensors
)

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = df[
        (df["location"].isin(selected_locations)) &
        (df["sensor_id"].isin(selected_sensors)) &
        (df["timestamp"].dt.date >= start_date) &
        (df["timestamp"].dt.date <= end_date)
    ]

else:
    filtered_df = df.iloc[0:0]

# ----------------------------------
# POLLUTION CLASSIFICATION
# ----------------------------------

filtered_df = filtered_df.copy()

filtered_df["pollution_category"] = pd.cut(
    filtered_df["pm25"],
    bins=[-float("inf"), 15, 35, 55, float("inf")],
    labels=["Low", "Moderate", "High", "Very High"]
)


# ----------------------------------
# KPI METRICS
# ----------------------------------

st.subheader("Environmental Overview")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Readings",
    f"{len(filtered_df):,}"
)

col2.metric(
    "Average Temperature",
    f"{filtered_df['temperature'].mean():.2f} °C"
)

col3.metric(
    "Average Humidity",
    f"{filtered_df['humidity'].mean():.2f} %"
)

col4.metric(
    "Average CO2",
    f"{filtered_df['co2'].mean():.2f} ppm"
)

st.divider()


# ----------------------------------
# TEMPERATURE ANALYSIS
# ----------------------------------

st.subheader("🌡️ Temperature Analysis")

temperature_fig = px.line(
    filtered_df.sort_values("timestamp"),
    x="timestamp",
    y="temperature",
    color="sensor_id",
    title="Temperature Trends Across Sensors",
    labels={
        "timestamp": "Date and Time",
        "temperature": "Temperature (°C)",
        "sensor_id": "Sensor"
    }
)

st.plotly_chart(temperature_fig, use_container_width=True)


# ----------------------------------
# HUMIDITY AND CO2 ANALYSIS
# ----------------------------------

col1, col2 = st.columns(2)

with col1:
    humidity_fig = px.histogram(
        filtered_df,
        x="humidity",
        nbins=30,
        title="Humidity Distribution",
        labels={"humidity": "Humidity (%)"}
    )

    st.plotly_chart(
        humidity_fig,
        use_container_width=True
    )

with col2:
    co2_fig = px.box(
        filtered_df,
        x="location",
        y="co2",
        color="location",
        title="CO2 Levels Across Locations",
        labels={"co2": "CO2 (ppm)"}
    )

    st.plotly_chart(
        co2_fig,
        use_container_width=True
    )


# ----------------------------------
# AIR POLLUTION ANALYSIS
# ----------------------------------

st.subheader("🌫️ Air Pollution Analysis")

pollution_fig = px.scatter(
    filtered_df,
    x="pm25",
    y="pm10",
    color="location",
    size="pm25",
    hover_data=["sensor_id", "timestamp"],
    title="PM2.5 vs PM10 Across Locations",
    labels={
        "pm25": "PM2.5 (µg/m³)",
        "pm10": "PM10 (µg/m³)"
    }
)

st.plotly_chart(
    pollution_fig,
    use_container_width=True
)

# ----------------------------------
# POLLUTION CATEGORY DISTRIBUTION
# ----------------------------------

st.subheader("Pollution Classification")

category_counts = (
    filtered_df["pollution_category"]
    .value_counts()
    .reindex(
        ["Low", "Moderate", "High", "Very High"],
        fill_value=0
    )
    .reset_index()
)

category_counts.columns = ["Category", "Readings"]

classification_fig = px.bar(
    category_counts,
    x="Category",
    y="Readings",
    color="Category",
    title="Distribution of Pollution Categories",
    text="Readings"
)

st.plotly_chart(
    classification_fig,
    use_container_width=True
)

# ----------------------------------
# DATA QUALITY DASHBOARD
# ----------------------------------

st.subheader("🔍 Data Quality Analysis")

collection = get_collection()

# 1. Missing values
required_fields = [
    "temperature",
    "humidity",
    "pm25",
    "pm10",
    "co2"
]

missing_count = 0

for field in required_fields:
    missing_count += collection.count_documents({
        "$or": [
            {field: {"$exists": False}},
            {field: None}
        ]
    })

# 2. Duplicate sensor-timestamp groups
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

duplicate_count = (
    duplicates[0]["duplicate_groups"] if duplicates else 0
)

# 3. Invalid readings
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

quality_col1, quality_col2, quality_col3 = st.columns(3)

quality_col1.metric(
    "Missing Values",
    f"{missing_count:,}"
)

quality_col2.metric(
    "Duplicate Groups",
    f"{duplicate_count:,}"
)

quality_col3.metric(
    "Invalid Readings",
    f"{invalid_count:,}"
)

if missing_count == 0 and duplicate_count == 0 and invalid_count == 0:
    st.success("Database quality checks completed. No issues detected.")
else:
    st.warning("Potential data quality issues detected. Review the indicators above.")

# ----------------------------------
# LOCATION-WISE ANALYSIS
# ----------------------------------

st.subheader("📍 Location-Wise Environmental Analysis")

location_stats = (
    filtered_df.groupby("location")
    .agg(
        avg_temperature=("temperature", "mean"),
        avg_humidity=("humidity", "mean"),
        avg_pm25=("pm25", "mean"),
        avg_pm10=("pm10", "mean"),
        avg_co2=("co2", "mean"),
        total_readings=("sensor_id", "count")
    )
    .reset_index()
)

location_fig = px.bar(
    location_stats,
    x="location",
    y="avg_pm25",
    color="location",
    title="Average PM2.5 Levels by Location",
    labels={
        "location": "Location",
        "avg_pm25": "Average PM2.5 (µg/m³)"
    }
)

st.plotly_chart(
    location_fig,
    use_container_width=True
)

st.dataframe(
    location_stats.round(2),
    use_container_width=True,
    hide_index=True
)


# ----------------------------------
# SENSOR-WISE ANALYSIS
# ----------------------------------

st.subheader("📡 Sensor-Wise Performance")

sensor_stats = (
    filtered_df.groupby(["sensor_id", "location"])
    .agg(
        avg_temperature=("temperature", "mean"),
        avg_pm25=("pm25", "mean"),
        avg_humidity=("humidity", "mean"),
        avg_co2=("co2", "mean"),
        total_readings=("temperature", "count")
    )
    .reset_index()
)

st.dataframe(
    sensor_stats.round(2),
    use_container_width=True,
    hide_index=True
)



# ----------------------------------
# ADVANCED ANOMALY DETECTION
# ----------------------------------

st.subheader("⚠️ Advanced Environmental Anomaly Detection")

# Project-defined demo thresholds
TEMP_LIMIT = 40
PM25_LIMIT = 35
PM10_LIMIT = 100
CO2_LIMIT = 1000

# Identify abnormal readings
temperature_alerts = filtered_df["temperature"] > TEMP_LIMIT
pm25_alerts = filtered_df["pm25"] > PM25_LIMIT
pm10_alerts = filtered_df["pm10"] > PM10_LIMIT
co2_alerts = filtered_df["co2"] > CO2_LIMIT

# Combine all anomaly conditions
anomalies = filtered_df[
    temperature_alerts |
    pm25_alerts |
    pm10_alerts |
    co2_alerts
].copy()

# Display individual alert counts
alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)

alert_col1.metric(
    "High Temperature",
    f"{temperature_alerts.sum():,}"
)

alert_col2.metric(
    "High PM2.5",
    f"{pm25_alerts.sum():,}"
)

alert_col3.metric(
    "High PM10",
    f"{pm10_alerts.sum():,}"
)

alert_col4.metric(
    "High CO2",
    f"{co2_alerts.sum():,}"
)

st.metric(
    "Total Unique Abnormal Readings",
    f"{len(anomalies):,}"
)

# Identify the reason for each anomaly
def get_alert_reason(row):

    reasons = []

    if row["temperature"] > TEMP_LIMIT:
        reasons.append("High Temperature")

    if row["pm25"] > PM25_LIMIT:
        reasons.append("High PM2.5")

    if row["pm10"] > PM10_LIMIT:
        reasons.append("High PM10")

    if row["co2"] > CO2_LIMIT:
        reasons.append("High CO2")

    return ", ".join(reasons)


if not anomalies.empty:

    anomalies["alert_reason"] = anomalies.apply(
        get_alert_reason,
        axis=1
    )

    st.warning(
        "Potential environmental abnormalities detected."
    )

    st.dataframe(
        anomalies[
            [
                "sensor_id",
                "location",
                "timestamp",
                "temperature",
                "pm25",
                "pm10",
                "co2",
                "alert_reason"
            ]
        ].sort_values(
            "timestamp",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

else:
    st.success(
        "No readings exceeded the configured demo thresholds."
    )

st.caption(
    "Alerts use project-defined demonstration thresholds, "
    "not official regulatory standards. Individual alert counts "
    "may overlap when a reading exceeds multiple thresholds."
)


# ----------------------------------
# DOWNLOAD FILTERED DATA
# ----------------------------------

st.subheader("📥 Export Environmental Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="environmental_sensor_data.csv",
    mime="text/csv"
)


# ----------------------------------
# FOOTER
# ----------------------------------

st.divider()

st.caption(
    "Environmental Sensor Data Analysis System | "
    "Python • MongoDB • Pandas • Streamlit • Plotly"
)
