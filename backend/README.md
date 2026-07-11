# Grocery Helper — Backend

FastAPI service that powers the Monthly Grocery Helper app: JWT authentication and a groceries API for tracking items, prices, sellers, and stock levels.

## Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Framework      | [FastAPI](https://fastapi.tiangolo.com/) 0.128 |
| Language       | Python 3.14                          |
| ORM            | SQLAlchemy 2.0 (async, via `asyncpg`) |
| Migrations     | Alembic                              |
| Validation     | Pydantic v2 / Pydantic Settings      |
| Auth           | JWT (PyJWT) + Argon2 password hashing |
| Server         | Uvicorn                              |
| Database       | PostgreSQL (Supabase, free tier)     |

## Architecture

The codebase follows a layered, feature-first structure — each feature owns its router, service, repository, and schemas:

```
HTTP request
   ↓
Router      (app/features/<feature>/router.py)   — HTTP concerns only: routes, status codes, DI
   ↓
Service     (app/features/<feature>/service.py)  — business logic
   ↓
Repository  (app/features/<feature>/repository.py) — database access
   ↓
Database
```

### Project structure

```
backend/
├── app/
│   ├── api/
│   │   └── router.py             # aggregates all feature routers under /api
│   ├── common/                   # cross-feature helpers
│   │   ├── constants.py
│   │   ├── enums.py
│   │   ├── filters.py
│   │   ├── pagination.py
│   │   └── responses.py
│   ├── core/
│   │   ├── config.py             # Settings (env-driven)
│   │   ├── database.py
│   │   ├── dependencies.py       # get_db, get_current_user
│   │   ├── exception_handlers.py
│   │   ├── exceptions.py
│   │   ├── log_config.py
│   │   ├── openapi_config.py
│   │   └── security.py           # OAuth2/JWT bearer scheme
│   ├── db/
│   │   ├── base.py               # declarative Base
│   │   ├── mixins.py             # shared model mixins (id, timestamps, ...)
│   │   └── session.py            # async engine/session factory
│   ├── features/
│   │   ├── auth/
│   │   │   ├── dependencies.py
│   │   │   ├── models.py         # User model
│   │   │   ├── repository.py
│   │   │   ├── router.py
│   │   │   ├── schemas/
│   │   │   └── service.py
│   │   └── grocery/
│   │       ├── dependencies.py
│   │       ├── filters.py        # query-param filter object
│   │       ├── models.py         # Grocery model
│   │       ├── repository.py
│   │       ├── router.py
│   │       ├── schemas/
│   │       └── service.py
│   ├── middleware/
│   │   └── request_logger.py
│   ├── utils/
│   │   ├── hashing.py
│   │   ├── jwt_helper.py
│   │   └── uuid_validation_helper.py
│   └── main.py                   # FastAPI app, middleware, exception handlers
├── migrations/                   # Alembic environment + versions
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── .env.sample
```

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) for Python version management
- Python 3.14 (see `.python-version`)
- A PostgreSQL database (a free [Supabase](https://supabase.com/) instance works well)

## Getting Started

### 1. Set the Python version

```bash
cd backend
pyenv install 3.14.6   # if not already installed
pyenv local 3.14.6
```

### 2. Create and activate a virtual environment

```bash
python -m venv .grocery-management-venv
source .grocery-management-venv/bin/activate   # Windows: .grocery-management-venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the sample file and fill in your own values:

```bash
cp .env.sample .env
```

| Variable                       | Description                                          | Default                         |
|---------------------------------|-------------------------------------------------------|----------------------------------|
| `DATABASE_URL`                  | PostgreSQL connection string                          | —                                |
| `SECRET_KEY`                    | Secret used to sign JWT access/refresh tokens          | —                                |
| `LOG_LEVEL`                     | Logging verbosity (`DEBUG`, `INFO`, ...)               | —                                |
| `ENVIRONMENT`                   | Deployment environment name (`development`, `production`) | —                            |
| `SHOW_SQL_LOG`                  | Log SQLAlchemy-generated SQL statements                | `False`                         |
| `ALLOW_ORIGINS`                 | JSON array of CORS-allowed origins                      | `["http://localhost:5173"]`     |

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the development server

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## Database Migrations

This project uses Alembic. Common commands:

```bash
# Generate a new migration from model changes
alembic revision --autogenerate -m "describe your change"

# Apply all pending migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1
```

## API Overview

All routes are mounted under the `/api` prefix. Interactive OpenAPI docs are available at `/docs`.

### Auth — `/api/auth`

| Method | Path             | Description                          | Auth required |
|--------|------------------|----------------------------------------|:--------------:|
| POST   | `/register`      | Create a new user account              | No             |
| POST   | `/login`         | Authenticate and receive access/refresh tokens | No      |
| POST   | `/token-refresh` | Exchange a refresh token for a new access token | No     |

Send the access token on subsequent requests as `Authorization: Bearer <access_token>`.

### Groceries — `/api/groceries`

| Method | Path                     | Description                                   | Auth required |
|--------|--------------------------|------------------------------------------------|:--------------:|
| GET    | `/`                      | List groceries (supports filtering, see below) | No            |
| GET    | `/{grocery_id}`          | Get a single grocery item's details             | No            |
| POST   | `/`                      | Create a grocery item                           | Yes           |
| PUT    | `/{grocery_id}`          | Update a grocery item                           | Yes           |
| DELETE | `/{grocery_id}`          | Delete a grocery item                           | Yes           |
| PATCH  | `/bulk/should-include`   | Bulk-update the `should_include` flag on multiple items | Yes  |

**List filters** (query parameters on `GET /`):

- `type` — `weight`, `sack`, `can`, `piece`, `packet`, `bottle`
- `current_seller` / `best_seller` — `meena`, `shwapno`, `local`, `comilla`, `default`, `agora`, `online`
- `category` — `toiletries`, `food`, `cookies`, `oil`, `other`
- `should_include` — `true` / `false`
- `search` — free-text search across item name/brand

## Running with Docker

From the repository root:

```bash
docker compose up backend
```

This builds the backend image and starts it on `http://localhost:8000`, reading configuration from `backend/.env`. See the [root README](../README.md) for running the full stack together.

## Code Style

- Keep routers thin — HTTP concerns only (status codes, request/response shapes, DI).
- Business logic belongs in the service layer; database access belongs in the repository layer.
- Feature-specific code stays inside its `app/features/<feature>/` folder; cross-feature helpers go in `app/common/`.
