FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Cloud Run uses PORT env variable
ENV PORT=8501
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Run command - use shell form to expand $PORT
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true
