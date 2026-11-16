🌍 Environmental Sensor Data Analysis System Using MongoDB


📌 Project Overview
The Environmental Sensor Data Analysis System Using MongoDB is a data analytics project designed to monitor, analyse, and visualize environmental sensor readings across multiple locations.

The system uses Python for data generation and analysis, MongoDB for storing and querying environmental data, Pandas for data processing, and Streamlit with Plotly for interactive visualization.

It analyses environmental parameters such as temperature, humidity, PM2.5, PM10, and CO2 to identify pollution patterns, detect abnormal readings, and evaluate data quality.

Note: This project currently uses simulated environmental sensor readings for demonstration and analysis. It does not collect live sensor data.

🎯 Project Objectives
Generate and manage environmental sensor datasets.
Store structured sensor readings in MongoDB.
Perform statistical and location-wise environmental analysis.
Identify pollution categories based on PM2.5 values.
Detect potentially abnormal environmental readings.
Identify missing values, duplicate records, and invalid readings.
Visualize environmental trends through an interactive dashboard.
Export filtered environmental data for further analysis.


🛠️ Technologies Used
Technology	Purpose
Python	Core programming language
MongoDB	NoSQL database
PyMongo	Python-MongoDB connectivity
Pandas	Data processing and analysis
NumPy	Numerical operations
Streamlit	Interactive dashboard
Plotly	Data visualization
Git and GitHub	Version control



🏗️ System Architecture
The project follows this workflow:

Simulated Sensor Data
        |
        v
  generate_data.py
        |
        v
  sensor_readings.csv
        |
        v
   import_data.py
        |
        v
      MongoDB
        |
   +----+----+
   |         |
   v         v
analyze_data.py   app.py
   |                |
   v                v
Statistical       Streamlit
Analysis          Dashboard
   |                |
   +-------+--------+
           |
           v
 Environmental Insights
 Anomaly Detection
 Data Quality Analysis
 Interactive Visualizations



📊 Dataset Description
The project generates 10,000 simulated environmental sensor readings from five sensors across five locations.

Sensor ID	Location
SENSOR_01	Bangalore
SENSOR_02	Mysore
SENSOR_03	Mangalore
SENSOR_04	Hubli
SENSOR_05	Belgaum
Dataset Attributes
Attribute	Description
sensor_id	Environmental sensor identifier
location	Sensor location
timestamp	Date and time of the reading
temperature	Temperature in °C
humidity	Relative humidity in %
pm25	PM2.5 concentration in µg/m³
pm10	PM10 concentration in µg/m³
co2	CO2 concentration in ppm
The simulated readings use five-minute timestamp intervals, beginning on January 1, 2026.


⚙️ Project Features
1. Environmental Data Generation
Generates 10,000 simulated sensor records.
Includes five sensors across five locations.
Generates temperature, humidity, PM2.5, PM10, and CO2 readings.
Exports the generated dataset into CSV format.
2. MongoDB Data Storage
Connects Python applications to MongoDB using PyMongo.
Stores sensor readings in the EnvironmentalDB database.
Uses the sensor_readings collection.
Supports data retrieval and aggregation queries.
3. Statistical Data Analysis
Overall environmental statistics.
Sensor-wise environmental analysis.
Location-wise pollution analysis.
Daily environmental trends.
Average, minimum, and maximum measurements.
4. Pollution Classification
PM2.5 readings are grouped into four project-defined categories:

PM2.5 Range (µg/m³)	Category
≤ 15	Low
> 15 to 35	Moderate
> 35 to 55	High
> 55	Very High
These are demonstration categories defined for this project, not official regulatory classifications.

5. Advanced Anomaly Detection
The system identifies potentially abnormal readings using project-defined thresholds.

Parameter	Demonstration Threshold
Temperature	> 40°C
PM2.5	> 35 µg/m³
PM10	> 100 µg/m³
CO2	> 1000 ppm
The dashboard displays individual alert counts, total unique abnormal readings, and the reason each reading was flagged. Individual alert counts may overlap when one reading exceeds multiple thresholds.

6. Data Quality Analysis
The system performs three major data-quality checks:

Missing environmental values.
Duplicate sensor-timestamp groups.
Invalid environmental readings.
7. Interactive Streamlit Dashboard
The dashboard provides:

Environmental KPI metrics.
Temperature trend visualization.
Humidity distribution.
CO2 comparison across locations.
PM2.5 versus PM10 scatter plot.
Pollution classification chart.
Location-wise environmental analysis.
Sensor-wise performance analysis.
Advanced anomaly detection.
Data-quality indicators.
Filtered CSV data export.
Users can filter readings by location, sensor, and date range.


📁 Project Structure
environmental_sensor_analysis/
│
├── generate_data.py
├── import_data.py
├── analyze_data.py
├── app.py
├── sensor_readings.csv
├── test_data_quality.py
├── cleanup_test_data.py
├── README.md
└── .gitignore
The venv/ virtual environment folder is created locally and should not be committed to GitHub.


🚀 Installation and Setup
Prerequisites
Python 3.11 or later
MongoDB Community Server
MongoDB Compass (optional, for database visualization)
Visual Studio Code
Git
Step 1: Clone the Repository
git clone https://github.com/Bhoom4/environmental_sensor_analysis.git
cd environmental_sensor_analysis
Step 2: Create a Virtual Environment
python -m venv venv
Activate it on Windows PowerShell:

.\venv\Scripts\Activate.ps1
Step 3: Install Dependencies
pip install pymongo pandas numpy streamlit plotly dnspython
Step 4: Start MongoDB
Ensure the MongoDB Community Server service is running.

The project uses this local MongoDB connection:

mongodb://localhost:27017
Step 5: Generate Environmental Sensor Data
python generate_data.py
This generates the sensor_readings.csv dataset.

Step 6: Import Data into MongoDB
python import_data.py
This imports the generated records into:

Database: EnvironmentalDB
Collection: sensor_readings
Important: The current import script clears the target collection before inserting the CSV records. Run it only when you intend to reload the dataset.

Step 7: Perform Environmental Data Analysis
python analyze_data.py
This executes the statistical analysis, pollution classification, anomaly detection, and data-quality checks.

Step 8: Launch the Dashboard
streamlit run app.py
The dashboard will open in your web browser.



🧪 Testing and Validation
The project includes controlled testing of data-quality detection.

The following test cases were performed:

Test Case	Expected Detection
Missing humidity value	1 missing value
Duplicate sensor-timestamp records	1 duplicate group
Invalid temperature of 99°C	1 invalid reading
All three test cases were successfully detected by the dashboard.

After testing, the temporary test records were removed, preserving the original 10,000 records.


📈 Project Outcomes
The implemented system demonstrates:

Environmental data generation and storage using MongoDB.
Statistical analysis using MongoDB aggregation pipelines.
Interactive environmental data visualization.
Pollution classification using PM2.5 values.
Threshold-based anomaly detection.
Missing-value, duplicate, and invalid-reading detection.
Interactive filtering and CSV export.


🔮 Future Enhancements
Integration with real IoT environmental sensors.
Real-time environmental data ingestion.
Automated alerts and notifications.
Advanced time-series forecasting.
Machine learning-based anomaly detection.
Deployment to a cloud platform.
Historical environmental trend prediction.


👩‍💻 Author
Bhoomika Harish Naik

GitHub: Bhoom4

Project Repository: Environmental Sensor Data Analysis System

Developed using Python, MongoDB, Pandas, Streamlit, and Plotly.
