<?php
require __DIR__ . '/../vendor/autoload.php';

use App\PresidioClient;
use Dotenv\Dotenv;

// Load environment variables
if (file_exists(__DIR__ . '/../.env')) {
    Dotenv::createImmutable(__DIR__ . '/../')->load();
}

$analyzerUrl = $_ENV['PRESIDIO_ANALYZER_API_URL'] ?? 'http://localhost:5002';
$anonymizerUrl = $_ENV['PRESIDIO_ANONYMIZER_API_URL'] ?? 'http://localhost:5001';
$analyzerKey = $_ENV['PRESIDIO_ANALYZER_API_KEY'] ?? null;
$anonymizerKey = $_ENV['PRESIDIO_ANONYMIZER_API_KEY'] ?? null;
$client = new PresidioClient($analyzerUrl, $anonymizerUrl, $analyzerKey, $anonymizerKey);

$error = null;
$output = '';
$input = $_POST['input_text'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        $options = [];
        // Pass additional options from form
        if (!empty($_POST['entities'])) {
            $entities = array_map('trim', explode(',', $_POST['entities']));
            $options['entities'] = array_filter($entities, static fn($e) => $e !== '');
        }
        if (isset($_POST['score']) && is_numeric(trim($_POST['score']))) {
            $options['score_threshold'] = (float) trim($_POST['score']);
        }
        $output = $client->analyzeAndAnonymize($input, $options);
    } catch (Exception $e) {
        $error = 'Error communicating with Presidio: ' . $e->getMessage();
    }
}
?>
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Presidio Anonymizer</title>
    <link href="https://unpkg.com/@tabler/core@1.0.0-beta19/dist/css/tabler.min.css" rel="stylesheet"/>
    <script src="https://unpkg.com/@tabler/core@1.0.0-beta19/dist/js/tabler.min.js"></script>
  </head>
  <body>
    <div class="page">
      <div class="page-body container-xl">
        <h2 class="mt-4">Presidio Anonymizer</h2>
        <?php if ($error): ?>
          <div class="alert alert-danger"> <?= htmlspecialchars($error) ?> </div>
        <?php endif; ?>
        <form method="POST" class="card">
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Input Text</label>
                  <textarea name="input_text" class="form-control resize-sync" rows="10" style="min-height:200px; resize:none; overflow:hidden;"><?= htmlspecialchars($input) ?></textarea>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3 position-relative">
                  <label class="form-label">Anonymized Output</label>
                  <button type="button" id="copyOutput" class="btn btn-sm btn-outline-secondary position-absolute end-0 top-0 m-2" title="Copy">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon" width="16" height="16" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                      <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                      <rect x="8" y="8" width="12" height="12" rx="2" />
                      <path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2" />
                    </svg>
                  </button>
                  <textarea class="form-control resize-sync" rows="10" style="min-height:200px; resize:none; overflow:hidden;" readonly><?= htmlspecialchars($output) ?></textarea>
                </div>
              </div>
            </div>
            <div class="mb-3">
              <a class="btn" data-bs-toggle="collapse" href="#advancedSettings" role="button" aria-expanded="false" aria-controls="advancedSettings">
                Advanced Settings
              </a>
            </div>
            <div class="collapse" id="advancedSettings">
              <div class="card card-body">
                <div class="mb-3">
                  <label class="form-label">Entity Types (comma separated)</label>
                  <input type="text" name="entities" class="form-control" placeholder="EMAIL,PHONE_NUMBER"/>
                </div>
                <div class="mb-3">
                  <label class="form-label">Minimum Likelihood Score</label>
                  <input type="number" step="0.01" name="score" class="form-control" placeholder="0.5"/>
                </div>
              </div>
            </div>
          </div>
          <div class="card-footer text-end">
            <button type="submit" class="btn btn-primary">Anonymize</button>
          </div>
        </form>
      </div>
      <footer class="footer footer-transparent mt-3">
        <div class="container-xl text-center">
          UI Made with <a href="https://tabler.io" target="_blank" rel="noopener noreferrer">Tabler</a>
        </div>
      </footer>
    </div>
    <script>
      document.addEventListener('DOMContentLoaded', function () {
        const inputArea = document.querySelector('textarea[name="input_text"]');
        const outputArea = document.querySelector('textarea[readonly]');
        const copyBtn = document.getElementById('copyOutput');

        function syncResize() {
          inputArea.style.height = 'auto';
          outputArea.style.height = 'auto';
          const maxHeight = Math.max(inputArea.scrollHeight, outputArea.scrollHeight);
          inputArea.style.height = maxHeight + 'px';
          outputArea.style.height = maxHeight + 'px';
        }

        syncResize();
        inputArea.addEventListener('input', syncResize);


        if (copyBtn) {
          copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(outputArea.value || '');
          });
        }
      });
    </script>
  </body>
</html>
