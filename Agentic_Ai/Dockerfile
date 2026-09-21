# ============================================================
# Agentic AI Orchestration Service — Dockerfile
# Port: 8001 | FastAPI + LangGraph + Uvicorn
# ============================================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8001

# Run the walletrace FastAPI app on port 8001
CMD ["uvicorn", "walletrace.api:app", "--host", "0.0.0.0", "--port", "8001"]
