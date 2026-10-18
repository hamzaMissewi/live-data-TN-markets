# Backend Setup — Tunisia Markets Hub (FastAPI)

This document covers how to install, configure, and run the FastAPI backend described in `README.md`.

## Architecture (from README.md)

```
 Data sources ──► Ingestion (Python/Celery) ──► PostgreSQL + TimescaleDB + Redis ──► API (FastAPI)
 (BVMT, BCT, FX APIs, news)                 validate + normalize                              │
                                                                                               ▼
                                                                                        Next.js frontend + Cloudflare CDN
```

**Layers:**
1. **Ingestion:** scrapers + API clients (Celery cron jobs)
2. **Storage:** PostgreSQL 16 + TimescaleDB extension (time series), Redis (cache + Celery broker)
3. **Analytics:** pandas z-score anomaly detection pipeline
4. **API:** FastAPI read-only JSON endpoints (`/api/v1/companies`, `/api/v1/prices`, `/api/v1/fx`, `/api/v1/news`, `/api/v1/anomalies`, `/api/v1/commodities`)
5. **Frontend:** Next.js App Router with ISR

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| Docker & Docker Compose | latest | PostgreSQL + TimescaleDB + Redis |
| pip | latest | Python package manager |

## 1. Navigate to the Project

```bash
cd e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense
```

## 2. Start Infrastructure (PostgreSQL + Redis)

The backend requires a running TimescaleDB (PostgreSQL) and Redis instance. Use Docker Compose:

```bash
docker-compose up -d postgres redis
```

Verify the containers are running:

```bash
docker-compose ps
```

Expected output:

```
NAME                              IMAGE                        STATUS
tunisia-markets-postgres          timescale/timescaledb:latest-pg16   Up (healthy)
tunisia-markets-redis             redis:7-alpine                          Up (healthy)
```

Ports exposed:
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## 3. Configure Environment

Copy the example environment file and adjust as needed:

```bash
cd backend
copy .env.example .env
```

Key settings in `.env`:

```ini
# Database (must match docker-compose values)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tunisia_markets
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=tunisia_markets

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
ENVIRONMENT=development

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

> **Note:** `ADSENSE_CLIENT_ID`, `ADSENSE_SLOT_CHART`, `ADSENSE_SLOT_SIDEBAR`, `ADSENSE_SLOT_IN_CONTENT` are optional for local development.

## 4. Install Python Dependencies

Create and activate a virtual environment (recommended):

```bash
# Create venv
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (macOS / Linux)
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Core packages installed:
- `fastapi==0.115.0` — web framework
- `uvicorn[standard]==0.32.0` — ASGI server
- `sqlalchemy==2.0.36` + `asyncpg==0.29.0` — async PostgreSQL driver
- `alembic==1.13.2` — database migrations
- `timescaledb==0.2.0` — TimescaleDB extension support
- `redis==5.2.0` + `celery==5.4.0` — task queue + broker
- `pandas==2.2.3` + `numpy==2.1.3` + `scikit-learn==1.5.2` — analytics
- `httpx==0.27.2` + `beautifulsoup4==4.12.3` — scraping
- `pydantic==2.9.2` + `pydantic-settings==2.5.2` — validation + config

## 5. Initialize the Database

The backend auto-creates tables on startup via SQLAlchemy `Base.metadata.create_all`. No manual migration is required for first run:

```bash
# Tables are created automatically when the API starts
```

If you need to reset the database:

```bash
docker-compose down -v   # removes postgres data volume
docker-compose up -d postgres redis
```

## 6. Run the Backend API

### Option A: Direct (development)

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B: Docker

```bash
docker-compose up -d api
```

## 7. Verify the API is Running

Health check:

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok","version":"1.0.0"}`

API documentation (when `ENVIRONMENT != "production"`):

```bash
open http://localhost:8000/docs
```

### Test Key Endpoints

```bash
# List sectors
curl http://localhost:8000/api/v1/sectors

# List companies
curl http://localhost:8000/api/v1/companies

# Latest prices
curl http://localhost:8000/api/v1/prices/latest

# FX rates
curl http://localhost:8000/api/v1/fx/rates

# Commodity prices
curl http://localhost:8000/api/v1/commodities/prices

# Latest news
curl http://localhost:8000/api/v1/news

# Anomalies
curl http://localhost:8000/api/v1/anomalies
```

> **Note:** Database-dependent endpoints (`/sectors`, `/companies`, etc.) return `500` until PostgreSQL is running and contains seed data.

## 7b. Run Workers (Celery) — Optional

For ingestion and anomaly detection jobs:

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
```

## 8. Project Structure (Backend)

```
backend/
├── main.py                  # FastAPI entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container definition
├── .env                     # Environment variables (local)
├── .env.example             # Template
├── app/
│   ├── main.py              # FastAPI app factory + middleware
│   ├── core/
│   │   └── config.py        # Pydantic settings
│   ├── api/
│   │   ├── __init__.py      # Router export
│   │   └── v1/
│   │       ├── __init__.py  # API v1 router + sub-routers
│   │       ├── companies.py # /api/v1/companies
│   │       ├── prices.py    # /api/v1/prices
│   │       ├── fx.py        # /api/v1/fx
│   │       ├── news.py      # /api/v1/news (EN/FR/AR)
│   │       ├── anomalies.py # /api/v1/anomalies
│   │       ├── commodities.py # /api/v1/commodities
│   │       └── health.py    # /api/v1/health
│   ├── db/
│   │   └── session.py       # Async engine + session
│   ├── models/
│   │   ├── company.py       # Company, Sector
│   │   ├── price.py         # PriceDaily, PriceIntraday
│   │   ├── fx.py            # FXPair, FXRate
│   │   ├── anomaly.py       # Anomaly
│   │   ├── news.py          # NewsItem, NewsSource
│   │   └── commodity.py     # Commodity, CommodityPrice
│   ├── schemas/
│   │   ├── news.py          # NewsListResponse (locale-aware)
│   │   ├── company.py
│   │   ├── anomaly.py
│   │   ├── fx.py
│   │   ├── commodity.py
│   │   └── common.py        # Pagination
│   ├── scrapers/            # BVMT, BCT, FX scrapers
│   ├── workers/             # Celery tasks
│   ├── services/            # Business logic
│   ├── scripts/             # Ingestion scripts
│   └── tests/               # Pytest tests
├── db/
│   └── init.sql             # Database seed
└── docker/                  # Docker config
```

## 9. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'greenlet'` | Missing SQLAlchemy async dependency | `pip install greenlet asyncpg` |
| `ConstraintColumnNotFoundError: no column named 'date.desc()'` | SQLAlchemy Index bug | Fixed in code — `date.desc()` → `date` in Index definitions |
| `ImportError: cannot import name 'router'` | Wrong import in `app/api/__init__.py` | Fixed — imports `api_v1_router` |
| Endpoints return 500 | PostgreSQL not running | `docker-compose up -d postgres redis` |
| Port 8000 already in use | Another process on 8000 | Change `API_PORT` in `.env` |

## 10. Connect Frontend to Backend

The frontend (`frontend/`) calls the API at `http://localhost:8000/api/v1`. Ensure:

1. Backend is running on port 8000
2. `.env` has `FRONTEND_URL=http://localhost:3000` (CORS)
3. Frontend `.env` has `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`

Then start the frontend:

```bash
cd ../frontend
npm run dev
```

## Summary of Commands

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Configure
cd backend
copy .env.example .env

# 3. Install deps
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Run API
python main.py

# 5. Test
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/sectors
```
