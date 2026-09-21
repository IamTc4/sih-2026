# ============================================================
# Cybersecurity & Threat Intelligence Service — Dockerfile
# Port: 8003 | FastAPI + Uvicorn
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

# Ensure the evidence DB directory is writable by appuser
RUN chown appuser:appgroup /app

USER appuser

EXPOSE 8003

# Run the Cybersecurity FastAPI app on port 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
