# =========================================================================
# SlothFeed Production Container Dockerfile
# Optimized for Render Web Service and Background Worker Deployments
# =========================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000 \
    GEMMA_MODEL_NAME=gemma-2-2b-it

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose Render default port
EXPOSE 10000

# Health check to ensure service vitality
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Launch uvicorn web service bound to 0.0.0.0 and dynamically assigned PORT
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT}"]
