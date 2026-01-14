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

```
models/
├── staging/
│   └── thelook_ecommerce/
│       ├── stg_orders.sql
│       ├── stg_order_items.sql
│       ├── stg_users.sql
│       ├── stg_products.sql
│       ├── sources.yml
│       └── _staging_schema.yml
│
└── marts/
    ├── core/
    │   ├── fct_orders.sql        # Fact: order-level with revenue
    │   ├── dim_users.sql         # Dim: user demographics
    │   ├── dim_products.sql      # Dim: product catalog
    │   └── _core_schema.yml
    │
    └── metrics/
        ├── daily_revenue.sql     # Pre-aggregated daily metrics
        └── _metrics_schema.yml
```

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

## 📊 Data Models

### Staging Layer

| Model | Source Table | Description |
|-------|--------------|-------------|
| `stg_orders` | `orders` | Order headers with status & timestamps |
| `stg_order_items` | `order_items` | Line items with sale price |
| `stg_users` | `users` | User demographics |
| `stg_products` | `products` | Product catalog |

### Mart Layer

| Model | Grain | Key Metrics |
|-------|-------|-------------|
| `fct_orders` | Order | `total_revenue`, `item_count` |
| `dim_users` | User | `total_orders`, `first_order_at` |
| `dim_products` | Product | `profit_margin` |
| `daily_revenue` | Day | `total_revenue`, `avg_order_value` |

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