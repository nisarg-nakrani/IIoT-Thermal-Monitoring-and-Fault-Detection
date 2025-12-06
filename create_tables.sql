
CREATE TABLE IF NOT EXISTS iiot_measurements (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    temperature DOUBLE PRECISION,
    vibration DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    flow_rate DOUBLE PRECISION,
    current DOUBLE PRECISION,
    voltage DOUBLE PRECISION,
    
    fft_temp_0 DOUBLE PRECISION, fft_vib_0 DOUBLE PRECISION, fft_pres_0 DOUBLE PRECISION,
    fft_temp_1 DOUBLE PRECISION, fft_vib_1 DOUBLE PRECISION, fft_pres_1 DOUBLE PRECISION,
    fft_temp_2 DOUBLE PRECISION, fft_vib_2 DOUBLE PRECISION, fft_pres_2 DOUBLE PRECISION,
    fft_temp_3 DOUBLE PRECISION, fft_vib_3 DOUBLE PRECISION, fft_pres_3 DOUBLE PRECISION,
    fft_temp_4 DOUBLE PRECISION, fft_vib_4 DOUBLE PRECISION, fft_pres_4 DOUBLE PRECISION,
    fft_temp_5 DOUBLE PRECISION, fft_vib_5 DOUBLE PRECISION, fft_pres_5 DOUBLE PRECISION,
    fft_temp_6 DOUBLE PRECISION, fft_vib_6 DOUBLE PRECISION, fft_pres_6 DOUBLE PRECISION,
    fft_temp_7 DOUBLE PRECISION, fft_vib_7 DOUBLE PRECISION, fft_pres_7 DOUBLE PRECISION,
    fft_temp_8 DOUBLE PRECISION, fft_vib_8 DOUBLE PRECISION, fft_pres_8 DOUBLE PRECISION,
    fft_temp_9 DOUBLE PRECISION, fft_vib_9 DOUBLE PRECISION, fft_pres_9 DOUBLE PRECISION,
    fault_type TEXT
);

-- helpful index for time-series queries
CREATE INDEX IF NOT EXISTS idx_iiot_measurements_ts ON iiot_measurements (ts DESC);
CREATE INDEX IF NOT EXISTS idx_iiot_measurements_fault ON iiot_measurements (fault_type);
