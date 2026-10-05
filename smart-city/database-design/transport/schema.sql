CREATE TABLE vehicles (
    id TEXT PRIMARY KEY,
    plate_number TEXT NOT NULL UNIQUE,
    model TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'AVAILABLE'
        CHECK (status IN ('AVAILABLE', 'IN_USE', 'MAINTENANCE')),
    created_at DATETIME NOT NULL
);

CREATE INDEX ix_vehicles_plate_number ON vehicles (plate_number);
CREATE INDEX ix_vehicles_status ON vehicles (status);

CREATE TABLE parkings (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    total_spaces INTEGER NOT NULL,
    available_spaces INTEGER NOT NULL,
    price_per_hour_cents INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CHECK (available_spaces >= 0),
    CHECK (available_spaces <= total_spaces)
);

CREATE INDEX ix_parkings_available_spaces ON parkings (available_spaces);

CREATE TABLE reservations (
    id TEXT PRIMARY KEY,
    parking_id TEXT NOT NULL REFERENCES parkings(id),
    user_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'CANCELLED', 'EXPIRED')),
    created_at DATETIME NOT NULL,
    expires_at DATETIME
);

CREATE INDEX ix_reservations_parking_id ON reservations (parking_id);
CREATE INDEX ix_reservations_user_id ON reservations (user_id);
CREATE INDEX ix_reservations_status ON reservations (status);