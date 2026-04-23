# Hackathon Template (Flask + Vue + PostgreSQL + Docker)

This template includes:
- **Backend:** Flask + raw SQL (`psycopg`)
- **Frontend:** Vue 3 + TypeScript + Pinia + Vite
- **Database:** PostgreSQL
- **Infrastructure:** Docker Compose
- **Sample feature:** end-to-end tasks/todos CRUD

## Quick start

```bash
docker compose up --build
```

Then open:
- Frontend: http://localhost:5173
- Backend health: http://localhost:5000/api/health
- Tasks API: http://localhost:5000/api/tasks

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   └── routes.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── postgres/
│   └── init/
│       └── 01-schema.sql
└── docker-compose.yml
```

## API routes

- `GET /api/health`
- `GET /api/tasks`
- `POST /api/tasks`
- `PATCH /api/tasks/:id`
- `DELETE /api/tasks/:id`
