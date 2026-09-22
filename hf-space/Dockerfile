# ============================================================
# CryptoSentinel — Hugging Face Spaces Deployment
# Single container running all 5 services via supervisord
# nginx on port 7860 proxies to all backend services
# ============================================================

# ── Stage 1: Build React Dashboard ──────────────────────────
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend

# Install deps (cached layer)
COPY Dashboard/package*.json ./
RUN npm ci --prefer-offline

# Build production React app
COPY Dashboard/ ./
RUN npm run build

# ── Stage 2: Combined Python Runtime + Nginx + Supervisor ───
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system packages: nginx + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Install ALL Python deps (merged from all 4 services) ────
COPY hf-space/requirements-all.txt /tmp/requirements-all.txt
RUN pip install --no-cache-dir -r /tmp/requirements-all.txt

# ── Copy all backend service code ───────────────────────────
COPY blockchain/    /app/blockchain/
COPY Agentic_Ai/    /app/agentic_ai/
COPY ML/            /app/ml_service/
COPY Cybersecurity/ /app/cybersecurity/

# ── Copy React build to nginx html dir ─────────────────────
COPY --from=frontend-builder /frontend/dist /usr/share/nginx/html

# ── Copy nginx config (listens on 7860, proxies to backends) ─
COPY hf-space/nginx.conf /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/sites-enabled/default.conf 2>/dev/null || true

# ── Copy supervisord config ─────────────────────────────────
COPY hf-space/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log dirs
RUN mkdir -p /var/log/supervisor /var/log/nginx /tmp/nginx \
    && chown -R www-data:www-data /var/log/nginx

# HF Spaces standard port
EXPOSE 7860

# Supervisord manages all processes
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
