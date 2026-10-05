# Environment Service database

## `sensors`

Хранит датчики. `status` может быть `ACTIVE`, `INACTIVE`, `MAINTENANCE`.
`last_seen_at` обновляется при каждом новом показании.

## `sensor_readings`

Хранит показания датчиков. `sensor_id` ссылается на `sensors.id`.
`measured_at` — время измерения, `created_at` — время сохранения в БД.

## Связи

`one-to-many`: один датчик — много показаний.