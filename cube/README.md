# Cube Semantic Layer

This directory contains the Cube configuration for the Retail Semantic Layer.

## Overview

Cube provides a governed metrics layer on top of your dbt marts, offering:
- **Metric Definitions**: Consistent business metrics (revenue, orders, AOV)
- **Caching**: Automatic query caching for performance
- **Governance**: Access control and query validation
- **REST API**: Query metrics via HTTP endpoints

## Deployment Options

### Option 1: Cloud Run (Production) ⭐ Recommended

```bash
# Deploy Cube to Cloud Run
cd cube
chmod +x deploy.sh
./deploy.sh

# Then redeploy the API to connect to Cube
cd ../api
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Local Docker (Development)

```bash
cd cube
docker-compose up -d
```

### Option 3: Cube Cloud (Managed)

Sign up at [cube.dev/cloud](https://cube.dev/cloud) and import this configuration.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit UI                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI (api/)                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │  /ask (Gemini NLQ)  │    │  /cube/* (Cube API) │             │
│  └─────────────────────┘    └─────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│      Cube Server        │    │     BigQuery            │
│  (localhost:4000)       │    │  (direct SQL)           │
│  • REST API             │    │                         │
│  • Caching              │    │                         │
│  • Metrics definitions  │    │                         │
└─────────────────────────┘    └─────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BigQuery (dbt marts)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start Cube Server

```bash
cd cube
docker-compose up -d
```

This starts Cube on:
- **REST API**: http://localhost:4000
- **Playground**: http://localhost:4000/#/playground
- **SQL API**: localhost:15432 (PostgreSQL protocol)

### 2. Verify Connection

```bash
# Health check
curl http://localhost:4000/readyz

# Get available cubes
curl http://localhost:4000/cubejs-api/v1/meta \
  -H "Authorization: $(python3 -c "import jwt, time; print(jwt.encode({'iat': int(time.time()), 'exp': int(time.time()) + 3600}, 'retail-semantic-layer-secret-key-change-me', algorithm='HS256'))")"
```

### 3. Query Metrics

```bash
# Query via API
curl -X POST http://localhost:4000/cubejs-api/v1/load \
  -H "Content-Type: application/json" \
  -H "Authorization: <token>" \
  -d '{
    "query": {
      "measures": ["orders.count", "orders.total_revenue"],
      "dimensions": ["orders.status"]
    }
  }'
```

## File Structure

```
cube/
├── cube.yaml              # Main Cube configuration
├── docker-compose.yaml    # Docker setup for Cube server
├── README.md              # This file
└── model/
    └── cubes/
        ├── orders.yaml    # Order metrics & dimensions
        ├── revenue.yaml   # Revenue aggregations
        └── users.yaml     # User metrics
```

## Cube Definitions

### Orders Cube (`orders.yaml`)

| Measure | Type | Description |
|---------|------|-------------|
| `count` | count | Total number of orders |
| `total_revenue` | sum | Sum of order revenue |
| `avg_order_value` | avg | Average order value |

| Dimension | Type | Description |
|-----------|------|-------------|
| `order_id` | string | Primary key |
| `status` | string | Order status |
| `country` | string | Customer country |
| `order_date` | time | Order date |

### Revenue Daily Cube (`revenue.yaml`)

| Measure | Type | Description |
|---------|------|-------------|
| `total_revenue` | sum | Daily revenue |
| `total_orders` | sum | Daily order count |
| `avg_daily_order_value` | avg | Average order value |

### Users Cube (`users.yaml`)

| Measure | Type | Description |
|---------|------|-------------|
| `count` | count | Total users |
| `total_orders_placed` | sum | Total orders by users |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CUBEJS_DB_TYPE` | bigquery | Database type |
| `CUBEJS_DB_BQ_PROJECT_ID` | semantic-layer-484020 | GCP project |
| `CUBEJS_API_SECRET` | (required) | JWT signing secret |
| `CUBEJS_DEV_MODE` | true | Enable dev mode |

## Integration with FastAPI

The FastAPI backend (`api/`) includes Cube client code:

```python
from cube_client import query_cube, get_order_metrics

# Query Cube
result = query_cube(
    measures=["orders.count", "orders.total_revenue"],
    dimensions=["orders.status"]
)

# Use pre-built metrics
metrics = get_order_metrics()
```

## API Endpoints (via FastAPI)

| Endpoint | Description |
|----------|-------------|
| `GET /cube/health` | Cube server health |
| `GET /cube/meta` | Available cubes/measures |
| `POST /cube/query` | Execute custom query |
| `GET /cube/metrics/orders` | Order metrics |
| `GET /cube/metrics/revenue/daily` | Daily revenue |
| `GET /cube/metrics/revenue/by-country` | Revenue by country |
| `GET /cube/metrics/users` | User metrics |

## Troubleshooting

### Cube won't start
```bash
# Check logs
docker-compose logs cube

# Verify BigQuery credentials
gcloud auth application-default print-access-token
```

### Authentication errors
```bash
# Regenerate token
export CUBEJS_API_SECRET="your-secret"
python3 -c "import jwt, time; print(jwt.encode({'iat': int(time.time()), 'exp': int(time.time()) + 3600}, '$CUBEJS_API_SECRET', algorithm='HS256'))"
```

### No data returned
- Verify BigQuery views exist: `vw_orders`, `vw_users`, `vw_daily_revenue`
- Check Cube playground: http://localhost:4000/#/playground
