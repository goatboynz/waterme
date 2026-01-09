# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Final Image
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt
COPY backend/ ./backend/

# Copy frontend build to nginx
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy nginx config
COPY rootfs/etc/nginx/nginx.conf /etc/nginx/nginx.conf

# Entrypoint script
COPY rootfs/usr/bin/run.sh /usr/bin/run.sh
RUN chmod +x /usr/bin/run.sh

CMD ["/usr/bin/run.sh"]
