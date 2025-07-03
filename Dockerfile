# syntax=docker/dockerfile:1
FROM php:8.1-fpm-alpine AS base

LABEL maintainer="Presidio UI"

# Install system packages
RUN apk add --no-cache nginx curl bash

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer

WORKDIR /app

# Copy dependency definitions
COPY composer.json composer.lock ./

# Install PHP dependencies
RUN composer install --no-dev --prefer-dist --no-progress --no-suggest \
    && rm -rf /root/.composer

# Copy application code
COPY public ./public
COPY src ./src
COPY presidio-api-docs.yml ./

# Setup nginx configuration template
RUN mkdir -p /etc/nginx/templates /etc/nginx/conf.d /run/nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/default.conf.template /etc/nginx/templates/default.conf.template

# Copy entrypoint
COPY docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Default environment variables
ENV PORT=8080 \
    PRESIDIO_ANALYZER_API_URL=http://localhost:5002 \
    PRESIDIO_ANONYMIZER_API_URL=http://localhost:5001

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD curl -f http://localhost:${PORT}/ || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["php-fpm", "-F"]
