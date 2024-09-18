#!/bin/bash

# Create directory for SSL certificates
mkdir -p /etc/nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/privkey.pem \
    -out /etc/nginx/ssl/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set appropriate permissions
chmod 644 /etc/nginx/ssl/fullchain.pem
chmod 644 /etc/nginx/ssl/privkey.pem