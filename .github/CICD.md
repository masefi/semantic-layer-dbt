# CI/CD Pipeline

This directory contains GitHub Actions workflows for automated deployment of the Retail Semantic Layer.

## Workflows

### 1. `deploy.yml` - Deploy Services

Deploys all services to Google Cloud Run:

| Trigger | What Happens |
|---------|--------------|
| Push to `main` | Deploys Cube → API → UI |
| Pull Request | Runs tests only |
| Manual dispatch | Choose which services to deploy |

**Pipeline:**
```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Test   │ ──▶ │ Deploy Cube │ ──▶ │ Deploy API  │ ──▶ │ Deploy UI   │
└─────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 2. `dbt.yml` - dbt CI/CD

Runs dbt on model changes:

| Trigger | What Happens |
|---------|--------------|
| PR with model changes | Compile & test in isolated dataset |
| Push to `main` with model changes | Run dbt in production dataset |
| Manual dispatch | Run with optional `--full-refresh` |

## Required Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Description | How to Get |
|--------|-------------|------------|
| `GCP_SA_KEY` | GCP Service Account JSON key | See below |
| `CUBEJS_API_SECRET` | Cube API authentication secret | Generate: `openssl rand -hex 32` |

### Creating GCP Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions" \
  --project=semantic-layer-484020

# Grant permissions
gcloud projects add-iam-policy-binding semantic-layer-484020 \
  --member="serviceAccount:github-actions@semantic-layer-484020.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding semantic-layer-484020 \
  --member="serviceAccount:github-actions@semantic-layer-484020.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding semantic-layer-484020 \
  --member="serviceAccount:github-actions@semantic-layer-484020.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding semantic-layer-484020 \
  --member="serviceAccount:github-actions@semantic-layer-484020.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create github-sa-key.json \
  --iam-account=github-actions@semantic-layer-484020.iam.gserviceaccount.com

# Copy contents of github-sa-key.json to GitHub secret GCP_SA_KEY
cat github-sa-key.json
```

## Manual Deployment

To deploy manually from GitHub:

1. Go to **Actions** tab
2. Select **Deploy Semantic Layer**
3. Click **Run workflow**
4. Choose which services to deploy
5. Click **Run workflow**

## Environment Variables

### Cube Service
| Variable | Value |
|----------|-------|
| `CUBEJS_DB_TYPE` | bigquery |
| `CUBEJS_DB_BQ_PROJECT_ID` | semantic-layer-484020 |
| `CUBEJS_API_SECRET` | (from secret) |

### API Service
| Variable | Value |
|----------|-------|
| `GCP_PROJECT_ID` | semantic-layer-484020 |
| `BQ_DATASET` | retail_marts_dev |
| `CUBE_API_URL` | (auto-discovered) |
| `CUBEJS_API_SECRET` | (from secret) |

### UI Service
| Variable | Value |
|----------|-------|
| `API_URL` | (auto-discovered) |

## Deployment Order

Services must be deployed in order due to dependencies:

```
1. Cube   (no dependencies)
      ↓
2. API    (depends on Cube URL)
      ↓
3. UI     (depends on API URL)
```

The workflow handles this automatically by passing outputs between jobs.

## Monitoring

After deployment, verify services:

```bash
# Check all services
gcloud run services list --region=us-central1

# Check specific service logs
gcloud run logs read semantic-api --region=us-central1 --limit=50
```
