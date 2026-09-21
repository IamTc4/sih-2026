# ============================================================
# Dashboard — Multi-Stage Dockerfile
# Stage 1: Build React + Vite app
# Stage 2: Serve with Nginx (+ reverse proxy to backends)
# ============================================================

# ---- Stage 1: Build ----
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies first for layer caching
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

# Copy source and build
COPY . .
RUN npm run build

# ---- Stage 2: Serve with Nginx ----
FROM nginx:1.27-alpine AS production

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config with reverse proxy rules
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
