# Retail Semantic Layer

A production-style semantic layer demo using dbt, BigQuery, and Cube — built to demonstrate analytics engineering best practices.

## 🎯 Objective

Build a complete semantic layer on **BigQuery public data** (`thelook_ecommerce`) that showcases:

- **dbt** for data transformation (staging → marts)
- **Cube** for semantic metrics layer
- **Streamlit** for dashboards
- **NLQ API** for natural language queries

## 🏗️ Architecture

```
BigQuery Public Dataset (thelook_ecommerce)
            ↓
       dbt Sources
            ↓
     Staging Models (stg_*)     ← Views, 1:1 with source
            ↓
     Mart Models (fct_*, dim_*) ← Tables, business logic
            ↓
  Semantic Exposure Layer       ← Public-safe views
            ↓
     Cube Semantic Layer        ← Metric definitions & Query API
            ↓
  Streamlit UI + NLQ API        ← Presentation Layer
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

## 📚 Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [BigQuery thelook_ecommerce](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce)
- [Cube.dev](https://cube.dev/)