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
            $options['entities'] = array_map('trim', explode(',', $_POST['entities']));
        }
        if (!empty($_POST['score'])) {
            $options['score_threshold'] = (float) $_POST['score'];
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
                  <textarea name="input_text" class="form-control" rows="10" style="min-height:200px;"><?= htmlspecialchars($input) ?></textarea>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Anonymized Output</label>
                  <textarea class="form-control" rows="10" style="min-height:200px;" readonly><?= htmlspecialchars($output) ?></textarea>
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
          Made with <a href="https://tabler.io" target="_blank">Tabler</a>
        </div>
      </footer>
    </div>
  </body>
</html>
