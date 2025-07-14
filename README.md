# Presidio UI

This repository provides a minimal PHP web interface for text anonymization using [Microsoft Presidio](https://microsoft.github.io/presidio/). The application uses the [Tabler](https://tabler.io/) UI kit for styling.

[![Build and publish Docker image](https://github.com/fs1n/presidio-ui/actions/workflows/publish.yml/badge.svg)](https://github.com/fs1n/presidio-ui/actions/workflows/publish.yml)

## Features

- Side‑by‑side text areas for input and anonymized output
- Optional advanced settings panel to pass entity types and score threshold
- Configurable Presidio Analyzer and Anonymizer endpoints via `.env`
- Basic error handling
- New *File PII* tab to anonymize uploaded documents

![Screenshot of the application UI - Data Fictional!!](https://github.com/user-attachments/assets/c2cd4d14-6735-4862-bb32-df3ba6aad24d)
*Screenshot of the application UI - Data Fictional!!*

## Quick Start

The UI requires running Presidio's analyzer and anonymizer services. You can
start them using Docker:

```bash
# Download Docker images for presidio
docker pull mcr.microsoft.com/presidio-analyzer
docker pull mcr.microsoft.com/presidio-anonymizer

# Run containers with default ports
docker run -d -p 5002:3000 mcr.microsoft.com/presidio-analyzer:latest
docker run -d -p 5001:3000 mcr.microsoft.com/presidio-anonymizer:latest
```

### Docker `run`

Build and run the UI container directly:

```bash
docker build -t presidio-ui .
docker run -p 8080:8080 \
  -e PRESIDIO_ANALYZER_API_URL=http://localhost:5002 \
  -e PRESIDIO_ANONYMIZER_API_URL=http://localhost:5001 \
  presidio-ui
```

### Docker Compose

Alternatively use `docker-compose` which exposes the same environment
variables:

```bash
docker-compose up --build
```

The application will then be available on [http://localhost:8080](http://localhost:8080).

## Environment Variables

The container recognizes the following variables which can also be placed in a
`.env` file or passed via `docker run -e`/`docker-compose`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port the container listens on |
| `PRESIDIO_ANALYZER_API_URL` | `http://localhost:5002` | URL of the Presidio analyzer service |
| `PRESIDIO_ANALYZER_API_KEY` | *(empty)* | Optional API key for analyzer |
| `PRESIDIO_ANONYMIZER_API_URL` | `http://localhost:5001` | URL of the Presidio anonymizer service |
| `PRESIDIO_ANONYMIZER_API_KEY` | *(empty)* | Optional API key for anonymizer |

## Build Instructions

Build the container for the current architecture:

```bash
docker build -t presidio-ui .
```

To create a multi-architecture image (e.g., `amd64` and `arm64`) use Docker
Buildx:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t presidio-ui:latest .
```

## Usage

Paste text into the left area, adjust settings if desired and click **Anonymize**. The right area will display Presidio’s anonymized output.

## Disclaimer

The anonymization features in this UI leverage components from the [Microsoft Presidio](https://github.com/microsoft/presidio/) project. These components are included for convenience and are not affiliated with or endorsed by this repository's maintainer. You are solely responsible for verifying that all sensitive information has been removed from your text. The maintainer accepts no liability for any errors in the anonymization process or for any resulting damages.
