# Final Image
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN apk add --no-cache \
    nginx \
    bash \
    && mkdir -p /run/nginx

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip3 install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy pre-built frontend assets
COPY frontend/dist /usr/share/nginx/html

# Copy rootfs and scripts
COPY rootfs/nginx.conf /etc/nginx.conf
COPY run.sh /

# Set permissions
RUN chmod a+x /run.sh

# Labels
LABEL \
    io.hass.name="WaterMe" \
    io.hass.description="Advanced Irrigation System for Home Assistant" \
    io.hass.type="addon" \
    io.hass.version="0.1.5"

CMD [ "/run.sh" ]
