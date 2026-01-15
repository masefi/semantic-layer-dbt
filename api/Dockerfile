FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Environment defaults
ENV PORT=8080
ENV GCP_PROJECT_ID=semantic-layer-484020
ENV BQ_DATASET=retail_marts_dev

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
