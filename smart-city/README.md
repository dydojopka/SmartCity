# Smart City

Учебная экосистема из шести независимых микросервисов. Полное описание
архитектуры и распределение работ находятся в `../PLAN.md`.

## Состояние проекта

Создан технический каркас:

- шесть FastAPI-приложений с `GET /health`;
- отдельный SQLite volume для каждого сервиса;
- Docker Compose;
- React/Vite frontend;
- зафиксированный API-контракт;
- отдельные задания для трёх участников.

Identity и Utility Service реализованы. Transport, Billing, Environment и
Notification пока содержат только технический каркас.

## Быстрый запуск

```bash
cp .env.example .env
docker compose up --build
```

Frontend: <http://localhost:5173>

Swagger сервисов:

- Identity: <http://localhost:8001/docs>
- Transport: <http://localhost:8002/docs>
- Utility: <http://localhost:8003/docs>
- Environment: <http://localhost:8004/docs>
- Billing: <http://localhost:8005/docs>
- Notification: <http://localhost:8006/docs>

Проверка состояния выполняется по пути `/health` на соответствующем порту.

## Тестовые учётные записи

Все тестовые учётные записи создаются при первом старте Identity Service. Пароль
для всех: `demo12345`.

| Роль | Email | UUID |
|---|---|---|
| Пользователь | `user@smartcity.local` | `00000000-0000-0000-0000-000000000001` |
| Оператор | `operator@smartcity.local` | `00000000-0000-0000-0000-000000000002` |
| Администратор | `admin@smartcity.local` | `00000000-0000-0000-0000-000000000003` |

## Проверка сервисов

```bash
for p in 8001 8002 8003 8004 8005 8006; do
  curl --fail "http://localhost:$p/health"
done
```

Тесты backend запускаются отдельно для каждого сервиса:

```bash
cd services/identity-service
python -m pip install -r requirements.txt
pytest -q
```

Для frontend:

```bash
cd frontend
npm ci
npm run build
```

## Командная работа

- `tasks/zheNYA.md` — Identity, Utility, инфраструктура и интеграция;
- `tasks/daNYA.md` — Transport и Billing;
- `tasks/vaNYA.md` — Environment, Notification и предметный frontend.

Перед началом разработки все участники должны прочитать
`docs/API_CONTRACT.md`.
