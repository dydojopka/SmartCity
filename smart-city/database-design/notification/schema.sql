CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    recipient TEXT NOT NULL,
    channel TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'SENT', 'FAILED')),
    created_at DATETIME NOT NULL,
    sent_at DATETIME
);

CREATE INDEX ix_notifications_status ON notifications (status);
CREATE INDEX ix_notifications_created_at ON notifications (created_at DESC);