# Retail Semantic Layer

A production-style AI-powered analytics platform using dbt, BigQuery, Cube, Google Gemini, and Streamlit — built to demonstrate modern data stack best practices.

> 📚 **[Complete Architecture Guide](docs/PROJECT_ARCHITECTURE.md)** — Comprehensive documentation covering all components, metrics, data models, and API reference.

## 🎯 Objective

Build a complete semantic layer on **BigQuery public data** (`thelook_ecommerce`) that showcases:

- **dbt** for data transformation (staging → marts)
- **Cube** for semantic metrics definitions and governance
- **Google Gemini** for AI-powered natural language queries
- **Streamlit** for interactive dashboards

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE                                │
│              BigQuery (thelook_ecommerce)                        │
│     orders | users | products | events | inventory               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION (dbt)                          │
│  ┌─────────┐    ┌──────────────┐    ┌───────────────────────┐   │
│  │ Staging │ →  │ Intermediate │ →  │   Marts (25+ models)  │   │
│  │ stg_*   │    │    int_*     │    │   fct_* / dim_*       │   │
│  └─────────┘    └──────────────┘    └───────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                SEMANTIC LAYER (Cube + Gemini)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Cube: Metric definitions, governance, caching           │   │
│  │  Gemini: Natural Language → SQL (via Vertex AI)          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PRESENTATION (Streamlit)                        │
│     KPI Dashboard | Revenue Charts | NLQ Interface               │
└─────────────────────────────────────────────────────────────────┘
```

## 🧠 Why Cube?

**The Core Idea:** dbt prepares trusted data; Cube turns that data into a queryable semantic API.

Without Cube, business logic leaks into SQL queries, BI tools, and ad-hoc scripts. With Cube, metrics are defined once and governed centrally.

### ❌ Without Cube
- **Flow:** Streamlit/Slack → Raw SQL → BigQuery
- **Problems:** Splintered logic, no semantic validation, hard to maintain.

### ✅ With Cube
- **Flow:** Streamlit/Slack → Cube API → BigQuery
- **Benefits:**
  - **Single Semantic Contract:** `total_revenue` means the same thing everywhere.
  - **Governance:** Access control and validation at the API level.
  - **Design:** Clean separation of concerns (dbt = transformation, Cube = semantics).

### What Cube Does (vs dbt)
| Layer | Responsibility | Example |
|-------|----------------|---------|
| **dbt** | Transformation, Cleaning, Materialization | `fct_orders`, `dim_users` |
| **Cube** | Metric Definitions, Query Generation, API | `Orders.totalRevenue`, `Users.count` |

Cube **never** transforms raw data. It reads trusted marts/views from dbt and serves them.

## 📁 Project Structure

models/
├── staging/
│   └── thelook_ecommerce/      # 7 sources (orders, events, inventory...)
│
└── marts/
    ├── core/                   # Dimensions (users, products, date)
    ├── customers/              # RFM, Cohorts, Retention, LTV
    ├── products/               # Affinity, Performance, Brand/Category
    ├── revenue/                # Daily/Monthly Financials, Geo Revenue
    ├── operations/             # Fulfillment, Returns, Status Funnels
    └── web/                    # Sessions, Traffic Funnels, Browser Stats


## 🔧 Setup

### Prerequisites

- Python 3.9+
- Google Cloud account with BigQuery access

### Installation

```bash
# Install dbt with BigQuery adapter
pip install dbt-bigquery

# Authenticate with Google Cloud
gcloud auth application-default login
gcloud auth application-default set-quota-project semantic-layer-484020
```

### Configure Profile

Create `~/.dbt/profiles.yml`:

```yaml
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: semantic-layer-484020
      dataset: retail_marts_dev
      location: US
      threads: 4
```

### Verify Connection

```bash
dbt debug
```

## 🚀 Usage

```bash
# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## 📊 Data Models & Analytics

### 1. Customer Intelligence (`marts/customers`)
| Model | Insights | Key Metrics |
|-------|----------|-------------|
| `fct_customer_orders` | Lifetime Value | `customer_lifespan_days`, `avg_order_value`, `is_repeat` |
| `fct_rfm_scores` | Segmentation | `recency_score`, `frequency_score`, `rfm_segment` (e.g., "Champions") |
| `fct_customer_cohorts` | Retention | `retention_rate`, `churn_rate` |
| `fct_cohort_retention` | Vintage Analysis | `cohort_size`, `active_customers` |

### 2. Product Analytics (`marts/products`)
| Model | Insights | Key Metrics |
|-------|----------|-------------|
| `fct_product_affinity` | **Basket Analysis** | `support`, `confidence`, `lift` (Product A + B co-occurrence) |
| `fct_product_performance` | Profitability | `profit_margin`, `return_rate`, `days_since_last_sale` |
| `fct_brand_performance` | Brand Strengths | `brand_rank`, `revenue_growth` |

### 3. Revenue Analytics (`marts/revenue`)
| Model | Insights | Key Metrics |
|-------|----------|-------------|
| `fct_monthly_revenue` | Growth Trends | `mom_growth_pct`, `yoy_growth_pct` |
| `fct_cohort_revenue` | LTV Trends | `revenue_per_active_user` |
| `fct_geography_revenue` | Regional Perf | `country_rank`, `market_penetration` |

### 4. Operations & Web (`marts/ops`, `marts/web`)
| Model | Insights | Key Metrics |
|-------|----------|-------------|
| `fct_fulfillment` | SLA Tracking | `processing_hours`, `shipping_hours`, `on_time_delivery_rate` |
| `fct_web_funnel` | Conversion | `product_view_rate`, `cart_to_purchase_rate`, `bounce_rate` |
| `fct_sessions` | User Behavior | `session_duration`, `events_per_session` |

## 🧪 Testing

24 data quality tests including:

- **Uniqueness**: Primary keys on all tables
- **Not null**: Required fields
- **Relationships**: Foreign key integrity
- **Accepted values**: Order status validation

## 📍 BigQuery Datasets

| Dataset | Purpose |
|---------|---------|
| `retail_marts_dev` | Development environment |
| `retail_marts` | Production (future) |
| `retail_public_demo` | Reviewer-accessible views |

## 🤖 Smart NLQ with Intelligent Routing

The NLQ API features **smart routing** - Gemini analyzes your question and automatically chooses the best execution path:

```
┌──────────────────────────────────────────────────────────────┐
│                    User Question                              │
│            "What is our total revenue?"                       │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   Gemini LLM Analysis                         │
│              "This is a simple aggregation..."                │
└──────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│  🧊 CUBE (Cached)    │    │  🔧 BigQuery (Ad-hoc)│
│  - Total revenue     │    │  - RFM segments      │
│  - Orders by country │    │  - Product analysis  │
│  - Daily trends      │    │  - Complex joins     │
└──────────────────────┘    └──────────────────────┘
```

### Route Examples

| Question | Route | Why |
|----------|-------|-----|
| "What is our total revenue?" | 🧊 Cube | Simple aggregation → cached |
| "Revenue by country" | 🧊 Cube | Grouped metric → governed |
| "Champions segment customers" | 🔧 BigQuery | RFM analysis → not in Cube |
| "Products with highest return rate" | 🔧 BigQuery | Complex query → ad-hoc SQL |

### API Endpoints

```bash
# Health check (shows Cube & BigQuery status)
curl https://semantic-api-5592650460.us-central1.run.app/

# Smart NLQ - automatically routes to Cube or BigQuery
curl -X POST https://semantic-api-5592650460.us-central1.run.app/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our total revenue by country?"}'

# Direct Cube query
curl -X POST https://semantic-api-5592650460.us-central1.run.app/cube/query \
  -H "Content-Type: application/json" \
  -d '{"measures": ["orders.total_revenue"], "dimensions": ["orders.country"]}'
```

### Technology

- **LLM:** Google Gemini 2.5 Flash (via Vertex AI)
- **Semantic Layer:** Cube.js (cached, governed metrics)
- **Data Warehouse:** BigQuery (ad-hoc queries)
- **API Framework:** FastAPI
- **Deployment:** Google Cloud Run

## 🚀 CI/CD Pipeline

Automated deployment via GitHub Actions:

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `deploy.yml` | Push to `main` | Deploys Cube → API → UI to Cloud Run |
| `dbt.yml` | Model changes | Runs dbt tests and builds |

### Required Secrets

Configure in **Settings → Secrets → Actions**:

| Secret | Description |
|--------|-------------|
| `GCP_SA_KEY` | GCP Service Account JSON key |
| `CUBEJS_API_SECRET` | Cube API authentication secret |

See [.github/CICD.md](.github/CICD.md) for detailed setup instructions.

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| **UI (Streamlit)** | https://semantic-ui-5592650460.us-central1.run.app |
| **API (FastAPI)** | https://semantic-api-5592650460.us-central1.run.app |
| **Cube** | https://cube-semantic-layer-5592650460.us-central1.run.app |

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[Architecture Guide](docs/PROJECT_ARCHITECTURE.md)** | Complete system design, all metrics, data models, API reference |
| **[CI/CD Guide](.github/CICD.md)** | GitHub Actions setup and deployment |
| **[Cube Setup](cube/README.md)** | Cube semantic layer configuration |
| **[Terraform Infrastructure](https://github.com/masefi/terraform-semantic-layer)** | GCP IAM & service accounts |

## 📚 Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [BigQuery thelook_ecommerce](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce)
- [Google Vertex AI](https://cloud.google.com/vertex-ai)
- [Cube.dev](https://cube.dev/)