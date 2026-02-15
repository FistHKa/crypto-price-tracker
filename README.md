# 🚀 Crypto Price Tracker

## 🧩 What the service actually does

This service continuously collects cryptocurrency index prices and builds a historical price database.

Instead of querying an external API every time a client requests data, the system:

1. fetches prices in the background every minute
2. stores them safely in PostgreSQL
3. allows clients to query already collected historical data instantly

This design avoids external API dependency during client requests and simulates a real-world data ingestion service
used in trading platforms and analytics systems.

---

## 🎯 Project Goal

Design and implement a production-style asynchronous backend service that:

- periodically fetches cryptocurrency index prices from an external API
- stores historical data safely in PostgreSQL
- exposes a clean REST API for querying latest and historical prices
- runs background jobs independently from the API layer
- provides reliable automated testing with an isolated database
- is fully reproducible via Docker and verified in CI

---

## ✨ Features

- Async FastAPI REST API
- Background price collection via Celery + Redis
- PostgreSQL storage with SQLAlchemy 2.0 async
- Alembic database migrations
- Fully dockerized environment
- Isolated test database
- Async pytest test suite
- GitHub Actions CI pipeline
- Decimal-safe price storage
- ISO 8601 timestamp API

---

## 🚀 Quick Start

### 1) Clone repository

```bash
git clone https://github.com/FistHKa/crypto-price-tracker.git
cd crypto-price-tracker
```

### 2) Create environment file

```bash
cp .env.example .env
```

### 3) Run services

```bash
docker compose up --build
```

### 4) Open API docs

```bash
http://localhost:8000/docs
```

---

## 🏗️ Architecture

External API (Deribit) → Celery Worker → PostgreSQL → FastAPI API → Clients

---

## 🔄 Data Flow

1) Celery Beat schedules a periodic task every minute
2) Worker fetches BTC and ETH index prices from Deribit API
3) Prices are validated and normalized
4) Data is stored in PostgreSQL
5) FastAPI reads stored data and serves client requests

*Important*: the API never calls the external provider directly.
Clients always read from the database.

---

## 🧰 Tech Stack

| Layer           | Technology                      |
| --------------- | ------------------------------- |
| API             | FastAPI                         |
| Async HTTP      | aiohttp                         |
| Background Jobs | Celery                          |
| Broker          | Redis                           |
| Database        | PostgreSQL                      |
| ORM             | SQLAlchemy 2.0 Async            |
| Migrations      | Alembic                         |
| Testing         | pytest + pytest-asyncio + httpx |
| Containers      | Docker + Docker Compose         |
| CI              | GitHub Actions                  |

---

## 📁 Project Structure

The project is organized as a layered Python service with clear separation between API layer,
database layer, background tasks, and integrations.

```text
crypto_price_tracker/
│
├── alembic/
│  └── versions/
│
├── app/
│ ├── api/
│ │  └── prices.py
│ │
│ ├── clients/
│ │  ├── __init__.py
│ │  └── deribit.py
│ │
│ ├── core/
│ │  ├── __init__.py
│ │  ├── config.py
│ │  └── logging.py
│ │
│ ├── db/
│ │  ├── __init__.py
│ │  ├── base.py
│ │  ├── runtime.py
│ │  └── session.py
│ │
│ ├── models/
│ │  ├── __init__.py
│ │  └── price.py
│ │
│ ├── repositories/
│ │  ├── __init__.py
│ │  └── prices.py
│ │
│ ├── schemas/
│ │  ├── __init__.py
│ │  └── price.py
│ │
│ ├── tasks/
│ │  ├── __init__.py
│ │  └── prices.py
│ │
│ ├── __init__.py
│ ├── celery_app.py
│ └── main.py
│
├── tests/
│  ├── __init__.py
│  ├── conftest.py
│  └── test_prices_api.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── docker-compose.test.yml
├── Dockerfile
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## ⚙️ Environment Variables

The application is configured via environment variables.
See `.env.example` for reference.

| Variable              | Description                        |
| --------------------- | ---------------------------------- |
| APP_NAME              | Application name                   |
| ENV                   | Environment (dev/test/prod)        |
| DATABASE_URL          | Async PostgreSQL connection string |
| TEST_DATABASE_URL     | Database used during tests         |
| POSTGRES_DB           | Default DB name (docker)           |
| POSTGRES_USER         | DB user                            |
| POSTGRES_PASSWORD     | DB password                        |
| CELERY_BROKER_URL     | Redis broker                       |
| CELERY_RESULT_BACKEND | Redis backend                      |

---

## 🐋 Running Locally (Docker)

### 1) Create `.env` from the example:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 2) Build & start the stack:

```bash
docker compose up --build
```

API will be available at:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

Stop:

```bash
docker compose down
```

---

## 🧪 Running Tests (isolated PostgreSQL)

Tests run Alembic migrations automatically inside the `tests` service before executing pytest.

### Run:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### Clean up (recommended):

```bash
docker compose -f docker-compose.test.yml down -v
```

---

## 📡 API Endpoints

### Health Check

```bash
GET /health
```

Response:

```json
{
  "status": "ok",
  "app_name": "crypto-price-tracker",
  "env": "dev"
}
```

### Get Latest Price

Returns the most recent stored price for a ticker.

Query Parameters:

| Name   | Type   | Required | Description |
| ------ | ------ | -------- | ----------- |
| ticker | string | yes      | BTC or ETH  |

```bash
GET /prices/latest?ticker=BTC
```

### Get All Prices for Ticker

Returns all stored prices for a ticker (ordered by timestamp).

Query Parameters:

| Name   | Type   | Required | Description |
| ------ | ------ | -------- | ----------- |
| ticker | string | yes      | BTC or ETH  |

```bash
GET /prices?ticker=BTC
```

### Get Prices by Date Range

Filters prices within a datetime range.

Query Parameters:

| Name      | Type     | Required | Description  |
| --------- | -------- | -------- | ------------ |
| ticker    | string   | yes      | BTC or ETH   |
| date_from | ISO 8601 | no       | Start date   |
| date_to   | ISO 8601 | no       | End date     |
| limit     | int      | no       | Default 1000 |
| offset    | int      | no       | Default 0    |

```bash
GET /prices/by-date?ticker=BTC&date_from=2026-02-03T20:45:00Z&date_to=2026-02-03T20:55:00Z
```

---

## 🗄️ Database

Database: PostgreSQL 16
`prices` table:

| Column    | Type        | Description   |
| --------- | ----------- | ------------- |
| id        | integer PK  | Auto ID       |
| ticker    | varchar     | BTC / ETH     |
| price     | numeric     | Decimal price |
| timestamp | timestamptz | UTC timestamp |

All timestamps are stored as timezone-aware UTC.

---

## 📦 Migrations

Migrations are handled via **Alembic**.

### Create migration

```bash
alembic revision --autogenerate -m "message"
```

### Apply migrations

```bash
alembic upgrade head
```

Migrations are applied automatically on first container startup and during tests.

---

## 🔍 Testing Strategy

- Real PostgreSQL database
- Separate test DB
- Fresh schema via Alembic
- Database cleanup between tests
- Full API integration tests (no mocks)

*Covered*:
- health endpoint
- latest price
- list retrieval
- date range filtering

---

## 🧠 Key Engineering Decisions

### Async everywhere
Improves I/O performance for:
- HTTP requests
- DB operations
- Background tasks

### Celery for background jobs
Separates API workload from ingestion workload.

### Docker-first development
Provides reproducible environment and easy onboarding.

### Separate Test DB
Prevents:
- Data corruption
- Non-deterministic tests

---

## 🔁 CI Pipeline

CI is implemented via **GitHub Actions**.

On every push & pull request:
- Build Docker image
- Start test PostgreSQL
- Apply migrations
- Run pytest
- Pipeline fails automatically on any test failure

File location:

```bash
.github/workflows/ci.yml`
```