# Retail Semantic Layer NLQ API 🧠

An intelligent natural language query engine powered by **Gemini 2.5 Flash** and **BigQuery**.

## 🚀 Capabilities

Translates plain English questions into optimized SQL queries against the dbt Semantic Layer.

**Example Questions:**
* "What was our total revenue last month?"
* "Show me top 10 products by return rate"
* "How are the Champions segment customers performing?"
* "What is the retention rate for the January 2024 cohort?"

## 🛠️ Setup

### Prerequisites
* Google Cloud Project with Vertex AI enabled
* Service Account with `BigQuery Job User` and `Vertex AI User` roles

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (if not using defaults):
```bash
export GCP_PROJECT_ID="semantic-layer-484020"
export BQ_DATASET="retail_marts_dev"
```

3. Run the server:
```bash
uvicorn main:app --reload
```

## 🔌 API Endpoints

### `POST /ask`
Main endpoint for NLQ.

**Request:**
```json
{
  "query": "Who are our top customers?",
  "execute": true
}
```

**Response:**
```json
{
  "original_query": "Who are our top customers?",
  "intent": "analyze_top_customers",
  "table_used": "fct_customer_orders",
  "sql": "SELECT ...",
  "data": [...],
  "explanation": "Querying customer orders fact table ordered by LTV."
}
```

### `POST /sql-only`
Returns the generated SQL without executing it (debugging).

### `GET /schema`
Returns the list of available tables and context.
