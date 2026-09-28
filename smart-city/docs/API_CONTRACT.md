# API-контракт MVP

Этот файл фиксирует форматы, от которых зависят разные участники.

## Общие правила

- Все тела запросов и ответов используют JSON.
- Все идентификаторы - UUID в строковом виде.
- Дата и время - ISO 8601 в UTC, например `2026-09-27T12:00:00Z`.
- Защищённые endpoints получают `Authorization: Bearer <JWT>`.
- Ошибка имеет стандартный формат FastAPI: `{"detail": "Описание"}`.
- JWT содержит `sub` с UUID пользователя, `role` и `exp`.
- Допустимые роли: `USER`, `OPERATOR`, `ADMIN`.

## 1. Identity Service - порт 8001

### `POST /auth/register`

Запрос:

```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

Ответ `201`:

```json
{
  "id": "00000000-0000-0000-0000-000000000001",
  "email": "user@example.com",
  "first_name": "Иван",
  "last_name": "Иванов",
  "role": "USER",
  "is_active": true,
  "created_at": "2026-09-27T12:00:00Z"
}
```

Повторный email: `409`.

### `POST /auth/login`

Запрос:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Ответ `200`:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

Неверные данные: `401`.

### `GET /users/me`

Требует JWT. Возвращает полный публичный профиль текущего пользователя в том
же формате, что регистрация.

### `GET /users/{id}`

Публичный endpoint. Ответ `200`:

```json
{
  "id": "00000000-0000-0000-0000-000000000001",
  "first_name": "Иван",
  "last_name": "Иванов",
  "role": "USER"
}
```

Не найден: `404`.

### `GET /users`

Требует JWT. Возвращает массив публичных профилей.

## 2. Transport Service - порт 8002

### `GET /vehicles`

Ответ `200`:

```json
[
  {
    "id": "10000000-0000-0000-0000-000000000001",
    "type": "BUS",
    "route_number": "24",
    "latitude": 59.9343,
    "longitude": 30.3351,
    "status": "ACTIVE",
    "updated_at": "2026-09-27T12:00:00Z"
  }
]
```

### `GET /parking`

Ответ `200`:

```json
[
  {
    "id": "20000000-0000-0000-0000-000000000001",
    "name": "Центральная парковка",
    "address": "Невский проспект, 1",
    "latitude": 59.9343,
    "longitude": 30.3351,
    "total_spaces": 20,
    "available_spaces": 7
  }
]
```

### `POST /parking/{id}/reserve`

Требует JWT, тело не требуется. Ответ `201`:

```json
{
  "id": "30000000-0000-0000-0000-000000000001",
  "parking_id": "20000000-0000-0000-0000-000000000001",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "status": "ACTIVE",
  "created_at": "2026-09-27T12:00:00Z"
}
```

Парковка не найдена: `404`. Свободных мест нет: `409`.

## 3. Utility Service - порт 8003

### `POST /issues`

Требует JWT. Запрос:

```json
{
  "title": "Не работает фонарь",
  "description": "Фонарь не включается вечером",
  "category": "LIGHTING",
  "address": "Невский проспект, 10"
}
```

Ответ `201` содержит `id`, `user_id`, переданные поля, статус `NEW`,
`created_at` и `updated_at`.

### `GET /issues`

Требует JWT. Возвращает массив заявок. Пользователь видит свои заявки,
`OPERATOR` и `ADMIN` - все.

### `PUT /issues/{id}`

Требует роль `OPERATOR` или `ADMIN`.

```json
{
  "status": "IN_PROGRESS"
}
```

Ответ `200` - обновлённая заявка. Допустимые статусы: `NEW`, `IN_PROGRESS`,
`RESOLVED`, `REJECTED`.

## 4. Environment Service - порт 8004

### `GET /sensors`

Ответ `200`:

```json
[
  {
    "id": "40000000-0000-0000-0000-000000000001",
    "name": "Датчик температуры №1",
    "type": "TEMPERATURE",
    "unit": "°C",
    "latitude": 59.9343,
    "longitude": 30.3351,
    "status": "ACTIVE",
    "last_seen_at": "2026-09-27T12:00:00Z"
  }
]
```

### `GET /sensors/{id}/data`

Поддерживает необязательный query-параметр `limit`, по умолчанию 100.

```json
[
  {
    "id": "50000000-0000-0000-0000-000000000001",
    "sensor_id": "40000000-0000-0000-0000-000000000001",
    "value": 18.7,
    "measured_at": "2026-09-27T12:00:00Z",
    "received_at": "2026-09-27T12:00:01Z"
  }
]
```

### `POST /sensors/data`

Требует заголовок `X-Sensor-Key`.

```json
{
  "sensor_id": "40000000-0000-0000-0000-000000000001",
  "value": 18.7,
  "measured_at": "2026-09-27T12:00:00Z"
}
```

Ответ `201` - сохранённое показание. Неверный ключ: `401`, неизвестный датчик:
`404`, неактивный датчик: `400`.

## 5. Billing Service - порт 8005

### `GET /accounts/{userId}/invoices`

Требует JWT владельца либо администратора.

```json
[
  {
    "id": "60000000-0000-0000-0000-000000000001",
    "user_id": "00000000-0000-0000-0000-000000000001",
    "description": "Электроэнергия за сентябрь",
    "amount_cents": 245000,
    "status": "PENDING",
    "due_date": "2026-10-10",
    "paid_at": null,
    "created_at": "2026-09-27T12:00:00Z"
  }
]
```

Запрос чужих счетов обычным пользователем: `403`.

### `POST /payments`

Требует JWT.

```json
{
  "invoice_id": "60000000-0000-0000-0000-000000000001",
  "idempotency_key": "browser-generated-unique-key"
}
```

Ответ `201` при первом вызове и `200` при повторном ключе:

```json
{
  "id": "70000000-0000-0000-0000-000000000001",
  "invoice_id": "60000000-0000-0000-0000-000000000001",
  "amount_cents": 245000,
  "status": "CREATED",
  "idempotency_key": "browser-generated-unique-key",
  "created_at": "2026-09-27T12:00:00Z",
  "updated_at": "2026-09-27T12:00:00Z"
}
```

### `POST /payments/webhook/success`

Требует заголовок `X-Service-Token`.

```json
{
  "external_event_id": "provider-event-001",
  "payment_id": "70000000-0000-0000-0000-000000000001"
}
```

Ответ `200` - обновлённый платёж со статусом `SUCCEEDED`. Повтор события
возвращает тот же успешный результат и не изменяет данные повторно.

## 6. Notification Service - порт 8006

### `POST /notifications`

Внутренний endpoint, требует заголовок `X-Service-Token`.

```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "channel": "PUSH",
  "recipient": "00000000-0000-0000-0000-000000000001",
  "subject": "Статус изменён",
  "message": "Ваша заявка принята в работу"
}
```

Ответ `201`:

```json
{
  "id": "80000000-0000-0000-0000-000000000001",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "channel": "PUSH",
  "recipient": "00000000-0000-0000-0000-000000000001",
  "subject": "Статус изменён",
  "message": "Ваша заявка принята в работу",
  "status": "SENT",
  "created_at": "2026-09-27T12:00:00Z",
  "sent_at": "2026-09-27T12:00:00Z"
}
```

Неверный service token: `401`.
