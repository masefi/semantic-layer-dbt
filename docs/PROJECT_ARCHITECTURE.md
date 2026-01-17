# Retail Semantic Layer - Complete Architecture Guide

> **A production-grade AI-powered analytics platform demonstrating modern data stack best practices**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Data Flow Pipeline](#data-flow-pipeline)
4. [Component Deep Dive](#component-deep-dive)
   - [Data Warehouse (BigQuery)](#1-data-warehouse-bigquery)
   - [Transformation Layer (dbt)](#2-transformation-layer-dbt)
   - [AI Semantic Layer (Gemini)](#3-ai-semantic-layer-gemini)
   - [Presentation Layer (Streamlit)](#4-presentation-layer-streamlit)
5. [Data Models Catalog](#data-models-catalog)
6. [Metrics Dictionary](#metrics-dictionary)
7. [API Reference](#api-reference)
8. [Natural Language Query (NLQ) System](#natural-language-query-nlq-system)
9. [Deployment Architecture](#deployment-architecture)
10. [Security & Governance](#security--governance)

---

## Executive Summary

The **Retail Semantic Layer** is a complete, production-style analytics platform that transforms raw e-commerce data into actionable business intelligence through natural language queries. It demonstrates the modern data stack paradigm where:

- **Raw Data** lives in a cloud data warehouse (BigQuery)
- **Transformations** are managed as code (dbt)
- **Semantic Understanding** is powered by AI (Google Gemini)
- **Insights** are delivered through intuitive interfaces (Streamlit)

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Natural Language Queries** | Ask questions in plain English: *"What was our revenue last month?"* |
| **Real-time Analytics** | Live dashboards with 5-minute data refresh |
| **Customer Intelligence** | RFM segmentation, cohort analysis, lifetime value |
| **Product Analytics** | Market basket analysis, affinity scoring, performance tracking |
| **Operational Insights** | Fulfillment SLAs, return analysis, status funnels |

### Technology Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Streamlit Dashboard (app.py)                    │   │
│  │  • KPI Metrics  • Revenue Trends  • Natural Language Query   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SEMANTIC LAYER                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │           FastAPI + Google Gemini 2.5 Flash                  │   │
│  │  • NLQ-to-SQL Translation  • Query Execution  • Validation   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      TRANSFORMATION LAYER                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    dbt (Data Build Tool)                     │   │
│  │  • Staging (7 sources)  • Marts (25+ models)  • Tests (24+)  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA WAREHOUSE                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Google BigQuery                           │   │
│  │  Source: bigquery-public-data.thelook_ecommerce              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Overview

### Design Philosophy

This project follows the **Medallion Architecture** pattern with three distinct data layers:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   BRONZE    │ ──▶ │   SILVER    │ ──▶ │    GOLD     │ ──▶ │  SEMANTIC   │
│   (Source)  │     │  (Staging)  │     │   (Marts)   │     │   (Views)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     Raw data        Light cleanup       Business logic      Public exposure
     BigQuery         stg_* views        fct_*/dim_*          vw_* views
```

### Why This Architecture?

| Layer | Purpose | Benefit |
|-------|---------|---------|
| **Bronze (Sources)** | Direct access to raw data | Single source of truth |
| **Silver (Staging)** | Standardization, typing, basic cleaning | Consistent data contracts |
| **Gold (Marts)** | Business logic, aggregations, metrics | Reusable analytics assets |
| **Semantic (Views)** | Controlled exposure for external tools | Security & governance |

---

## Data Flow Pipeline

### End-to-End Data Journey

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────┘

[BigQuery Public Data] ─────────────────────────────────────────────────────┐
         │                                                                   │
         │  thelook_ecommerce dataset                                        │
         │  • orders (100K+ records)                                         │
         │  • order_items (300K+ records)                                    │
         │  • users (100K+ records)                                          │
         │  • products (30K+ records)                                        │
         │  • events (2M+ records)                                           │
         │  • inventory_items                                                │
         │  • distribution_centers                                           │
         ▼                                                                   │
┌─────────────────────────────────────────┐                                  │
│         STAGING LAYER (Views)           │                                  │
│  ┌───────────────────────────────────┐  │                                  │
│  │ stg_orders         - Order header │  │                                  │
│  │ stg_order_items    - Line items   │  │                                  │
│  │ stg_users          - Customer     │  │                                  │
│  │ stg_products       - Catalog      │  │                                  │
│  │ stg_events         - Web events   │  │                                  │
│  │ stg_inventory      - Stock        │  │                                  │
│  │ stg_dist_centers   - Warehouses   │  │                                  │
│  └───────────────────────────────────┘  │                                  │
└─────────────────────────────────────────┘                                  │
         │                                                                   │
         │  Cleaned, typed, standardized                                     │
         ▼                                                                   │
┌─────────────────────────────────────────┐                                  │
│       INTERMEDIATE LAYER (Tables)       │                                  │
│  ┌───────────────────────────────────┐  │                                  │
│  │ int_order_items_enriched          │  │ ◀── Wide join of orders,        │
│  │   • order + item + product + user │  │     products, users             │
│  │                                   │  │                                  │
│  │ int_user_order_summary            │  │ ◀── Pre-aggregated user         │
│  │   • total_orders, revenue, profit │  │     lifetime metrics            │
│  └───────────────────────────────────┘  │                                  │
└─────────────────────────────────────────┘                                  │
         │                                                                   │
         │  Denormalized, enriched                                           │
         ▼                                                                   │
┌─────────────────────────────────────────┐                                  │
│          MART LAYER (Tables)            │                                  │
│                                         │                                  │
│  ┌─────────────────────────────────┐    │                                  │
│  │ CORE (Dimensions & Facts)       │    │                                  │
│  │  • dim_users, dim_products      │    │                                  │
│  │  • dim_date, fct_orders         │    │                                  │
│  └─────────────────────────────────┘    │                                  │
│                                         │                                  │
│  ┌─────────────────────────────────┐    │                                  │
│  │ CUSTOMERS (Segmentation)        │    │                                  │
│  │  • fct_customer_orders          │    │                                  │
│  │  • fct_rfm_scores               │    │                                  │
│  │  • fct_customer_cohorts         │    │                                  │
│  │  • fct_customer_retention       │    │                                  │
│  └─────────────────────────────────┘    │                                  │
│                                         │                                  │
│  ┌─────────────────────────────────┐    │                                  │
│  │ PRODUCTS (Performance)          │    │                                  │
│  │  • fct_product_performance      │    │                                  │
│  │  • fct_category_performance     │    │                                  │
│  │  • fct_brand_performance        │    │                                  │
│  │  • fct_product_affinity         │    │                                  │
│  └─────────────────────────────────┘    │                                  │
│                                         │                                  │
│  ┌─────────────────────────────────┐    │                                  │
│  │ REVENUE (Financial)             │    │                                  │
│  │  • fct_daily_revenue            │    │                                  │
│  │  • fct_monthly_revenue          │    │                                  │
│  │  • fct_cohort_revenue           │    │                                  │
│  │  • fct_geography_revenue        │    │                                  │
│  └─────────────────────────────────┘    │                                  │
│                                         │                                  │
│  ┌─────────────────────────────────┐    │                                  │
│  │ OPERATIONS (Fulfillment)        │    │                                  │
│  │  • fct_fulfillment              │    │                                  │
│  │  • fct_fulfillment_summary      │    │                                  │
│  │  • fct_returns, fct_order_status│    │                                  │
│  └─────────────────────────────────┘    │                                  │
│                                         │                                  │
│  ┌─────────────────────────────────┐    │                                  │
│  │ WEB (Digital Analytics)         │    │                                  │
│  │  • fct_sessions                 │    │                                  │
│  │  • fct_web_funnel               │    │                                  │
│  │  • fct_traffic_source_perf      │    │                                  │
│  │  • fct_browser_performance      │    │                                  │
│  └─────────────────────────────────┘    │                                  │
└─────────────────────────────────────────┘                                  │
         │                                                                   │
         │  Business-ready metrics                                           │
         ▼                                                                   │
┌─────────────────────────────────────────┐                                  │
│       SEMANTIC LAYER (Views)            │                                  │
│  ┌───────────────────────────────────┐  │                                  │
│  │ vw_orders         - Safe orders   │  │ ◀── External tool access        │
│  │ vw_users          - Safe users    │  │     (Cube, BI tools)            │
│  │ vw_daily_revenue  - Safe revenue  │  │                                  │
│  └───────────────────────────────────┘  │                                  │
└─────────────────────────────────────────┘                                  │
         │                                                                   │
         │  Governed, documented                                             │
         ▼                                                                   │
┌─────────────────────────────────────────┐                                  │
│         AI SEMANTIC API                  │                                  │
│  ┌───────────────────────────────────┐  │                                  │
│  │ Google Gemini 2.5 Flash           │  │                                  │
│  │  • NLQ → SQL translation          │  │                                  │
│  │  • Schema-aware prompting         │  │                                  │
│  │  • Query execution & response     │  │                                  │
│  └───────────────────────────────────┘  │                                  │
└─────────────────────────────────────────┘                                  │
         │                                                                   │
         ▼                                                                   │
┌─────────────────────────────────────────┐                                  │
│         STREAMLIT DASHBOARD              │ ◀─────────────────────────────────┘
│  • Real-time KPIs                       │
│  • Interactive charts                   │
│  • Natural language query interface     │
└─────────────────────────────────────────┘
```

---

## Component Deep Dive

### 1. Data Warehouse (BigQuery)

#### Source Dataset: `bigquery-public-data.thelook_ecommerce`

The Look is a fictitious e-commerce clothing site developed by Google. The dataset contains:

| Table | Description | Record Count | Key Fields |
|-------|-------------|--------------|------------|
| `orders` | Order headers | ~100K+ | order_id, user_id, status, timestamps |
| `order_items` | Line items | ~300K+ | order_item_id, product_id, sale_price |
| `users` | Customer profiles | ~100K+ | user_id, email, demographics, location |
| `products` | Product catalog | ~30K+ | product_id, name, brand, category, price |
| `events` | Web clickstream | ~2M+ | event_id, event_type, session_id, uri |
| `inventory_items` | Stock tracking | ~300K+ | inventory_item_id, product_id, cost |
| `distribution_centers` | Warehouses | ~10 | id, name, latitude, longitude |

#### BigQuery Datasets

| Dataset | Purpose | Schema |
|---------|---------|--------|
| `retail_marts_dev` | Development environment | All dbt models |
| `retail_marts_dev_public_demo` | Semantic exposure layer | vw_* views only |

---

### 2. Transformation Layer (dbt)

#### Project Configuration

```yaml
# dbt_project.yml
name: 'retail_semantic_layer'
version: '1.0.0'

models:
  retail_semantic_layer:
    staging:
      +materialized: view        # Lightweight, always fresh
    marts:
      +materialized: table       # Optimized for query performance
    semantic:
      +materialized: view        # External access layer
      +schema: public_demo       # Separate schema for security
```

#### Model Layers

##### Staging Models (`models/staging/`)

**Purpose:** 1:1 mapping with source tables. Light transformations only.

| Model | Source | Transformations |
|-------|--------|-----------------|
| `stg_orders` | orders | Rename columns, cast types |
| `stg_order_items` | order_items | Calculate line totals |
| `stg_users` | users | Standardize country names |
| `stg_products` | products | Calculate margins |
| `stg_events` | events | Parse event types |
| `stg_inventory_items` | inventory_items | Add cost fields |
| `stg_distribution_centers` | distribution_centers | Geocoding prep |

##### Intermediate Models (`models/intermediate/`)

**Purpose:** Denormalized tables for efficient downstream processing.

| Model | Description | Grain |
|-------|-------------|-------|
| `int_order_items_enriched` | Wide join: order + item + product + user | Order Item |
| `int_user_order_summary` | Pre-aggregated user lifetime metrics | User |

**Key Fields in `int_order_items_enriched`:**
```sql
-- IDs
order_item_id, order_id, user_id, product_id, distribution_center_id

-- Status & Timestamps  
order_status, order_created_at, order_shipped_at, order_delivered_at

-- Financials
sale_price, cost, item_profit

-- Product Details
product_name, brand, category, department

-- User Context
user_country, user_city, user_traffic_source
```

##### Mart Models (`models/marts/`)

See [Data Models Catalog](#data-models-catalog) for complete documentation.

---

### 3. AI Semantic Layer (Gemini)

#### Overview

The semantic layer uses **Google Gemini 2.5 Flash** via Vertex AI to translate natural language questions into executable SQL queries.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                          │
│                        (api/main.py)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   /ask       │    │  /sql-only   │    │   /schema    │       │
│  │  (POST)      │    │   (POST)     │    │    (GET)     │       │
│  │              │    │              │    │              │       │
│  │ NLQ → SQL    │    │ NLQ → SQL    │    │ Return       │       │
│  │ + Execute    │    │ (no execute) │    │ schema info  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│           │                  │                                   │
│           ▼                  ▼                                   │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              generate_sql(user_query)                │        │
│  │                                                      │        │
│  │  1. Build prompt with SYSTEM_PROMPT + schema         │        │
│  │  2. Call Gemini 2.5 Flash                            │        │
│  │  3. Parse JSON response                              │        │
│  │  4. Return {intent, table, sql, explanation}         │        │
│  └─────────────────────────────────────────────────────┘        │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              execute_query(sql)                      │        │
│  │                                                      │        │
│  │  1. Run SQL against BigQuery                         │        │
│  │  2. Return results as JSON (limit 100 rows)          │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### System Prompt Design

The LLM is provided with a comprehensive system prompt (`api/prompts.py`) containing:

1. **Role Definition:** Expert analytics engineer persona
2. **Schema Context:** Complete list of tables with descriptions
3. **Business Rules:** Date logic, aggregation rules, table selection
4. **Output Format:** Strict JSON schema
5. **Examples:** Few-shot learning with sample Q&A pairs

**Schema Knowledge Provided to LLM:**

```
DIMENSION TABLES:
- dim_date: Calendar reference (date_key, month_name, is_weekend)
- dim_users: User attributes (demographics, location, traffic_source)
- dim_products: Product catalog (brand, category, department, margin)
- dim_distribution_centers: Warehouse locations

FACT TABLES:
- fct_daily_revenue: Daily aggregates (revenue, orders, profit)
- fct_monthly_revenue: Monthly with MoM/YoY growth
- fct_customer_orders: Customer lifetime value metrics
- fct_rfm_scores: RFM segmentation
- fct_product_performance: Product-level metrics
- fct_category_performance: Monthly category stats
- fct_brand_performance: Monthly brand stats
- fct_fulfillment: Order-level shipping metrics
- fct_web_funnel: Conversion funnel by traffic source
```

#### LLM Configuration

```python
# Model Settings
model_name = "gemini-2.5-flash"
temperature = 0.1          # Low for deterministic SQL
max_output_tokens = 2048   # Sufficient for complex queries
```

---

### 4. Presentation Layer (Streamlit)

#### Dashboard Components

```
┌─────────────────────────────────────────────────────────────────┐
│  🛍️ Retail Semantic Layer Demo                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SIDEBAR                          MAIN CONTENT                   │
│  ┌─────────────┐                  ┌──────────────────────────┐  │
│  │ Connection  │                  │      KPI METRICS          │  │
│  │ Settings    │                  │  ┌────┐ ┌────┐ ┌────┐    │  │
│  │ ○ Mock      │                  │  │$XXX│ │XXXX│ │$XX │    │  │
│  │ ● Live      │                  │  │Rev │ │Ord │ │AOV │    │  │
│  │             │                  │  └────┘ └────┘ └────┘    │  │
│  │ [Refresh]   │                  └──────────────────────────┘  │
│  │             │                                                 │
│  │ Filters     │                  ┌──────────────────────────┐  │
│  │ 📅 Date     │                  │         TABS              │  │
│  │ 📊 Status   │                  │ [Overview] [Trends] [NLQ] │  │
│  │             │                  │                           │  │
│  └─────────────┘                  │  ┌────────────────────┐   │  │
│                                   │  │  Revenue Chart     │   │  │
│                                   │  │  📈                │   │  │
│                                   │  └────────────────────┘   │  │
│                                   │                           │  │
│                                   │  ┌────────────────────┐   │  │
│                                   │  │  Category Pie      │   │  │
│                                   │  │  🥧                │   │  │
│                                   │  └────────────────────┘   │  │
│                                   └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Features

| Feature | Description |
|---------|-------------|
| **Data Source Toggle** | Switch between mock data and live API |
| **Cache Control** | 5-minute TTL with manual refresh button |
| **KPI Cards** | Total Revenue, Orders, AOV with trend indicators |
| **Revenue Trend** | Interactive time series chart (Plotly) |
| **Category Breakdown** | Donut chart of sales by category |
| **NLQ Interface** | Free-form question input with SQL preview |

---

## Data Models Catalog

### Core Domain (`marts/core/`)

#### `dim_users`
**Description:** Master user dimension with demographics and behavioral attributes

| Column | Type | Description |
|--------|------|-------------|
| user_id | INT | Primary key |
| email | STRING | User email (masked in public views) |
| first_name | STRING | First name |
| last_name | STRING | Last name |
| age | INT | Age in years |
| age_group | STRING | Binned age (18-24, 25-34, etc.) |
| gender | STRING | M/F |
| country | STRING | Country of residence |
| city | STRING | City |
| traffic_source | STRING | Acquisition channel |
| created_at | TIMESTAMP | Account creation date |
| signup_cohort | DATE | Monthly cohort (YYYY-MM-01) |
| total_orders | INT | Lifetime order count |
| total_revenue | FLOAT | Lifetime revenue |

#### `dim_products`
**Description:** Product catalog with pricing and categorization

| Column | Type | Description |
|--------|------|-------------|
| product_id | INT | Primary key |
| product_name | STRING | Full product name |
| brand | STRING | Brand name |
| category | STRING | Product category |
| department | STRING | Men/Women/etc. |
| cost | FLOAT | Cost to company |
| retail_price | FLOAT | Retail price |
| profit_margin | FLOAT | retail_price - cost |
| distribution_center_id | INT | FK to distribution center |

#### `dim_date`
**Description:** Date dimension for time-based analysis

| Column | Type | Description |
|--------|------|-------------|
| date_key | DATE | Primary key |
| day_of_week | STRING | Monday, Tuesday, etc. |
| day_of_month | INT | 1-31 |
| month_name | STRING | January, February, etc. |
| month_number | INT | 1-12 |
| quarter | INT | 1-4 |
| year | INT | YYYY |
| is_weekend | BOOL | True for Sat/Sun |

#### `fct_orders`
**Description:** Order-level fact table with revenue metrics

| Column | Type | Description |
|--------|------|-------------|
| order_id | INT | Primary key |
| user_id | INT | FK to dim_users |
| order_status | STRING | Complete/Shipped/Returned/etc. |
| order_created_at | TIMESTAMP | Order timestamp |
| item_count | INT | Number of items |
| total_revenue | FLOAT | Sum of sale prices |
| total_profit | FLOAT | Sum of item profits |
| is_first_order | BOOL | Customer's first order flag |

---

### Customer Analytics (`marts/customers/`)

#### `fct_customer_orders`
**Description:** Customer lifetime value and profile metrics

| Column | Type | Description |
|--------|------|-------------|
| user_id | INT | Primary key |
| first_order_at | TIMESTAMP | First purchase date |
| last_order_at | TIMESTAMP | Most recent purchase |
| customer_lifespan_days | INT | Days between first and last order |
| days_since_last_order | INT | Recency metric |
| total_orders | INT | Lifetime order count |
| total_revenue | FLOAT | Lifetime revenue (LTV) |
| total_profit | FLOAT | Lifetime profit |
| total_items | INT | Total items purchased |
| total_returns | INT | Number of returns |
| return_rate | FLOAT | Returns / Orders |
| avg_order_value | FLOAT | Revenue / Orders |
| avg_items_per_order | FLOAT | Items / Orders |
| customer_status | STRING | New/Repeat/Loyal |
| signup_cohort | DATE | Acquisition cohort |
| age_group | STRING | Customer age band |
| country | STRING | Country |

#### `fct_rfm_scores`
**Description:** RFM (Recency, Frequency, Monetary) segmentation

| Column | Type | Description |
|--------|------|-------------|
| user_id | INT | Primary key |
| recency_days | INT | Days since last order |
| frequency | INT | Total order count |
| monetary | FLOAT | Total revenue |
| recency_score | INT | 1-5 (5 = most recent) |
| frequency_score | INT | 1-5 (5 = most frequent) |
| monetary_score | INT | 1-5 (5 = highest value) |
| rfm_code | STRING | Concatenated scores (e.g., "555") |
| rfm_segment | STRING | Named segment |

**RFM Segments:**

| Segment | Criteria | Action |
|---------|----------|--------|
| **Champions** | R≥4, F≥4, M≥4 | Reward, upsell premium |
| **Loyal Customers** | R≥3, F≥4, M≥3 | Engage, loyalty programs |
| **Potential Loyalists** | R≥4, F≥2, M≥2 | Nurture with targeted offers |
| **Recent Customers** | R≥4, F=1 | Onboard, encourage 2nd purchase |
| **Promising** | R≥3, F=1 | Create brand awareness |
| **Needs Attention** | R≥2, F≥2 | Reactivation campaigns |
| **Can't Lose** | R≤2, F≥4 | Win back immediately |
| **At Risk** | R≤2, F≥2 | Prevent churn |
| **Lost** | Others | Re-engagement or write-off |

#### `fct_customer_cohorts`
**Description:** Monthly activity matrix for cohort retention analysis

| Column | Type | Description |
|--------|------|-------------|
| user_id | INT | User identifier |
| signup_cohort | DATE | First-of-month signup date |
| activity_month | DATE | Month of activity |
| months_since_signup | INT | Cohort age |
| is_active | BOOL | Had order in month |

#### `fct_customer_retention`
**Description:** Aggregated retention rates by cohort

| Column | Type | Description |
|--------|------|-------------|
| signup_cohort | DATE | Cohort month |
| months_since_signup | INT | Period number |
| cohort_size | INT | Original cohort size |
| active_customers | INT | Customers active in period |
| retention_rate | FLOAT | active / cohort_size |
| churned_customers | INT | Cumulative churned |

---

### Product Analytics (`marts/products/`)

#### `fct_product_performance`
**Description:** Product-level sales and profitability metrics

| Column | Type | Description |
|--------|------|-------------|
| product_id | INT | Primary key |
| product_name | STRING | Product name |
| brand | STRING | Brand |
| category | STRING | Category |
| department | STRING | Department |
| total_units_sold | INT | Quantity sold |
| total_revenue | FLOAT | Sales revenue |
| total_profit | FLOAT | Profit |
| profit_margin_pct | FLOAT | Profit / Revenue |
| avg_sale_price | FLOAT | Average selling price |
| items_returned | INT | Return count |
| return_rate | FLOAT | Returns / Sold |
| first_sale_date | DATE | First sale |
| last_sale_date | DATE | Most recent sale |
| days_since_last_sale | INT | Staleness indicator |

#### `fct_category_performance`
**Description:** Monthly category-level aggregates

| Column | Type | Description |
|--------|------|-------------|
| category | STRING | Category name |
| department | STRING | Department |
| order_month | TIMESTAMP | Month |
| total_units_sold | INT | Units |
| total_revenue | FLOAT | Revenue |
| total_profit | FLOAT | Profit |
| avg_sale_price | FLOAT | ASP |
| order_count | INT | Distinct orders |
| unique_customers | INT | Distinct customers |
| items_returned | INT | Returns |
| return_rate | FLOAT | Return rate |
| category_rank_by_revenue | INT | Rank within month |

#### `fct_brand_performance`
**Description:** Monthly brand-level aggregates

| Column | Type | Description |
|--------|------|-------------|
| brand | STRING | Brand name |
| order_month | TIMESTAMP | Month |
| total_units_sold | INT | Units |
| total_revenue | FLOAT | Revenue |
| total_profit | FLOAT | Profit |
| order_count | INT | Orders |

#### `fct_product_affinity`
**Description:** Market basket analysis for product recommendations

| Column | Type | Description |
|--------|------|-------------|
| product_id_a | INT | First product |
| product_name_a | STRING | Name |
| category_a | STRING | Category |
| product_id_b | INT | Second product |
| product_name_b | STRING | Name |
| category_b | STRING | Category |
| co_occurrence_count | INT | Times bought together |
| support | FLOAT | P(A ∩ B) |
| confidence_a_to_b | FLOAT | P(B\|A) |
| confidence_b_to_a | FLOAT | P(A\|B) |
| lift | FLOAT | P(A ∩ B) / P(A)×P(B) |

**Interpretation:**
- **Support:** How often do these products appear together? (>0.01 is significant)
- **Confidence:** If customer buys A, how likely are they to buy B?
- **Lift:** >1 means positive association, <1 means negative, =1 means independent

---

### Revenue Analytics (`marts/revenue/`)

#### `fct_daily_revenue`
**Description:** Daily financial metrics

| Column | Type | Description |
|--------|------|-------------|
| order_date | DATE | Primary key |
| total_orders | INT | Order count |
| total_items | INT | Items sold |
| total_revenue | FLOAT | Gross revenue |
| total_profit | FLOAT | Gross profit |
| unique_customers | INT | Distinct buyers |
| new_customers | INT | First-time buyers |
| repeat_customers | INT | Returning buyers |
| orders_returned | INT | Returned orders |
| orders_cancelled | INT | Cancelled orders |
| avg_order_value | FLOAT | Revenue / Orders |
| return_rate | FLOAT | Returns / Orders |

#### `fct_monthly_revenue`
**Description:** Monthly revenue with growth metrics

| Column | Type | Description |
|--------|------|-------------|
| order_month | TIMESTAMP | Month (first of month) |
| total_orders | INT | Monthly orders |
| total_revenue | FLOAT | Monthly revenue |
| total_profit | FLOAT | Monthly profit |
| new_customers | INT | New customer count |
| active_days | INT | Days with orders |
| prev_month_revenue | FLOAT | Prior month revenue |
| prev_year_revenue | FLOAT | Same month last year |
| mom_growth_pct | FLOAT | Month-over-month growth |
| yoy_growth_pct | FLOAT | Year-over-year growth |
| cumulative_revenue_ytd | FLOAT | Running total |

#### `fct_cohort_revenue`
**Description:** Revenue contribution by customer cohort

| Column | Type | Description |
|--------|------|-------------|
| signup_cohort | DATE | Customer cohort |
| order_month | DATE | Activity month |
| months_since_signup | INT | Cohort age |
| active_customers | INT | Customers who ordered |
| total_orders | INT | Order count |
| total_revenue | FLOAT | Revenue from cohort |
| revenue_per_active_user | FLOAT | ARPU |

#### `fct_geography_revenue`
**Description:** Revenue by country and month

| Column | Type | Description |
|--------|------|-------------|
| country | STRING | Country |
| order_month | TIMESTAMP | Month |
| total_orders | INT | Orders |
| total_revenue | FLOAT | Revenue |
| total_customers | INT | Unique customers |
| avg_order_value | FLOAT | AOV |
| country_rank | INT | Revenue rank |

---

### Operations Analytics (`marts/operations/`)

#### `fct_fulfillment`
**Description:** Order-level fulfillment timing

| Column | Type | Description |
|--------|------|-------------|
| order_id | INT | Primary key |
| user_id | INT | Customer |
| status | STRING | Current status |
| total_revenue | FLOAT | Order value |
| item_count | INT | Items |
| created_at | TIMESTAMP | Order placed |
| shipped_at | TIMESTAMP | Order shipped |
| delivered_at | TIMESTAMP | Order delivered |
| processing_hours | INT | Created → Shipped |
| shipping_hours | INT | Shipped → Delivered |
| total_fulfillment_hours | INT | Created → Delivered |
| is_shipped_same_day | BOOL | Same-day ship flag |
| is_delivered_within_3_days | BOOL | 3-day delivery flag |
| is_delivered_within_7_days | BOOL | 7-day delivery flag |

#### `fct_fulfillment_summary`
**Description:** Monthly fulfillment SLA performance

| Column | Type | Description |
|--------|------|-------------|
| order_month | TIMESTAMP | Month |
| total_orders | INT | Orders shipped |
| avg_processing_hours | FLOAT | Avg time to ship |
| avg_shipping_hours | FLOAT | Avg transit time |
| avg_total_hours | FLOAT | Avg total fulfillment |
| pct_shipped_same_day | FLOAT | Same-day ship rate |
| pct_delivered_3_days | FLOAT | 3-day delivery rate |
| pct_delivered_7_days | FLOAT | 7-day delivery rate |

#### `fct_returns`
**Description:** Product-level return analysis

| Column | Type | Description |
|--------|------|-------------|
| product_id | INT | Primary key |
| product_name | STRING | Name |
| category | STRING | Category |
| total_units_sold | INT | Units sold |
| total_units_returned | INT | Units returned |
| return_rate | FLOAT | Returns / Sold |
| revenue_lost_to_returns | FLOAT | Return value |

#### `fct_order_status`
**Description:** Order status distribution over time

| Column | Type | Description |
|--------|------|-------------|
| order_month | TIMESTAMP | Month |
| order_status | STRING | Status |
| order_count | INT | Count |
| total_revenue | FLOAT | Revenue |
| pct_of_month | FLOAT | Share of month's orders |

---

### Web Analytics (`marts/web/`)

#### `fct_sessions`
**Description:** Web session-level metrics

| Column | Type | Description |
|--------|------|-------------|
| session_id | STRING | Primary key |
| user_id | INT | User (if logged in) |
| traffic_source | STRING | Acquisition source |
| browser | STRING | Browser type |
| session_start_at | TIMESTAMP | Session start |
| session_end_at | TIMESTAMP | Session end |
| session_duration_seconds | INT | Duration |
| page_views | INT | Page view count |
| event_count | INT | Total events |
| has_cart | BOOL | Added to cart |
| has_purchase | BOOL | Completed purchase |

#### `fct_web_funnel`
**Description:** Daily conversion funnel by traffic source

| Column | Type | Description |
|--------|------|-------------|
| event_date | DATE | Date |
| traffic_source | STRING | Source |
| total_sessions | INT | Session count |
| sessions_with_product_view | INT | Viewed products |
| sessions_with_cart | INT | Added to cart |
| sessions_with_purchase | INT | Purchased |
| avg_session_duration | FLOAT | Avg duration |
| product_view_rate | FLOAT | View / Sessions |
| cart_rate | FLOAT | Cart / Sessions |
| purchase_rate | FLOAT | Purchase / Sessions |
| cart_to_purchase_rate | FLOAT | Purchase / Cart |

#### `fct_traffic_source_performance`
**Description:** Customer acquisition by channel

| Column | Type | Description |
|--------|------|-------------|
| traffic_source | STRING | Primary key |
| total_users | INT | Users acquired |
| total_orders | INT | Orders from source |
| total_revenue | FLOAT | Revenue |
| conversion_rate | FLOAT | Orders / Users |
| avg_ltv | FLOAT | Avg customer lifetime value |

#### `fct_browser_performance`
**Description:** Technical performance by browser

| Column | Type | Description |
|--------|------|-------------|
| browser | STRING | Browser name |
| total_sessions | INT | Sessions |
| avg_session_duration | FLOAT | Engagement |
| conversion_rate | FLOAT | Purchase rate |
| total_revenue | FLOAT | Revenue |

---

## Metrics Dictionary

### Revenue Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Total Revenue** | SUM(sale_price) | Gross sales amount |
| **Total Profit** | SUM(sale_price - cost) | Gross margin |
| **Average Order Value (AOV)** | Total Revenue / Total Orders | Revenue per transaction |
| **MoM Growth %** | (This Month - Last Month) / Last Month | Monthly growth rate |
| **YoY Growth %** | (This Month - Same Month LY) / Same Month LY | Annual growth rate |

### Customer Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Customer Lifetime Value (LTV)** | Total Revenue per User | All-time customer value |
| **Recency** | DATEDIFF(TODAY, Last Order Date) | Days since last purchase |
| **Frequency** | COUNT(Orders) | Total order count |
| **Monetary** | SUM(Revenue) | Total spend |
| **Customer Lifespan** | Last Order - First Order | Active duration |
| **Repeat Customer Rate** | Repeat Customers / Total | % returning buyers |

### Product Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Return Rate** | Items Returned / Items Sold | Product quality indicator |
| **Support** | Co-occurrences / Total Orders | Basket frequency |
| **Confidence** | Co-occurrences / Product Orders | Association strength |
| **Lift** | Support / (P(A) × P(B)) | Association significance |

### Operations Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Processing Time** | Shipped At - Created At | Order-to-ship duration |
| **Shipping Time** | Delivered At - Shipped At | In-transit duration |
| **Same-Day Ship Rate** | Same Day Ships / Total | Fulfillment efficiency |
| **On-Time Delivery Rate** | Within SLA / Total | Delivery performance |

### Web Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Session Duration** | Session End - Session Start | Engagement depth |
| **Product View Rate** | Sessions with View / Total | Browse engagement |
| **Cart Rate** | Sessions with Cart / Total | Add-to-cart rate |
| **Purchase Rate** | Sessions with Purchase / Total | Conversion rate |
| **Cart Abandonment** | 1 - (Purchase / Cart) | Lost conversions |

---

## API Reference

### Base URL
```
https://semantic-api-5592650460.us-central1.run.app
```

### Endpoints

#### Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "ok",
  "service": "Retail Semantic NLQ API",
  "model": "gemini-2.5-flash",
  "dataset": "retail_marts_dev",
  "clients_initialized": true
}
```

#### Get Schema
```http
GET /schema
```

**Response:**
```json
{
  "tables": {
    "customers": ["fct_customer_orders", "fct_rfm_scores", "fct_customer_retention"],
    "products": ["fct_product_performance", "fct_product_affinity", "fct_category_performance"],
    "revenue": ["fct_daily_revenue", "fct_monthly_revenue", "fct_geography_revenue"],
    "operations": ["fct_fulfillment_summary", "fct_returns"],
    "web": ["fct_web_funnel", "fct_traffic_source_performance"]
  }
}
```

#### Ask Question (with execution)
```http
POST /ask
Content-Type: application/json

{
  "query": "What was our revenue last month?",
  "execute": true
}
```

**Response:**
```json
{
  "original_query": "What was our revenue last month?",
  "intent": "analyze_monthly_revenue",
  "table_used": "fct_monthly_revenue",
  "sql": "SELECT order_month, total_revenue FROM `semantic-layer-484020.retail_marts_dev.fct_monthly_revenue` ORDER BY order_month DESC LIMIT 1",
  "explanation": "Querying monthly fact table for the most recent completed month.",
  "data": [
    {"order_month": "2024-01-01", "total_revenue": 542891.23}
  ],
  "row_count": 1,
  "error": null
}
```

#### SQL Only (no execution)
```http
POST /sql-only
Content-Type: application/json

{
  "query": "Show me top selling products"
}
```

**Response:** Same structure but `data` and `row_count` will be null.

---

## Natural Language Query (NLQ) System

### How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NLQ PROCESSING FLOW                          │
└─────────────────────────────────────────────────────────────────────┘

   User Question                    "What are our top 10 products by revenue?"
         │
         ▼
┌─────────────────────┐
│   PROMPT ASSEMBLY   │   System prompt + Schema context + User question
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   GEMINI 2.5 FLASH  │   LLM generates structured JSON response
│   (temperature=0.1) │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   JSON PARSING      │   Extract: intent, table, SQL, explanation
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   QUERY EXECUTION   │   Run SQL against BigQuery
│   (if execute=true) │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   RESPONSE FORMAT   │   Return structured NLQResponse
└─────────────────────┘
         │
         ▼
   Data + Explanation              { data: [...], explanation: "..." }
```

### Example Queries

| Natural Language | Generated SQL | Table Used |
|------------------|---------------|------------|
| "What was our revenue last month?" | `SELECT total_revenue FROM fct_monthly_revenue ORDER BY order_month DESC LIMIT 1` | fct_monthly_revenue |
| "Show me customers in the Champions segment" | `SELECT * FROM fct_rfm_scores WHERE rfm_segment = 'Champions'` | fct_rfm_scores |
| "Which products have the highest return rate?" | `SELECT product_name, return_rate FROM fct_product_performance ORDER BY return_rate DESC` | fct_product_performance |
| "What's our conversion rate by traffic source?" | `SELECT traffic_source, purchase_rate FROM fct_web_funnel` | fct_web_funnel |

### LLM Prompt Engineering

The system prompt includes:

1. **Role Assignment:**
   > "You are an expert analytics engineer and SQL developer..."

2. **Schema Context:** Complete table list with columns and descriptions

3. **Business Rules:**
   - Table selection logic (use pre-aggregated marts)
   - Date handling (TIMESTAMP vs DATE casting)
   - Default aggregation behavior
   - Row limits (100 by default)

4. **Output Format:** Strict JSON schema with examples

5. **Few-shot Examples:** 3-5 sample Q&A pairs demonstrating expected behavior

---

## Deployment Architecture

### Cloud Run Services

```
┌─────────────────────────────────────────────────────────────────────┐
│                      GOOGLE CLOUD PLATFORM                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Cloud Run (API)                           │   │
│  │  semantic-api-5592650460.us-central1.run.app                 │   │
│  │                                                              │   │
│  │  • FastAPI application                                       │   │
│  │  • Auto-scaling (0 to N instances)                           │   │
│  │  • HTTPS/TLS termination                                     │   │
│  │  • IAM authentication                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              │ Vertex AI API                        │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Vertex AI                                 │   │
│  │                                                              │   │
│  │  • Gemini 2.5 Flash model                                    │   │
│  │  • Managed inference                                         │   │
│  │  • us-central1 region                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              │ BigQuery API                         │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    BigQuery                                  │   │
│  │                                                              │   │
│  │  Project: semantic-layer-484020                              │   │
│  │  Dataset: retail_marts_dev                                   │   │
│  │                                                              │   │
│  │  • dbt-managed tables/views                                  │   │
│  │  • Columnar storage                                          │   │
│  │  • Auto-scaling query execution                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Local Development

```bash
# 1. Install dependencies
pip install dbt-bigquery

# 2. Configure dbt profile (~/.dbt/profiles.yml)
# 3. Authenticate with Google Cloud
gcloud auth application-default login

# 4. Run dbt models
cd semantic-layer-dbt
dbt run

# 5. Start API locally
cd api
pip install -r requirements.txt
uvicorn main:app --reload

# 6. Start UI locally
cd ui
pip install -r requirements.txt
streamlit run app.py
```

---

## Security & Governance

### Data Access Control

| Layer | Access Pattern | Authentication |
|-------|----------------|----------------|
| BigQuery (raw) | Internal only | Service account |
| BigQuery (marts) | Internal + API | Service account |
| BigQuery (public_demo) | External tools | Restricted views |
| API | Authenticated | Cloud Run IAM |
| UI | Public | API passthrough |

### PII Handling

The semantic layer (`models/semantic/`) removes or masks PII:

- **Email:** Hashed or removed
- **Names:** Removed from public views
- **Addresses:** Aggregated to country level

### Query Governance

1. **Row Limits:** API enforces 100-row limit on responses
2. **Table Whitelist:** LLM can only access documented marts
3. **Query Timeout:** 30-second timeout on BigQuery queries
4. **Audit Logging:** All queries logged with user context

---

## Appendix

### File Structure

```
semantic-layer-dbt/
├── api/
│   ├── main.py              # FastAPI application
│   ├── prompts.py           # LLM system prompts
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Container definition
│
├── ui/
│   ├── app.py               # Streamlit dashboard
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Container definition
│
├── models/
│   ├── staging/             # Source-aligned views
│   ├── intermediate/        # Denormalized tables
│   ├── marts/               # Business-ready analytics
│   │   ├── core/            # Dimensions & base facts
│   │   ├── customers/       # Customer analytics
│   │   ├── products/        # Product analytics
│   │   ├── revenue/         # Financial analytics
│   │   ├── operations/      # Ops analytics
│   │   └── web/             # Digital analytics
│   └── semantic/            # External exposure layer
│
├── cube/
│   └── model/cubes/         # Cube.js semantic definitions
│
├── dbt_project.yml          # dbt configuration
└── docs/
    └── PROJECT_ARCHITECTURE.md  # This document
```

### Glossary

| Term | Definition |
|------|------------|
| **AOV** | Average Order Value |
| **ARPU** | Average Revenue Per User |
| **CLV/LTV** | Customer Lifetime Value |
| **Cohort** | Group of users with shared characteristic (e.g., signup month) |
| **dbt** | Data Build Tool - transformation framework |
| **Grain** | The level of detail in a table (e.g., order, user, day) |
| **Mart** | Business-ready data model optimized for analytics |
| **MoM** | Month-over-Month |
| **NLQ** | Natural Language Query |
| **RFM** | Recency, Frequency, Monetary - customer segmentation |
| **YoY** | Year-over-Year |

---

*Document Version: 1.0*  
*Last Updated: January 2026*
