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

Предметные endpoints из задания пока не реализованы.

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

## Командная работа

- `tasks/zheNYA.md` — Identity, Utility, инфраструктура и интеграция;
- `tasks/daNYA.md` — Transport и Billing;
- `tasks/vaNYA.md` — Environment, Notification и предметный frontend.

Перед началом разработки все участники должны прочитать
`docs/API_CONTRACT.md`.
