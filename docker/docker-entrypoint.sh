#!/bin/sh
set -e

# Substitute env vars in nginx template
envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Start PHP-FPM in the background
php-fpm -D

# Run nginx in the foreground
exec nginx -g 'daemon off;'
