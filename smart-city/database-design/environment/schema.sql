CREATE TABLE sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')),
    last_seen_at DATETIME,
    created_at DATETIME NOT NULL
);

CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    value NUMERIC NOT NULL,
    unit TEXT,
    measured_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE INDEX ix_sensor_readings_sensor_id_measured_at
    ON sensor_readings (sensor_id, measured_at DESC);