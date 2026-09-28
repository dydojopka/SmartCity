# Utility Service database

## `issues`

Хранит заявки ЖКХ. Таблица принадлежит только Utility Service. Поле `user_id`
содержит UUID пользователя из Identity Service, но внешнего ключа на Identity
DB нет: связь между сервисами выполняется только через HTTP и JWT.

| Поле | Назначение |
|---|---|
| `id` | первичный ключ UUID заявки |
| `user_id` | автор заявки |
| `title`, `description` | описание проблемы |
| `category` | категория заявки |
| `address` | адрес проблемы |
| `status` | `NEW`, `IN_PROGRESS`, `RESOLVED`, `REJECTED` |
| `created_at`, `updated_at` | время создания и последнего изменения в UTC |

Индексы по `user_id`, `category` и `status` поддерживают выдачу заявок и
будущие фильтры.
