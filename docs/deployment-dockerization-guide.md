# Deployment & Dockerization Guide

## Overview

This guide ties Docker and Render deployment directly to your system design learning phases. Each milestone only adds what you have just learned — no premature complexity.

**Deployment platform**: Render (render.com)
**Container runtime**: Docker + Docker Compose
**Database**: Supabase (stays in cloud throughout all phases)

**Quick reference — Phase → Action**:

| Phase | Action |
|-------|--------|
| Before Phase 1 | Dockerize backend + frontend locally |
| End of Phase 2 | First Render deployment |
| Phase 4 (Caching) | Add Redis on Render |
| Phase 5 (Scaling) | Nginx locally; Render handles production scaling |
| Phase 6 (Microservices) | Split into multiple Render Web Services |
| Phase 7 (CDN) | Render Static Site serves via CDN automatically |

---

## Milestone 1: Dockerize the App

**When**: Before Phase 1 begins (do this right now — it takes 1 hour and pays dividends forever)
**Why now**: Containerize first so every phase you learn is tested in a consistent environment. No "works on my machine" surprises.

**What you have**: React frontend + FastAPI backend + Supabase (cloud)

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (Docker layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage — serve with Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # React Router — send all routes to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### .dockerignore files

`backend/.dockerignore`:
```
__pycache__
*.pyc
*.pyo
.env
.git
.venv
```

`frontend/.dockerignore`:
```
node_modules
dist
.env
.git
```

### Test locally

```bash
# Build images
docker build -t grocery-backend ./backend
docker build -t grocery-frontend ./frontend

# Run backend (pass env vars from your .env file)
docker run -p 8000:8000 --env-file backend/.env grocery-backend

# Run frontend
docker run -p 3000:80 grocery-frontend

# Verify: http://localhost:3000 and http://localhost:8000/docs
```

**Success criteria**: Both containers start without errors. API docs accessible at `/docs`.

---

## Milestone 2: First Render Deployment

**When**: End of Phase 2 — after REST API is standardized and Authentication is implemented
**Why now**: Never expose an unprotected API to the public internet. Auth is the minimum bar before going live.

**Pre-deployment checklist**:
- [ ] All secrets in environment variables, none hardcoded in source
- [ ] Supabase URL and key referenced via `os.getenv()` or similar
- [ ] Backend binds to `0.0.0.0` (not `127.0.0.1`)
- [ ] CORS configured to allow your production frontend URL
- [ ] JWT secret stored in environment variable

### Deploy Backend as a Web Service

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repository
4. Configure the service:

| Setting | Value |
|---------|-------|
| Name | `grocery-manager-api` |
| Root Directory | `backend` |
| Runtime | `Docker` (uses your Dockerfile) |
| Health Check Path | `/health` |

5. Add environment variables in Render dashboard:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
SECRET_KEY=your_random_jwt_secret_here
ALLOWED_ORIGINS=https://grocery-manager-frontend.onrender.com
```

6. Click **Deploy**

### Deploy Frontend as a Static Site

1. Render → **New → Static Site**
2. Connect your GitHub repository
3. Configure:

| Setting | Value |
|---------|-------|
| Name | `grocery-manager-frontend` |
| Root Directory | `frontend` |
| Build Command | `npm ci && npm run build` |
| Publish Directory | `dist` |

4. Add environment variables:

```
VITE_API_URL=https://grocery-manager-api.onrender.com
```

5. Click **Deploy**

**Result**: Your app is live at `https://grocery-manager-frontend.onrender.com`

**Free tier note**: Render free Web Services spin down after 15 minutes of inactivity. The first request after sleep takes ~30 seconds. This is fine for learning — upgrade when you reach Phase 5.

---

## Milestone 3: Docker Compose for Local Development

**When**: Phase 3–4 — when you add Redis for caching (Topic #19)
**Why now**: You now have multiple services (app + Redis) that need to work together. Docker Compose manages this cleanly.

Create `docker-compose.yml` at the project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./backend:/app        # Hot reload — code changes reflect immediately
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules     # Preserve container node_modules
    command: npm run dev

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"           # Expose for local debugging with Redis CLI
    volumes:
      - redis_data:/data      # Persist cache across restarts

volumes:
  redis_data:
```

Create `.env` at the project root (add to `.gitignore`):

```bash
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
SECRET_KEY=your_random_secret
```

**Usage**:

```bash
docker-compose up              # Start all services (foreground)
docker-compose up -d           # Start in background
docker-compose logs -f backend # Stream backend logs
docker-compose down            # Stop and remove containers
docker-compose down -v         # Also remove volumes (clears Redis cache)
```

**What you learn**: How multiple services discover each other by service name (`redis://redis:6379` — `redis` is the service name, not `localhost`). This is the same concept as microservice DNS discovery.

---

## Milestone 4: Add Redis to Render (Production)

**When**: Phase 4 — after implementing and testing caching locally with Docker Compose
**Why now**: Your caching layer is working locally. Now bring it to production.

### Create a Redis Instance on Render

1. Render → **New → Redis**
2. Configure:

| Setting | Value |
|---------|-------|
| Name | `grocery-manager-redis` |
| Plan | Free (25MB — sufficient through Phase 5) |
| Region | Same region as your Web Service |

3. Copy the **Internal Redis URL** (format: `redis://red-xxx:6379`)

### Update Backend Environment Variable on Render

In your `grocery-manager-api` service → **Environment**:

```
REDIS_URL=redis://red-your-instance-id.render.com:6379
```

Render will restart your service automatically. Your caching is now live in production.

**Internal vs External URL**: Use the Internal URL for service-to-service communication on Render (faster, no egress cost). Use the External URL only when connecting from outside Render (e.g., your local machine for debugging).

---

## Milestone 5: Nginx Locally for Scaling Practice

**When**: Phase 5 — when learning Load Balancers (Topic #13) and Proxy/Reverse Proxy (Topic #20)
**Why now**: Run multiple backend instances locally behind Nginx to understand load balancing hands-on.

Update `docker-compose.yml` to add Nginx and multiple backend instances:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend-1
      - backend-2

  backend-1:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - INSTANCE_ID=backend-1    # So you can see which server handled the request
    # No ports — traffic only comes through Nginx

  backend-2:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - INSTANCE_ID=backend-2

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

Create `nginx/nginx.conf`:

```nginx
upstream grocery_backend {
    least_conn;                     # Load balancing algorithm: fewest connections
    server backend-1:8000;
    server backend-2:8000;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://grocery_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_next_upstream error timeout http_500;    # Skip failed server
    }

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

**On Render (production)**: Render handles load balancing and reverse proxy automatically. To scale horizontally on Render:
- Web Service → **Settings → Scaling**
- Set **Min/Max Instances** (paid plan required for >1 instance)
- Render distributes traffic automatically

---

## Milestone 6: Microservices on Render

**When**: Phase 6 — after splitting the monolith into microservices (Topic #26)
**Why now**: Each independent service needs its own deployment lifecycle.

### Project structure after microservices split

```
grocery-management/
  services/
    api-gateway/        → Render Web Service (public)
    auth-service/       → Render Web Service (private)
    grocery-service/    → Render Web Service (private)
    notification-service/ → Render Web Service (private)
  frontend/             → Render Static Site
```

### Deploy each service to Render

For each service, create a separate **Web Service** on Render:

| Service | Public | Root Directory |
|---------|--------|---------------|
| api-gateway | Yes (port 80) | `services/api-gateway` |
| auth-service | No | `services/auth-service` |
| grocery-service | No | `services/grocery-service` |
| notification-service | No | `services/notification-service` |

### Service-to-service communication on Render

Use Render's **private service URLs** so internal traffic stays within Render's network (faster, no bandwidth cost):

```python
# In api-gateway, reference other services by their Render internal hostname
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
GROCERY_SERVICE_URL = os.getenv("GROCERY_SERVICE_URL", "http://grocery-service:8002")
```

Set these as environment variables on the api-gateway service in Render.

### Local Docker Compose for microservices

```yaml
version: '3.8'

services:
  api-gateway:
    build: ./services/api-gateway
    ports:
      - "8000:8000"
    environment:
      - AUTH_SERVICE_URL=http://auth-service:8001
      - GROCERY_SERVICE_URL=http://grocery-service:8002

  auth-service:
    build: ./services/auth-service
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}

  grocery-service:
    build: ./services/grocery-service
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379

  redis:
    image: redis:7-alpine

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "15672:15672"    # Management UI
```

---

## Milestone 7: CDN for Static Assets

**When**: Phase 7 — after learning CDN (Topic #23)
**Why now**: You now understand why CDN matters. Time to verify your Render setup uses it.

**Good news**: Render Static Sites are automatically served via Render's CDN. No extra configuration needed.

To verify CDN is working:
1. Open browser DevTools → Network tab
2. Load your frontend at `https://grocery-manager-frontend.onrender.com`
3. Check response headers — you should see `cf-cache-status` or `x-render-origin-server`

**Custom domain on Render** (optional, but good practice for learning DNS):
1. Buy a domain (Namecheap, Cloudflare)
2. Render → Static Site → **Settings → Custom Domain**
3. Add your domain and follow Render's DNS instructions (CNAME record)
4. Render provisions a free SSL certificate automatically

---

## Environment Variables — Complete Reference

Track all environment variables across phases:

### Backend

| Variable | Added In | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Milestone 1 | Supabase PostgreSQL connection string |
| `SUPABASE_URL` | Milestone 1 | Supabase project URL |
| `SUPABASE_KEY` | Milestone 1 | Supabase anon/service key |
| `ALLOWED_ORIGINS` | Milestone 2 | CORS: your frontend URL |
| `SECRET_KEY` | Milestone 2 | JWT signing secret (32+ random chars) |
| `REDIS_URL` | Milestone 4 | Redis connection URL |
| `INSTANCE_ID` | Milestone 5 | Which backend instance handled request |
| `AUTH_SERVICE_URL` | Milestone 6 | URL for auth microservice |
| `GROCERY_SERVICE_URL` | Milestone 6 | URL for grocery microservice |

### Frontend

| Variable | Added In | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Milestone 2 | Backend base URL |
| `VITE_WS_URL` | Milestone 6 | WebSocket URL for real-time updates |

---

## Render Free Tier — What You Get

| Resource | Free Tier | When to Upgrade |
|----------|-----------|-----------------|
| Web Service | 750 hrs/month, spins down after 15 min idle | Phase 5 (if load testing) |
| Static Site | 100GB bandwidth/month | Rarely needed |
| Redis | 25MB | Phase 6 if cache grows large |
| PostgreSQL | 1GB (use Supabase instead) | N/A |

**Recommendation**: Stay on free tier through Phase 5. Upgrade to the $7/month Web Service plan only when testing horizontal scaling (you need always-on instances to test load balancing properly).

---

## Debugging Deployments on Render

```bash
# View live logs from Render CLI (install: npm install -g @render-cli/cli)
render logs --service grocery-manager-api --tail

# Or check Render dashboard → your service → Logs tab
```

**Common issues**:

| Problem | Cause | Fix |
|---------|-------|-----|
| Build fails | Missing dependency in requirements.txt | `pip freeze > requirements.txt` locally first |
| App crashes on start | `HOST` env var not set | Ensure `--host 0.0.0.0` in start command |
| CORS errors | ALLOWED_ORIGINS not set | Add frontend URL to ALLOWED_ORIGINS env var |
| Can't reach Redis | Wrong Redis URL | Use Internal URL, not External URL |
| Health check fails | `/health` endpoint missing | Add health endpoint before deploying |

---

## Health Check Endpoint (Required Before Deploying)

Add this to your FastAPI backend before any Render deployment. Render uses it to know when your service is ready and to restart it if it crashes:

```python
# backend/app/main.py
from fastapi import FastAPI, HTTPException
from sqlalchemy import text

app = FastAPI()

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

Configure on Render:
- **Health Check Path**: `/health`
- **Health Check Timeout**: 30 seconds