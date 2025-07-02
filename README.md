# Presidio UI

This repository provides a minimal PHP web interface for text anonymization using [Microsoft Presidio](https://microsoft.github.io/presidio/). The application uses the [Tabler](https://tabler.io/) UI kit for styling and communicates with a Presidio REST API.

## Features

- Side‑by‑side text areas for input and anonymized output
- Optional advanced settings panel to pass entity types and score threshold
- Configurable Presidio Analyzer and Anonymizer endpoints via `.env`
- Basic error handling and clean code structure

## Quick Start

The UI requires running Presidio's analyzer and anonymizer services. You can
start them using Docker:

```bash
docker pull mcr.microsoft.com/presidio-analyzer
docker pull mcr.microsoft.com/presidio-anonymizer

docker run -p 5002:5002 ghcr.io/microsoft/presidio-analyzer:latest
docker run -p 5001:5001 ghcr.io/microsoft/presidio-anonymizer:latest
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

## Notes

This code is intended as a simple starting point. Extend the `PresidioClient` class and the front‑end form to expose additional Presidio capabilities as needed.
