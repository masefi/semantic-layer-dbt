# Cube Semantic Layer

This directory contains the data models for Cube.

## Setup

1. **Install Cube CLI** (requires Docker/Node.js)
   ```bash
   npm install -g cubejs-cli
   ```

2. **Configure Credentials**
   Create a `.env` file in this directory:
   ```env
   CUBEJS_DB_TYPE=bigquery
   CUBEJS_DB_BQ_PROJECT_ID=semantic-layer-484020
   CUBEJS_DB_BQ_KEY_FILE=/path/to/key.json
   ```

3. **Run Cube**
   ```bash
   cubejs dev
   ```

## Models
- `orders`: Order-level metrics (revenue, count, average value)
- `users`: User demographics and totals
- `revenue_daily`: Pre-aggregated daily trend metrics
