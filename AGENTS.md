This repository uses PHP for a small web application.
After making changes, attempt to run `composer install` and `php -l <file>` to check syntax if the commands are available. If those commands fail due to missing programs, mention it in the PR testing notes.

## Project structure

- `public/` – web entry point containing `index.php`
- `src/` – PHP classes such as `PresidioClient`
- `presidio-api-docs.yml` – OpenAPI specification for the analyzer and anonymizer APIs
- `composer.json` – dependency definitions