CREATE TABLE invoices (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    status TEXT NOT NULL DEFAULT 'UNPAID'
        CHECK (status IN ('UNPAID', 'PAID', 'CANCELLED')),
    description TEXT,
    due_date DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_invoices_user_id ON invoices (user_id);
CREATE INDEX ix_invoices_status ON invoices (status);

CREATE TABLE payments (
    id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES invoices(id),
    user_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED')),
    idempotency_key TEXT NOT NULL UNIQUE,
    external_event_id TEXT UNIQUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_payments_invoice_id ON payments (invoice_id);
CREATE INDEX ix_payments_user_id ON payments (user_id);
CREATE INDEX ix_payments_status ON payments (status);
CREATE UNIQUE INDEX ix_payments_idempotency_key ON payments (idempotency_key);
CREATE UNIQUE INDEX ix_payments_external_event_id ON payments (external_event_id);

CREATE TABLE webhook_events (
    id TEXT PRIMARY KEY,
    external_event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    processed_at DATETIME NOT NULL
);

CREATE UNIQUE INDEX ix_webhook_events_external_event_id ON webhook_events (external_event_id);