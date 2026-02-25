# Motorsports Telemetry Analytics Pipeline

Built a real-time streaming architecture using Kafka, Apache Flink, and Streamlit to process and visualize motorsports telemetry data.

This project simulates live car telemetry (speed, RPM) and performs windowed aggregation to compute real-time performance analytics.


# Data Pipeline

Telemetry Producer (Python)
        ↓
Kafka (telemetry_raw topic)
        ↓
Apache Flink (5-sec tumbling window aggregation)
        ↓
Kafka (telemetry_analytics topic)
        ↓
Streamlit Dashboard (Live Visualization)

# Tech Stack Used

- **Apache Kafka :** Used for real-time ingestion and streaming of telemetry events between system components.

- **Apache Flink (PyFlink) :** Used for real-time stream processing and window-based aggregation of telemetry data.

- **Docker Compose:** Used to orchestrate and manage multi-container distributed services locally.

- **Streamlit + Plotly :** Used to build an interactive real-time dashboard for visualizing processed telemetry analytics.

- **Python 3.10: ** Used as the primary programming language for producer, processing logic, and dashboard development.

# How To Run The Project

1. Clean start using the commands:
```
docker compose down -v

docker compose up --build -d
```
Verify services are running:

```
docker compose ps
```

It should show an output like this:

2️. Create Kafka Topics
Make sure kafka is running as in the above picture
```
docker compose exec kafka \
kafka-topics --create \
--topic telemetry_raw \
--bootstrap-server kafka:29092 \
--replication-factor 1 \
--partitions 1

docker compose exec kafka \
kafka-topics --create \
--topic telemetry_analytics \
--bootstrap-server kafka:29092 \
--replication-factor 1 \
--partitions 1
```
Verify:
```
docker compose exec kafka \
kafka-topics --bootstrap-server kafka:29092 --list
```
Output should look like this:

3. Submit Flink Job
```
docker compose exec flink-jobmanager \
flink run -d -py /opt/flink/jobs/telemetry_job.py
```
Open Flink UI (Port 8081) to verify job is RUNNING.

4. Run the data producer

From project root:
```
pip install kafka-python
python kafka/telemetry_producer.py
```
This simulates live telemetry data.

5. Open the dashboard

Open Streamlit on port 8501.

You should see analysis graphs such as: 

At the bottom, the entire data can be downloaded in .csv format, as in output.csv

# Streaming Logic

**Kafka source topic:** *telemetry_raw*

Example event:
```
{
  "car_id": "CAR_1",
  "speed": 178.4,
  "rpm": 8450
}
```
**Data processing**

Keyed by : _car_id_

A 5-second tumbling window computes the average speed and average RPM, sends data to the kafka sink.

**Output Topic:**  _telemetry_analytics_

Example output:
```
{

  "car_id": "CAR_1",
  "avg_speed": 180.2,
  "avg_rpm": 8320
}
```

# Ports Used

Service	| Port 
--- | ---
Kafka	| 9092
Zookeeper	| 2181
Flink UI	| 8081
Streamlit |	8501

   
## Note:

- Producer runs on host, uses localhost:9092

- Flink & Streamlit run inside Docker, use kafka:29092

- Kafka topics must exist before submitting Flink job

- Use docker compose down -v before starting for a clean reset
