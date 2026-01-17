# Cube.js Cloud Run Deployment
FROM cubejs/cube:latest

# Set working directory
WORKDIR /cube/conf

# Copy configuration and model files
COPY cube.yaml .
COPY model/ ./model/

# Environment variables (set via Cloud Run)
ENV CUBEJS_DB_TYPE=bigquery
ENV CUBEJS_DEV_MODE=false
ENV CUBEJS_CACHE_AND_QUEUE_DRIVER=memory
ENV CUBEJS_TELEMETRY=false

# Cloud Run uses PORT env variable (Cube listens on 4000 by default)
ENV PORT=4000
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:4000/readyz || exit 1
