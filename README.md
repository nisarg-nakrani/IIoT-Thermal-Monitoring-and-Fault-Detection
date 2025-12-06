# IIoT-Based Thermal System Monitoring & Predictive Fault Detection

This project is a complete **Industrial Internet of Things (IIoT)**
pipeline designed to monitor a thermal fluid system similar to those
used in chemical plants, heating loops, or fluid-processing pipelines.

we simulate the data streaming process using a real industrial dataset and push the
readings to a **PostgreSQL cloud database**, which is visualized in
**Streamlit**.

The system continuously tracks temperature, pressure, flow rate,
vibration, and electrical signals while raising alerts whenever values
drift into unsafe ranges. This demonstrates how industries use IIoT to
detect equipment problems long before failures occur.

------------------------------------------------------------------------

## Project Summary 

Industrial systems rarely fail suddenly they usually "warn us" through
small changes: a pump vibrates a bit more than usual, temperature creeps
slightly higher, flow drops by a few percent. Operators often miss these
early clues because they are subtle.

This project is built around that real-world problem.

To mimic an actual industrial environment, we built a **virtual sensor
stream** using a Kaggle dataset. A Python simulator reads each row as if
a real machine is sending data every 2 seconds. That data travels just
like an actual IIoT setup through a network layer to a central
PostgreSQL database.

From there, an interactive Streamlit dashboard displays live values,
historical trends, and instant alerts for abnormal behavior. The entire
flow recreates how modern plants detect overheating, leakage, power
fluctuations, or pump failures **before** they cause downtime.

This is not just a demonstration it is a complete proof-of-concept
for how predictive maintenance is implemented in real industries.

------------------------------------------------------------------------

## System Architecture

    Dataset (sensors)
            ↓
    Edge Layer (Raspberry Pi-style simulator)
            ↓
    Network Layer (TCP/IP database insertion)
            ↓
    Cloud Layer (PostgreSQL)
            ↓
    Application Layer (Streamlit Dashboard)

### Edge Layer

A Python script simulates real-time sensor readings, adds timestamps,
and sends each reading to PostgreSQL every 2 seconds.

### Cloud Layer

PostgreSQL acts as a central time-series database where all measurements
are stored.
This mimics industrial cloud platforms like AWS IoT, Azure IoT Hub, or
InfluxDB.

### Dashboard Layer

A Streamlit web app displays:

-   Live temperature, pressure, vibration trends.
-   Current system health.
-   Fault classifications.
-   Real-time alerts for dangerous conditions.

This gives operators actionable visibility into machine behavior.

------------------------------------------------------------------------

## What the System Monitors

  -----------------------------------------------------------------------
  Sensor Type                            Purpose
  -------------------------------------- --------------------------------
  **Temperature**                     Detect overheating or heater
                                      malfunctions

  **Vibration**                       Identify pump cavitation,
                                      misalignment, bearing issues

  **Pressure**                        Detect leaks or blockages

  **Flow Rate**                       Ensure fluid circulation is
                                      stable

  **Current / Voltage**               Monitor energy and electrical
                                      faults

  **FFT Components**                   Capture frequency-domain
                                       behavior for vibration analysis

  **Fault_Type**                      Pre-labeled states: Normal /
                                         Overheat / Leakage / Power Issue
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Real-Time Alerting

The dashboard generates alerts for:

-   High temperature.
-   Excessive vibration.
-   Unsafe pressure levels.
-   Fault types from dataset labels.

This simulates how real IIoT dashboards notify engineers through alarms.

------------------------------------------------------------------------

## How to Run the Project

### Install dependencies

    pip install -r requirements.txt

### Create the database table

    psql -U postgres -d IIOT_PROJECT -f create_tables.sql

### Start the simulator

    python simulator.py

### Start the dashboard

    streamlit run streamlit_app.py

------------------------------------------------------------------------

## What This Project Demonstrates

- End-to-end IIoT pipeline.
- Real-time data ingestion and visualization.
- Practical use of SQL for time-series industrial data.
- Early fault detection and alerting.
- Human-readable visualization for operators.
- Hands-on simulation of how predictive maintenance is built in industry.

------------------------------------------------------------------------

## Future Enhancements

-   Machine learning anomaly detection.
-   Predictive forecasting.
-   Multi-sensor scaling using MQTT or Kafka.
-   Automated corrective actions.
-   Cloud deployment.
