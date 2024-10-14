#!/bin/sh

# Enable strict error handling
set -e

# Function to log messages
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Create directory for SSL certificates
log "Creating directory for SSL certificates..."
mkdir -p /etc/nginx/ssl
if [ $? -eq 0 ]; then
    log "Directory /etc/nginx/ssl created successfully."
else
    log "Failed to create directory /etc/nginx/ssl!"
    exit 1
fi

# Generate self-signed certificate
log "Generating self-signed certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/privkey.pem \
    -out /etc/nginx/ssl/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Check if the files were created successfully
if [ -f /etc/nginx/ssl/privkey.pem ] && [ -f /etc/nginx/ssl/fullchain.pem ]; then
    log "Certificates generated successfully."
else
    log "Failed to generate certificates!"
    exit 1
fi

# Set appropriate permissions
log "Setting permissions for certificates..."
chmod 644 /etc/nginx/ssl/fullchain.pem
chmod 644 /etc/nginx/ssl/privkey.pem

# Verify permissions were applied
if [ "$(stat -c "%a" /etc/nginx/ssl/fullchain.pem)" = "644" ] && \
   [ "$(stat -c "%a" /etc/nginx/ssl/privkey.pem)" = "644" ]; then
    log "Permissions set successfully."
else
    log "Failed to set permissions for certificates!"
    exit 1
fi

log "Certificate generation and setup completed successfully."
