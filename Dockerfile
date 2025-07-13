# syntax=docker/dockerfile:1

### Build stage to install PHP dependencies
FROM composer:2 AS build
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --prefer-dist --no-progress --no-suggest

### Runtime image
FROM php:8.1-fpm-alpine
LABEL maintainer="Presidio UI"

# Install runtime packages, including envsubst from gettext
RUN apk add --no-cache nginx curl bash gettext

WORKDIR /app

# Copy PHP dependencies from the build stage
COPY --from=build /app/vendor ./vendor
COPY composer.json composer.lock ./

# Copy application code
COPY public ./public
COPY src ./src

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
