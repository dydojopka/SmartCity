# Transport Service database

## `vehicles`

Список транспортных средств с текущими координатами. Используется публичным
endpoint `GET /vehicles`.

| Поле | Назначение |
|---|---|
| `id` | первичный ключ UUID |
| `plate_number` | государственный номер, уникальный |
| `model` | модель транспорта |
| `latitude`, `longitude` | координаты |
| `status` | `AVAILABLE`, `IN_USE`, `MAINTENANCE` |
| `created_at` | дата создания в UTC |

## `parkings`

Парковочные зоны. `available_spaces` уменьшается атомарно в одной транзакции
при бронировании.

| Поле | Назначение |
|---|---|
| `id` | первичный ключ UUID |
| `name`, `address` | название и адрес |
| `latitude`, `longitude` | координаты |
| `total_spaces` | всего мест |
| `available_spaces` | свободных мест, не может стать отрицательным |
| `price_per_hour_cents` | цена в копейках за час |
| `created_at`, `updated_at` | служебные даты в UTC |

Ограничения: `available_spaces >= 0` и `available_spaces <= total_spaces`.

## `reservations`

Бронирования парковок. `user_id` — UUID пользователя из Identity Service;
внешнего ключа на Identity DB нет, связь только через JWT.

| Поле | Назначение |
|---|---|
| `id` | первичный ключ UUID |
| `parking_id` | ссылка на `parkings.id` |
| `user_id` | UUID пользователя из Identity Service |
| `status` | `ACTIVE`, `CANCELLED`, `EXPIRED` |
| `created_at` | дата создания в UTC |
| `expires_at` | срок действия брони |

Индексы по `parking_id`, `user_id`, `status` поддерживают выдачу активных броней.