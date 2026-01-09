# Final Image
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip3 install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy pre-built frontend assets
COPY frontend/dist /usr/share/nginx/html

# Copy rootfs (S6 services and configs)
COPY rootfs /

# Labeling
LABEL \
    io.hass.name="WaterMe" \
    io.hass.description="Advanced Irrigation System for Home Assistant" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="0.1.1"

# Use S6-Overlay
ENTRYPOINT ["/init"]
