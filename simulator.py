# simulator.py
import time
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timezone


CSV_PATH = "dataset.csv"          # Path to your Kaggle dataset
EMIT_INTERVAL = 2.0               # Seconds between inserts
LOOP = True                       # Repeat dataset forever
BATCH_SIZE = 1                    # Insert one row at a time

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "IIOT_PROJECT"
DB_USER = "postgres"
DB_PASS = "1234"

TABLE = "iiot_measurements"

INSERT_SQL_TEMPLATE = f"""
INSERT INTO {TABLE} (
    ts, temperature, vibration, pressure, flow_rate, current, voltage,
    fft_temp_0, fft_vib_0, fft_pres_0,
    fft_temp_1, fft_vib_1, fft_pres_1,
    fft_temp_2, fft_vib_2, fft_pres_2,
    fft_temp_3, fft_vib_3, fft_pres_3,
    fft_temp_4, fft_vib_4, fft_pres_4,
    fft_temp_5, fft_vib_5, fft_pres_5,
    fft_temp_6, fft_vib_6, fft_pres_6,
    fft_temp_7, fft_vib_7, fft_pres_7,
    fft_temp_8, fft_vib_8, fft_pres_8,
    fft_temp_9, fft_vib_9, fft_pres_9,
    fault_type
) VALUES %s
"""


def make_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def row_tuple_from_series(s):
    ts = datetime.now(timezone.utc)  # Use real streaming timestamp

    def get(col):
        v = s.get(col)
        if pd.isna(v):
            return None
        try:
            return float(v)
        except:
            return v  

    # Build the tuple in column order
    return (
        ts,
        get("Temperature"), get("Vibration"), get("Pressure"), get("Flow_Rate"),
        get("Current"), get("Voltage"),

        get("FFT_Temp_0"), get("FFT_Vib_0"), get("FFT_Pres_0"),
        get("FFT_Temp_1"), get("FFT_Vib_1"), get("FFT_Pres_1"),
        get("FFT_Temp_2"), get("FFT_Vib_2"), get("FFT_Pres_2"),
        get("FFT_Temp_3"), get("FFT_Vib_3"), get("FFT_Pres_3"),
        get("FFT_Temp_4"), get("FFT_Vib_4"), get("FFT_Pres_4"),
        get("FFT_Temp_5"), get("FFT_Vib_5"), get("FFT_Pres_5"),
        get("FFT_Temp_6"), get("FFT_Vib_6"), get("FFT_Pres_6"),
        get("FFT_Temp_7"), get("FFT_Vib_7"), get("FFT_Pres_7"),
        get("FFT_Temp_8"), get("FFT_Vib_8"), get("FFT_Pres_8"),
        get("FFT_Temp_9"), get("FFT_Vib_9"), get("FFT_Pres_9"),

        get("Fault_Type")
    )


def main():
    
    df = pd.read_csv(CSV_PATH)
    rows = df.shape[0]

    conn = make_conn()
    cur = conn.cursor()

    print(f"Loaded {rows} rows. Starting simulation...")

    idx = 0

    while True:
        batch = []

        for _ in range(BATCH_SIZE):
            s = df.iloc[idx % rows]
            batch.append(row_tuple_from_series(s))
            idx += 1

        execute_values(cur, INSERT_SQL_TEMPLATE, batch)
        conn.commit()

        print(f"[{datetime.now().isoformat()}] Inserted {len(batch)} row(s)")

        time.sleep(EMIT_INTERVAL)

        if not LOOP and idx >= rows:
            print("Dataset completed — exiting.")
            break

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
