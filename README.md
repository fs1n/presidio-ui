# Presidio UI

This repository provides a minimal PHP web interface for text anonymization using [Microsoft Presidio](https://microsoft.github.io/presidio/). The application uses the [Tabler](https://tabler.io/) UI kit for styling and communicates with a Presidio REST API.

## Features

- Side‑by‑side text areas for input and anonymized output
- Optional advanced settings panel to pass entity types and score threshold
- Configurable Presidio Analyzer and Anonymizer endpoints via `.env`
- Basic error handling and clean code structure

## Getting Started

### Requirements

- PHP 8.1+ and Composer
- Docker (for running Presidio locally)

### Setup

1. **Install dependencies**

   ```bash
   composer install
   ```

2. **Copy the environment template**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` to set `PRESIDIO_ANALYZER_API_URL` and `PRESIDIO_ANONYMIZER_API_URL` (and API keys if needed).

3. **Run Presidio via Docker**

   ```bash
   docker run -p 5002:5002 ghcr.io/microsoft/presidio-anonymizer:latest
   ```

   By default the app expects the analyzer on `http://localhost:5002` and the anonymizer on `http://localhost:5001`.

4. **Start the PHP development server**

   ```bash
   php -S localhost:8000 -t public
   ```

5. **Open the application**

   Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

Paste text into the left area, adjust settings if desired and click **Anonymize**. The right area will display Presidio’s anonymized output.

## Notes

This code is intended as a simple starting point. Extend the `PresidioClient` class and the front‑end form to expose additional Presidio capabilities as needed.
