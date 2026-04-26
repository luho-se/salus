# Salus

AI-assisted medical diagnostic analysis platform. Describe your symptoms, answer structured follow-up questions, and receive an explainable diagnosis powered by large language models and Shapley attribution (llmSHAP).

> **Disclaimer:** Salus is a research tool and does not constitute medical advice. Always consult a qualified healthcare professional for medical decisions.

## How it works

1. **Describe your symptoms** — enter a free-text description of what you are experiencing. The AI then extracts any structured information present in your description (location, duration, severity, etc.) and pre-fills those answers for you.

2. **Answer questions** — work through a set of follow-up questions generated specifically for your symptoms. Pre-filled answers are marked with an AI badge so you can review and correct them if needed.

3. *(Optional)* **Generate follow-up questions** — if you want a more thorough analysis, you can ask the AI to generate an additional round of targeted questions based on your answers so far. More questions generally improve diagnosis quality at the cost of additional computation time.

4. *(Optional)* **Add free-text context** — before starting the diagnosis you can add any extra context that did not fit the structured questions.

5. **Start diagnosis** — an LLM evaluates all your answers and produces a ranked list of possible conditions. Each condition includes a probability level (Low / Medium / High), a recommended care type (Self-care / See a professional / Emergency care), a motivation, and actionable recommendations. In parallel, llmSHAP computes Shapley attribution values to measure how much each individual answer contributed to the overall result.

6. **Review attribution** — after the diagnosis, a bar chart shows the relative influence of each answer, letting you see which information drove the result most.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, psycopg3 |
| AI | OpenAI GPT-4o-mini, llmSHAP |
| Frontend | Vue 3, TypeScript, Pinia, Vite, TailwindCSS 4, shadcn-vue |
| Database | PostgreSQL 16 |
| Infrastructure | Docker Compose |

## Quick start

Requires Docker and an OpenAI API key.

```bash
# 1. Create a .env file in the project root
echo "OPENAI_API_KEY=sk-..." > .env

# 2. Start the full stack
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:5000/api |

### Production build

```bash
docker compose -f compose.prod.yaml up --build
```

The production build serves the frontend via Nginx on port 80.

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── db.py                # psycopg3 connection pool
│   │   ├── routes/              # Flask blueprints
│   │   ├── services/            # Business logic & DB queries
│   │   │   └── resources/
│   │   │       └── ai_prompts/  # LLM system prompts
│   │   └── modules/
│   │       └── xai_module/      # llmSHAP wrapper
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   └── src/
│       ├── components/          # UI components (shadcn-vue + custom)
│       ├── stores/              # Pinia stores
│       ├── views/               # Page-level Vue components
│       ├── services/            # Axios API client
│       ├── types/               # Shared TypeScript interfaces
│       └── router/              # Vue Router config
├── postgres/
│   └── init/
│       └── 01-schema.sql        # Database schema
├── docker-compose.yml
└── compose.prod.yaml
```

## API overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create a project |
| GET | `/api/projects/:id` | Get project details |
| POST | `/api/projects/:id/generate_questions` | Generate questions from initial prompt |
| GET | `/api/questions/:projectId` | List questions |
| POST | `/api/answers/:projectId` | Save answers |
| GET | `/api/answers/:projectId` | Get answers |
| POST | `/api/questions/:projectId/follow_up` | Generate follow-up questions |
| POST | `/api/diagnosis/:projectId` | Start diagnosis (async) |
| GET | `/api/diagnosis/:id/status` | Poll diagnosis job status |
| GET | `/api/diagnosis/:id` | Get full diagnosis result |
| GET | `/api/diagnosis/list/:projectId/slim` | List diagnoses for a project |

## Environment variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Required. Used by GPT-4o-mini and llmSHAP. |
| `DATABASE_URL` | PostgreSQL connection string. Set automatically by Docker Compose. |

## Origin

Salus was created for the [WASP Lighthouse Hackathon 2026](https://wasp-sweden.org) held in Umeå, Sweden.
