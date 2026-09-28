# daNYA

## Твоя зона ответственности

Ты реализуешь два сервиса c бизнес-логикой: Transport Service и
Billing Service.

Перед началом прочитай `../docs/API_CONTRACT.md`. Если формат неудобен или
неполон, сначала обсуди изменение с участником A.

## Задача 1. Transport Service

Рабочий каталог: `../services/transport-service/`.

Реализуй:

- `GET /vehicles`;
- `GET /parking`;
- `POST /parking/{id}/reserve`.

Требования:

1. Добавь модели `vehicles`, `parkings`, `reservations`.
2. Добавь несколько машин и две парковки через идемпотентный seed.
3. Для бронирования возьми `user_id` из JWT.
4. Уменьшай `available_spaces` атомарно в одной транзакции.
5. Если мест нет, возвращай `409 Conflict`.
6. После бронирования отправляй уведомление по HTTP.
7. Ошибка Notification не должна отменять сохранённую бронь.
8. Добавь тест успешной брони и тест парковки без мест.

## Задача 2. Billing Service

Рабочий каталог: `../services/billing-service/`.

Реализуй:

- `GET /accounts/{userId}/invoices`;
- `POST /payments`;
- `POST /payments/webhook/success`.

Требования:

1. Добавь модели `invoices`, `payments`, `webhook_events`.
2. Денежные суммы храни целым числом копеек в `amount_cents`.
3. Пользователь получает только собственные счета; администратор может получить
   любые.
4. Платёж можно создать только для неоплаченного собственного счёта.
5. Повторный `idempotency_key` возвращает существующий платёж.
6. Webhook защищён заголовком `X-Service-Token`.
7. Повторный `external_event_id` не обрабатывается второй раз.
8. Статусы платежа и счёта меняются в одной транзакции.
9. После успеха отправляется уведомление по HTTP.
10. Добавь тест повторного idempotency key и повторного webhook.

## Проектирование БД

Заполни:

- `../database-design/transport/schema.dbml`;
- `../database-design/transport/schema.sql`;
- `../database-design/transport/description.md`;
- `../database-design/billing/schema.dbml`;
- `../database-design/billing/schema.sql`;
- `../database-design/billing/description.md`.

Экспортируй две диаграммы в PNG или PDF.

## Готово, если

- все шесть обязательных endpoints работают по контракту;
- сервисы используют только собственные SQLite-файлы;
- транзакции не допускают отрицательного числа мест и повторной оплаты;
- ключевые операции логируются;
- тесты проходят;
- схемы БД соответствуют моделям.
