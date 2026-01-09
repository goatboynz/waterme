#!/bin/bash
set -e

echo "Starting WaterMe Addon..."

# Start Nginx in background
nginx

# Start Backend
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8080
