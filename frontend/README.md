# Grocery Helper — Frontend

React + TypeScript single-page app for the Monthly Grocery Helper: browse, filter, add, and edit grocery items, and track price/seller comparisons month to month.

## Tech Stack

| Layer            | Technology                                  |
|-------------------|-----------------------------------------------|
| Framework         | [React](https://react.dev/) 19               |
| Language          | TypeScript                                   |
| Build tool        | [Vite](https://vite.dev/) 7 (SWC plugin for Fast Refresh) |
| UI components     | [MUI](https://mui.com/) (Material UI) + Emotion |
| Routing           | React Router 7                               |
| State management  | [Zustand](https://github.com/pmndrs/zustand) |
| HTTP client       | Axios                                        |
| Notifications     | react-toastify                               |
| Node version      | 25 (see `.node-version`)                     |

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── axiosInstance.ts          # configured Axios client (baseURL, interceptors)
│   │   ├── endpoints/
│   │   │   ├── AuthApi.ts
│   │   │   └── GroceryApi.ts
│   │   └── types/
│   │       ├── common.ts             # shared API types (errors, pagination, ...)
│   │       ├── requests/
│   │       │   ├── auth/UserLoginPayload.ts
│   │       │   └── grocery/          # Create/Update/BulkUpdate/Filter payloads
│   │       └── responses/            # response DTOs from the backend
│   ├── components/
│   │   ├── auth_components/          # UserLoginForm
│   │   ├── common/                   # shared UI primitives (buttons, fields, loader, ...)
│   │   └── grocery_components/       # list, detail, create/update forms, filter bar
│   ├── pages/                        # route-level views (Home, Login, Add/Detail/Update Grocery, About)
│   ├── store/                        # Zustand stores (auth, grocery)
│   ├── types/                        # app/domain-level types
│   ├── constants/                    # enums, API endpoint paths, route paths, utils
│   ├── styles/
│   ├── theme.ts                      # MUI theme
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── vite.config.ts
├── eslint.config.js
├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
├── Dockerfile
└── .env.sample
```

## Prerequisites

- [fnm](https://github.com/Schniz/fnm) (or any Node version manager) — Node 25
- npm (bundled with Node)
- The [backend API](../backend/README.md) running and reachable

## Getting Started

### 1. Set the Node version

```bash
cd frontend
fnm use    # reads .node-version
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment variables

Copy the sample file and point it at your backend:

```bash
cp .env.sample .env
```

| Variable              | Description                          | Example                  |
|------------------------|-----------------------------------------|----------------------------|
| `VITE_API_BASE_URL`   | Base URL of the backend API             | `http://localhost:8000`  |

### 4. Start the dev server

```bash
npm run dev
```

The app runs at `http://localhost:5173` by default.

## Available Scripts

| Command               | Description                                              |
|-------------------------|------------------------------------------------------------|
| `npm run dev`          | Start the Vite dev server (localhost only)                 |
| `npm run dev-public`   | Start the dev server bound to all interfaces on port 3000 (used by Docker) |
| `npm run build`        | Type-check (`tsc -b`) and produce a production build       |
| `npm run preview`      | Serve the production build locally                         |
| `npm run lint`         | Run ESLint over the project                                 |

## Running with Docker

From the repository root:

```bash
docker compose up frontend
```

This builds the frontend image and serves it on `http://localhost:3000`, reading configuration from `frontend/.env`. See the [root README](../README.md) for running the full stack together.

## Conventions

- **API layer** (`src/api/`): all HTTP calls go through `axiosInstance` and typed endpoint modules — never call `axios` directly from components.
- **Types**: request/response DTOs that mirror the backend contract live under `src/api/types/`; app-level/domain types live under `src/types/`.
- **State**: cross-cutting state (auth session, grocery list) lives in Zustand stores under `src/store/`; keep component-local state local.
- **Routes**: route paths are centralized in `src/constants/paths.ts`; API paths in `src/constants/apiEndpoints.ts` — avoid hardcoding either inline.
