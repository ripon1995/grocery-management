# 🛒 Monthly Grocery Helper

A full-stack application for tracking monthly groceries: item prices, sellers, stock levels, and shopping lists — with JWT-authenticated write access and a fast filterable UI.

## Project Structure

This is a monorepo with two independently runnable apps:

| Path         | Description                                                    | Docs                              |
|--------------|------------------------------------------------------------------|-------------------------------------|
| `/backend`   | FastAPI service exposing the auth and groceries API              | [backend/README.md](backend/README.md) |
| `/frontend`  | React + TypeScript SPA (Vite, MUI, Zustand)                      | [frontend/README.md](frontend/README.md) |

The database is PostgreSQL, hosted on [Supabase](https://supabase.com/) (free tier).

```
                ┌──────────────┐        HTTPS/JSON        ┌──────────────┐        SQL        ┌──────────────┐
                │   Frontend   │  ───────────────────────▶ │   Backend    │  ───────────────▶ │  PostgreSQL  │
                │  React + Vite│  ◀─────────────────────── │   FastAPI    │  ◀─────────────── │  (Supabase)  │
                └──────────────┘                            └──────────────┘                    └──────────────┘
```

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, JWT auth, Uvicorn — Python 3.14
- **Frontend:** React 19, TypeScript, Vite (SWC), MUI, Zustand, Axios, React Router — Node 25
- **Database:** PostgreSQL (Supabase)
- **Containers:** Docker + Docker Compose

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) — Python version management
- [fnm](https://github.com/Schniz/fnm) (or similar) — Node version management
- [Docker](https://www.docker.com/) — for the containerized workflow (optional but recommended)
- A PostgreSQL database (e.g. a free [Supabase](https://supabase.com/) project)

## Getting Started

You can run the stack either with Docker Compose (fastest way to get both services up) or by running each app natively.

### Option A — Docker Compose

1. Create `.env` files for each service from their samples and fill in your values:

   ```bash
   cp backend/.env.sample backend/.env
   cp frontend/.env.sample frontend/.env
   ```

2. Start both services:

   ```bash
   docker compose up
   ```

   - Backend: `http://localhost:8000` (docs at `/docs`)
   - Frontend: `http://localhost:3000`

### Option B — Run natively

Each app has its own setup guide with full details on environment variables, migrations, and available scripts:

**Backend**

```bash
cd backend
pyenv local 3.14.6
python -m venv .grocery-management-venv
source .grocery-management-venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env   # fill in DATABASE_URL, SECRET_KEY, etc.
alembic upgrade head
uvicorn app.main:app --reload
```

→ See [backend/README.md](backend/README.md) for the full API reference and environment variable table.

**Frontend**

```bash
cd frontend
fnm use
npm install
cp .env.sample .env   # point VITE_API_BASE_URL at the backend
npm run dev
```

→ See [frontend/README.md](frontend/README.md) for project structure and available scripts.

## Repository Conventions

- Each feature (backend) or domain area (frontend) is self-contained — see the respective READMEs for layering conventions (router → service → repository on the backend; api → store → components on the frontend).
- Environment configuration is per-app (`backend/.env`, `frontend/.env`); see each `.env.sample` for the required variables.
- Database schema changes go through Alembic migrations in `backend/migrations/`.
