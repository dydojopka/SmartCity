# Billing Service database

## `invoices`

Счета пользователей. `user_id` — UUID из Identity Service, внешнего ключа нет.

| Поле | Назначение |
|---|---|
| `id` | первичный ключ UUID |
| `user_id` | UUID пользователя из Identity Service |
| `amount_cents` | сумма в копейках, всегда > 0 |
| `status` | `UNPAID`, `PAID`, `CANCELLED` |
| `description`, `due_date` | описание и срок оплаты |
| `created_at`, `updated_at` | служебные даты в UTC |

## `payments`

Платежи по счетам.

| Поле | Назначение |
|---|---|
| `id` | первичный ключ UUID |
| `invoice_id` | ссылка на `invoices.id` |
| `user_id` | UUID пользователя |
| `amount_cents` | сумма в копейках, всегда > 0 |
| `status` | `PENDING`, `SUCCESS`, `FAILED` |
| `idempotency_key` | уникальный ключ идемпотентности |
| `external_event_id` | ID события от платёжного провайдера |
| `created_at`, `updated_at` | служебные даты в UTC |

Уникальные ограничения на `idempotency_key` и `external_event_id` обеспечивают
идемпотентность на уровне БД.

## `webhook_events`

Обработанные вебхуки платёжного провайдера. Уникальный `external_event_id`
гарантирует, что повторный вебхук не будет обработан второй раз.

| Поле | Назначение |
|---|---|
| `id` | первичный ключ UUID |
| `external_event_id` | уникальный идентификатор события |
| `event_type` | тип события |
| `payload` | JSON с телом вебхука |
| `processed_at` | дата обработки в UTC |

Платёж и счёт обновляются в одной транзакции, поэтому статусы `payments.status`
и `invoices.status` всегда согласованы.