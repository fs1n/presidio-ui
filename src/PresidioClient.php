<?php
namespace App;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

class PresidioClient
{
    private Client $analyzerClient;
    private Client $anonymizerClient;
    private ?string $analyzerKey;
    private ?string $anonymizerKey;

    public function __construct(
        string $analyzerUrl,
        string $anonymizerUrl,
        ?string $analyzerKey = null,
        ?string $anonymizerKey = null
    ) {
        $this->analyzerClient = new Client([
            'base_uri' => rtrim($analyzerUrl, '/'),
            'timeout'  => 10,
        ]);
        $this->anonymizerClient = new Client([
            'base_uri' => rtrim($anonymizerUrl, '/'),
            'timeout'  => 10,
        ]);
        $this->analyzerKey = $analyzerKey;
        $this->anonymizerKey = $anonymizerKey;
    }

    private function buildHeaders(?string $key): array
    {
        $headers = ['Content-Type' => 'application/json'];
        if ($key) {
            $headers['Authorization'] = 'Bearer ' . $key;
        }
        return $headers;
    }

    /**
     * Call the Presidio analyzer and return the results array.
     *
     * @param string $text
     * @param array $options Additional options like entities or score_threshold
     * @return array
     * @throws GuzzleException
     */
    public function analyze(string $text, array $options = []): array
    {
        $body = array_merge([
            'text' => $text,
            'language' => 'en',
        ], $options);

        $response = $this->analyzerClient->post('/analyze', [
            'headers' => $this->buildHeaders($this->analyzerKey),
            'json'    => $body,
        ]);

        return json_decode($response->getBody()->getContents(), true) ?? [];
    }

    /**
     * Send analyzer results to the anonymizer service and return the anonymized text.
     *
     * @param string $text
     * @param array $analyzerResults Results from the analyze() call
     * @param array $anonymizers Optional anonymizer configuration
     * @return string
     * @throws GuzzleException
     */
    public function anonymize(string $text, array $analyzerResults, array $anonymizers = []): string
    {
        $body = [
            'text' => $text,
            'analyzer_results' => $analyzerResults,
        ];
        if (!empty($anonymizers)) {
            $body['anonymizers'] = $anonymizers;
        }

        $response = $this->anonymizerClient->post('/anonymize', [
            'headers' => $this->buildHeaders($this->anonymizerKey),
            'json'    => $body,
        ]);

        $result = json_decode($response->getBody()->getContents(), true);
        return $result['text'] ?? '';
    }

    /**
     * Convenience method to analyze and immediately anonymize text.
     */
    public function analyzeAndAnonymize(string $text, array $options = []): string
    {
        $analysis = $this->analyze($text, $options);
        return $this->anonymize($text, $analysis);
    }
}
