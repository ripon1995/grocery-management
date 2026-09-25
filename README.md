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


## Project Tree

```text
grocery-management/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── .gitignore
├── backend/
│   ├── .env.sample
│   ├── .python-version
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   └── router.py
│   │   ├── clients/
│   │   │   └── redis_client.py
│   │   ├── common/
│   │   │   ├── constants.py
│   │   │   ├── enums.py
│   │   │   ├── filters.py
│   │   │   ├── pagination.py
│   │   │   └── responses.py
│   │   ├── core/
│   │   │   ├── api_response_schema.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── exception_handlers.py
│   │   │   ├── exceptions.py
│   │   │   ├── log_config.py
│   │   │   ├── openapi_config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── mixins.py
│   │   │   └── session.py
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── models.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── routers/
│   │   │   │   │   └── v1/
│   │   │   │   │       └── router.py
│   │   │   │   ├── schemas/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth_request_schemas.py
│   │   │   │   │   └── auth_response_schemas.py
│   │   │   │   └── service.py
│   │   │   └── grocery/
│   │   │       ├── __init__.py
│   │   │       ├── dependencies.py
│   │   │       ├── filters.py
│   │   │       ├── models.py
│   │   │       ├── repository.py
│   │   │       ├── routers/
│   │   │       │   └── v1/
│   │   │       │       └── router.py
│   │   │       ├── schemas/
│   │   │       │   ├── request_schemas.py
│   │   │       │   └── response_schemas.py
│   │   │       └── service.py
│   │   ├── main.py
│   │   ├── middleware/
│   │   │   ├── latency_header.py
│   │   │   └── request_logger.py
│   │   ├── services/
│   │   │   └── redis_service.py
│   │   └── utils/
│   │       ├── hashing.py
│   │       ├── jwt_helper.py
│   │       ├── redis_key_helper.py
│   │       └── uuid_validation_helper.py
│   ├── Dockerfile
│   ├── migrations/
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 03bba699f6d6_password_length_increased_to_255.py
│   │       ├── 41ab5277874e_add_indexes_to_grocery_category_seller_.py
│   │       ├── 5dc40e0c9376_add_category_column_to_grocery.py
│   │       ├── 72f31d406fa2_initial_fresh_start_clean_db.py
│   │       ├── 7f3834dfb197_add_online_value_to_seller_enum.py
│   │       ├── 85ef98a7301c_add_index_on_grocery_type_column.py
│   │       ├── 9212f2069cff_user_model_created.py
│   │       └── ff8c6088c88e_password_length_increased.py
│   ├── README.md
│   └── requirements.txt
├── docker-compose.yml
├── docs/
│   ├── improvements/
│   │   ├── day-3-day-4-typescript-improvements.md
│   │   ├── day-5-day-6-improvements.md
│   │   ├── day-7-improvements.md
│   │   ├── phase-4-caching-improvements.md
│   │   └── README.md
│   ├── project-goals/
│   │   ├── deployment-dockerization-guide.md
│   │   ├── goals.md
│   │   └── system-design-learning-roadmap.md
│   ├── project-staff/
│   │   ├── phase-2-apis.md
│   │   ├── phase-3-databases-sql-review.md
│   │   └── phase-4-caching-review.md
│   └── release-docs/
│       ├── aws-release/
│       │   ├── backend-release-guide.md
│       │   └── frontend-release-guide.md
│       ├── deploy-helper-aws-docker-compose.md
│       ├── deploy-helper-ec2-github-actions.md
│       └── docker-setup/
│           ├── backend-docker-setup.md
│           ├── basic-docker-commands.md
│           └── frontend-docker-setup.md
├── frontend/
│   ├── .env.sample
│   ├── .gitignore
│   ├── .node-version
│   ├── Dockerfile
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── public/
│   │   └── trolley.png
│   ├── README.md
│   ├── src/
│   │   ├── api/
│   │   │   ├── axiosInstance.ts
│   │   │   ├── endpoints/
│   │   │   │   ├── AuthApi.ts
│   │   │   │   └── GroceryApi.ts
│   │   │   ├── exceptions/
│   │   │   │   ├── baseExceptions.ts
│   │   │   │   ├── customException.ts
│   │   │   │   ├── exceptionFactory.ts
│   │   │   │   ├── handleAuthStoreExceptions.ts
│   │   │   │   └── handleGroceryStoreExceptions.ts
│   │   │   └── types/
│   │   │       ├── index.ts
│   │   │       ├── requests/
│   │   │       │   ├── auth/
│   │   │       │   │   └── UserLoginPayload.ts
│   │   │       │   └── grocery/
│   │   │       │       ├── BulkUpdateGroceryItem.ts
│   │   │       │       ├── CreateGroceryItem.ts
│   │   │       │       ├── GroceryFilterParams.ts
│   │   │       │       └── UpdateGroceryItem.ts
│   │   │       └── responses/
│   │   │           ├── GroceryDetailResponse.ts
│   │   │           ├── GroceryListResponse.ts
│   │   │           └── UserLoginResponse.ts
│   │   ├── App.css
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── auth_components/
│   │   │   │   └── UserLoginForm.tsx
│   │   │   ├── common/
│   │   │   │   ├── AppToast.tsx
│   │   │   │   ├── MonthlyGroceryAppBar.tsx
│   │   │   │   ├── MonthlyGroceryAppButton.tsx
│   │   │   │   ├── MonthlyGroceryAppDiplayField.tsx
│   │   │   │   ├── MonthlyGroceryAppError.tsx
│   │   │   │   ├── MonthlyGroceryAppInputField.tsx
│   │   │   │   ├── MonthlyGroceryAppInputFieldSmall.tsx
│   │   │   │   ├── MonthlyGroceryAppLoader.tsx
│   │   │   │   ├── MonthlyGroceryAppSelectField.tsx
│   │   │   │   └── MonthlyGroceryAppSelectFieldSmall.tsx
│   │   │   └── grocery_components/
│   │   │       ├── CreateGroceryForm.tsx
│   │   │       ├── GroceryDetail.tsx
│   │   │       ├── GroceryFilterBar.tsx
│   │   │       ├── GroceryList.tsx
│   │   │       └── GroceryUpdateForm.tsx
│   │   ├── constants/
│   │   │   ├── apiEndpoints.ts
│   │   │   ├── enums.ts
│   │   │   ├── errorCodes.ts
│   │   │   ├── paths.ts
│   │   │   └── utils.ts
│   │   ├── main.tsx
│   │   ├── pages/
│   │   │   ├── AboutPage.tsx
│   │   │   ├── AddGroceryPage.tsx
│   │   │   ├── DetailGroceryPage.tsx
│   │   │   ├── HomePage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   └── UpdateGroceryPage.tsx
│   │   ├── store/
│   │   │   ├── useAuthStore.ts
│   │   │   └── useGroceryStore.ts
│   │   ├── styles/
│   │   │   └── GroceryList.css
│   │   ├── theme.ts
│   │   ├── types/
│   │   │   ├── IApiResponse.ts
│   │   │   ├── IGroceryDetail.ts
│   │   │   └── IGroceryList.ts
│   │   └── utility/
│   │       └── logger.ts
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── grocery-management-redis.yml
└── README.md

```