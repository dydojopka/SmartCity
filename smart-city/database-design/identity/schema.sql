CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'USER'
        CHECK (role IN ('USER', 'OPERATOR', 'ADMIN')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL
);

CREATE INDEX ix_users_email ON users (email);
