
import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import time
import plotly.express as px
import plotly.graph_objects as go


# Configuration
DB_HOST = os.getenv("IIOT_DB_HOST", "localhost")
DB_PORT = os.getenv("IIOT_DB_PORT", "5432")
DB_NAME = os.getenv("IIOT_DB_NAME", "IIOT_PROJECT")
DB_USER = os.getenv("IIOT_DB_USER", "postgres")
DB_PASS = os.getenv("IIOT_DB_PASS", "1234")
TABLE = os.getenv("IIOT_TABLE", "iiot_measurements")
DEFAULT_LOOKBACK_MIN = 60  

st.set_page_config(page_title="IIoT Live Visualizer", layout="wide")
st.title("IIoT Real-time Data Visualizer")


@st.cache_resource
def get_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, pool_pre_ping=True)


def fetch_recent_rows(lookback_minutes: int, limit_rows: int, fault_filter_list=None) -> pd.DataFrame:
    """Fetch recent data from database with optional fault filtering"""
    engine = get_engine()
   
    
    if fault_filter_list and len(fault_filter_list) > 0:
       
        placeholders = ",".join([f"'{ft}'" for ft in fault_filter_list])
        sql = f"""
        SELECT * FROM {TABLE} 
        WHERE ts >= NOW() - INTERVAL '{lookback_minutes} minutes' AND fault_type IN ({placeholders})
        ORDER BY ts DESC 
        LIMIT :limit
        """
    else:
        sql = f"""
        SELECT * FROM {TABLE} 
        WHERE ts >= NOW() - INTERVAL '{lookback_minutes} minutes'
        ORDER BY ts DESC 
        LIMIT :limit
        """
    
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params={"limit": limit_rows})
    
    
    df.columns = [c.lower() for c in df.columns]
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"])
    return df



def fault_label(code):
    mapping = {
        0: "No Fault (Normal Operation)",
        1: "Overheating Fault",
        2: "Leakage Fault",
        3: "Power Fluctuation Fault",
        "0": "No Fault (Normal Operation)",
        "1": "Overheating Fault",
        "2": "Leakage Fault",
        "3": "Power Fluctuation Fault",
        0.0: "No Fault (Normal Operation)",
        1.0: "Overheating Fault",
        2.0: "Leakage Fault",
        3.0: "Power Fluctuation Fault",
        None: "Unknown",
        "": "Unknown"
    }
   
    try:
        if isinstance(code, str) and code.strip() != "":
            fcode = float(code)
            if fcode in mapping:
                return mapping[fcode]
            icode = int(fcode)
            if icode in mapping:
                return mapping[icode]
        elif isinstance(code, float) and code in mapping:
            return mapping[code]
        elif isinstance(code, int) and code in mapping:
            return mapping[code]
    except Exception:
        pass
    return mapping.get(code, str(code) if code is not None else "Unknown")


# Sidebar controls
st.sidebar.header("Query Controls")
lookback = st.sidebar.slider("Lookback window (minutes)", min_value=1, max_value=24*60, value=DEFAULT_LOOKBACK_MIN)
limit = st.sidebar.number_input("Rows to fetch (max)", min_value=10, max_value=5000, value=1000, step=10)

# Sensor selection
sensor_options = ["temperature", "vibration", "pressure", "flow_rate", "current", "voltage"]
sensor = st.sidebar.selectbox("Primary sensor for analysis", options=sensor_options)

# Auto-refresh
col_auto1, col_auto2 = st.sidebar.columns(2)
auto_refresh = col_auto1.checkbox("Auto-refresh", value=False)
auto_refresh_seconds = col_auto2.number_input("Interval (sec)", min_value=1, max_value=60, value=5)

# Refresh button
refresh_manual = st.sidebar.button("Refresh Now", use_container_width=True)


# Attempt to fetch data
try:
    df_full = fetch_recent_rows(lookback, int(limit))
except Exception as e:
    st.error(f"Error querying DB: {e}")
    with st.expander("Debug Info"):
        st.write(f"DB Config: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    st.stop()

if df_full.empty:
    st.info("No data in database yet. Check that your simulator is running and inserting data.")
    with st.expander("Debug Info"):
        st.write(dict(DB_HOST=DB_HOST, DB_PORT=DB_PORT, DB_NAME=DB_NAME, TABLE=TABLE))
    st.stop()

# Real-time update indicator
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Map fault_type column to labels for display
df_full["fault_label"] = df_full["fault_type"].apply(fault_label)
df_full["fault_display"] = df_full.apply(lambda row: f"{row['fault_type']} - {row['fault_label']}", axis=1)

# Get fault types for filtering
fault_options = sorted(df_full["fault_label"].unique().tolist())
fault_filter = st.sidebar.multiselect("Filter Fault Type", options=fault_options, default=[])

# Apply local filtering
df = df_full.copy()
if fault_filter:
    df = df[df["fault_label"].isin(fault_filter)]

# Auto-refresh handling
if auto_refresh:
    time.sleep(auto_refresh_seconds)
    st.rerun()

if refresh_manual:
    st.rerun()



st.subheader("Latest Sensor Readings")
latest = df.sort_values("ts", ascending=False).iloc[0]

def fmt(v):
    return f"{v:.2f}" if pd.notna(v) else "N/A"

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric(" Temperature", fmt(latest.get("temperature")))
col2.metric(" Pressure", fmt(latest.get("pressure")))
col3.metric(" Vibration", fmt(latest.get("vibration")))
col4.metric(" Flow Rate", fmt(latest.get("flow_rate")))
col5.metric("Current", fmt(latest.get("current")))
col6.metric("Voltage", fmt(latest.get("voltage")))

# Alerts for abnormal values
alerts = []
if latest.get("temperature", 0) > 75:
    alerts.append("High temperature detected!")
if latest.get("vibration", 0) > 3:
    alerts.append("High vibration detected!")
if latest.get("pressure", 0) > 120:
    alerts.append("High pressure detected!")
if latest.get("fault_type", "") not in ("0", 0, 0.0, "", None):
    code = latest.get("fault_type", "?")
    label = fault_label(code)
    alerts.append(f"Fault detected: {code} ({label})")
elif latest.get("fault_type", "") in ("0", 0):
    code = latest.get("fault_type", "?")
    label = fault_label(code)
    
if alerts:
    for msg in alerts:
        st.error(f"🚨 {msg}")

# Fault distribution pie chart
st.subheader("Fault Type Distribution")
fault_counts = df["fault_type"].fillna("Unknown").value_counts().reset_index()
fault_counts.columns = ["fault_type", "count"]
fig_fault = px.pie(fault_counts, names="fault_type", values="count", 
                    title="Fault Type Distribution", hole=0.3)
st.plotly_chart(fig_fault, use_container_width=True)

# Time series for selected sensor
st.subheader(f"Time Series - {sensor.upper()} (with Trend)")
if sensor not in df.columns:
    st.warning(f"Sensor '{sensor}' not found in data.")
else:
    ts_df = df.sort_values("ts", ascending=True)[["ts", sensor]].dropna()
    if ts_df.empty:
        st.info(f"No data points for {sensor}")
    else:
      
        window = max(3, min(20, len(ts_df)//10))
        ts_df["trend"] = ts_df[sensor].rolling(window=window, min_periods=1).mean()
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=ts_df["ts"], y=ts_df[sensor], mode='lines+markers', name=sensor.capitalize()))
        fig_ts.add_trace(go.Scatter(x=ts_df["ts"], y=ts_df["trend"], mode='lines', name="Trend (MA)", line=dict(dash='dash', color='orange')))
        fig_ts.update_layout(title=f"{sensor.upper()} over time (with Trend)", hovermode='x unified', xaxis_title="Timestamp", yaxis_title=sensor.capitalize())
        st.plotly_chart(fig_ts, use_container_width=True)

# Multi-sensor comparison
st.subheader(" Multi-Sensor Comparison")
sensors_to_plot = ["temperature", "vibration", "pressure", "flow_rate"]
available_sensors = [s for s in sensors_to_plot if s in df.columns]

if available_sensors:
    ts_plot = df.sort_values("ts", ascending=True)[["ts"] + available_sensors].dropna()
    
    if not ts_plot.empty:
        fig_multi = go.Figure()
        for col in available_sensors:
            fig_multi.add_trace(go.Scatter(
                x=ts_plot["ts"],
                y=ts_plot[col],
                mode='lines',
                name=col.capitalize()
            ))
        fig_multi.update_layout(
            title="Multiple Sensor Trends",
            xaxis_title="Timestamp",
            yaxis_title="Value",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_multi, use_container_width=True)

# Fault type counts by sensor (correlation analysis)
st.subheader("Fault Analysis")
col_fault1, col_fault2 = st.columns(2)

with col_fault1:
    st.write("**Faults by Type**")
    fault_summary = df["fault_type"].value_counts()
    st.bar_chart(fault_summary)

with col_fault2:
    st.write("**Fault Type Details**")
    fault_detail = df.groupby("fault_type").agg({
        "temperature": "mean",
        "vibration": "mean",
        "pressure": "mean"
    }).round(2)
    st.dataframe(fault_detail, use_container_width=True)

# Data table
st.subheader("Recent Data (Latest 200 rows)")
display_df = df.sort_values("ts", ascending=False).head(200).copy()

for col in ["temperature", "vibration", "pressure", "flow_rate", "current", "voltage"]:
    if col in display_df.columns:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
st.dataframe(display_df, use_container_width=True, height=400)

# Download button
@st.cache_resource
def df_to_csv_bytes(df_in):
    return df_in.to_csv(index=False).encode('utf-8')

csv_data = df_to_csv_bytes(df.head(1000))
st.download_button("Download Data as CSV", 
                   data=csv_data, 
                   file_name=f"iiot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                   mime="text/csv", 
                   use_container_width=True)

# Debug info
with st.expander("Debug Info"):
    col_d1, col_d2 = st.columns(2)
    col_d1.write("**Database Config:**")
    col_d1.write(f"Host: {DB_HOST}:{DB_PORT}")
    col_d1.write(f"Database: {DB_NAME}")
    col_d1.write(f"Table: {TABLE}")
    col_d2.write("**Query Stats:**")
    col_d2.write(f"Rows fetched: {len(df)} / {len(df_full)}")
    col_d2.write(f"Lookback: {lookback} min")
    col_d2.write(f"Fault filter: {fault_filter if fault_filter else 'None'}")
