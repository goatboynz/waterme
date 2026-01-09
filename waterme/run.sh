#!/usr/bin/with-contenv bashio

bashio::log.info "Starting WaterMe Irrigation Addon..."

# Start Nginx in background
bashio::log.info "Starting Nginx..."
nginx -g "daemon off;" &

# Start Backend
bashio::log.info "Starting FastAPI Backend..."
cd /app/backend
exec uvicorn main:app --host 0.0.0.0 --port 8080
