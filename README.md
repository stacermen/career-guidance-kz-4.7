# Career Guidance KZ — AI-powered psychological career counselling

Production-ready full-stack web application that runs Kazakhstan high-school /
university applicants through five validated psychometric tests
(Holland Code, Big Five, Multiple Intelligences, Work Values, Cognitive Style),
analyses the combined profile with a **free open AI model via
[Pollinations.ai](https://pollinations.ai)** (OpenAI-compatible, no API key
required — currently `gpt-oss-20b` on the anonymous tier), and recommends
concrete university specializations from a seeded catalogue of real Kazakhstan
universities and `государственный классификатор специальностей РК` codes.

The entire UI is in Russian.

## Stack

| Layer       | Tech                                                                 |
|-------------|----------------------------------------------------------------------|
| Frontend    | React 18 · Vite · TypeScript · Tailwind · shadcn-style primitives · Framer Motion · React Router v6 · Zustand · Axios · Recharts · @dnd-kit |
| Backend     | Python 3.11 · FastAPI · SQLAlchemy 2.0 async · asyncpg · Alembic · Pydantic v2 · httpx (Pollinations.ai) · ReportLab |
| Database    | PostgreSQL 15                                                        |
| Infra       | Docker · docker-compose · Nginx reverse proxy                        |

## Quick start (Docker)

```bash
cp .env.example .env
# No API keys required — Pollinations.ai is free and anonymous.
# All defaults work out-of-the-box.
docker compose up --build
```

Open <http://localhost> — Nginx serves the SPA on `/` and proxies `/api` to the
FastAPI backend. Postgres data is persisted in the named volume `postgres_data`.

The backend container automatically runs `alembic upgrade head` and seeds the
database (universities, specializations, all five tests with ~142 questions)
on startup. Re-running is idempotent.

The seed produces:

- **40+** real Kazakhstan universities across all major cities (Алматы, Астана, Шымкент, Қарағанды, Павлодар, Ақтөбе, Ақтау, Орал, Көкшетау, Семей, Өскемен, Тараз, Қызылорда, Атырау, Петропавл)
- **100+** specialization placements categorised across IT, Engineering, Medicine, Economics, Law, Pedagogy, Arts
- **5** psychometric modules with **142** validated questions (Holland 42 · Big Five 30 · MI 40 · Values 20 · Cognitive 10)

## Local development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
# Postgres expected on localhost:5432 — easiest is `docker compose up postgres`
export DATABASE_URL="postgresql+asyncpg://career:career@localhost:5432/careerdb"
# No AI credentials needed — Pollinations.ai is free.
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## Tests

```bash
cd backend && pytest -q
cd frontend && npm run lint && npm run typecheck
```

## API

| Method | Path                         | Purpose                                      |
|--------|------------------------------|----------------------------------------------|
| POST   | `/api/session`               | create anonymous session, returns `session_id` |
| POST   | `/api/answers`               | persist a batch of answers for a session     |
| POST   | `/api/analyze`               | trigger full AI analysis & matching          |
| GET    | `/api/results/{session_id}`  | fetch saved analysis + recommendations       |
| GET    | `/api/results/{session_id}/pdf` | downloadable PDF summary                  |
| GET    | `/api/universities`          | list universities (filters: `city`)          |
| GET    | `/api/specializations`       | list specializations (filters: `city`, `category`, `university_id`) |
| POST   | `/api/chat`                  | streaming SSE chat with AI career counsellor |
| GET    | `/api/health`                | liveness probe                               |
| GET    | `/api/tests`                 | list test modules + questions                |

## Project layout

```
.
├── backend/                    FastAPI service
│   ├── app/
│   │   ├── api/routes/         endpoint modules (sessions, answers, …)
│   │   ├── core/               config & logging
│   │   ├── db/                 SQLAlchemy session, seed_data
│   │   ├── models/             ORM models
│   │   ├── schemas/            Pydantic v2 schemas
│   │   └── services/           ai_service, scoring_service, recommendation_service, pdf_service
│   ├── alembic/                migrations
│   └── tests/                  pytest suite (scoring algorithms)
├── frontend/                   React + Vite SPA
│   └── src/
│       ├── api/                axios client + endpoint helpers
│       ├── components/         shared UI + charts
│       ├── hooks/              useSession, useTestFlow, useResults
│       ├── pages/              Landing, Onboarding, Test, Loading, Results, Universities, About
│       ├── stores/             Zustand testStore (with localStorage persistence)
│       └── utils/              client-side scoring helpers (mirrors backend)
├── docker-compose.yml
├── nginx.conf
└── README.md
```
