
import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime

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
# ANOMALY DETECTION
# ----------------------------------

st.subheader("⚠️ Potential Environmental Anomalies")

anomalies = filtered_df[
    (filtered_df["temperature"] > 40) |
    (filtered_df["pm25"] > 35) |
    (filtered_df["pm10"] > 100) |
    (filtered_df["co2"] > 1000)
].copy()

st.metric(
    "Potential Abnormal Readings",
    f"{len(anomalies):,}"
)

if not anomalies.empty:

    st.dataframe(
        anomalies[
            [
                "sensor_id",
                "location",
                "timestamp",
                "temperature",
                "pm25",
                "pm10",
                "co2"
            ]
        ].sort_values("timestamp", ascending=False),
        use_container_width=True,
        hide_index=True
    )

else:
    st.success("No readings exceeded the configured demo thresholds.")

st.caption(
    "Alerts use project-defined thresholds for demonstration, "
    "not official regulatory classifications."
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
