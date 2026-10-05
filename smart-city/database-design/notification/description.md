# Notification Service database

## `notifications`

Хранит уведомления. При создании статус `PENDING`, после имитации отправки —
`SENT`. `sent_at` заполняется при успешной отправке.

Поля:

- `id` — первичный ключ;
- `user_id` — UUID пользователя, если есть;
- `recipient` — получатель;
- `channel` — канал: EMAIL, PUSH, SMS;
- `subject` — тема;
- `message` — текст;
- `status` — PENDING, SENT, FAILED;
- `created_at` — время создания;
- `sent_at` — время отправки.