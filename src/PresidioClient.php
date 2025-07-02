<?php
namespace App;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

class PresidioClient
{
    private $client;
    private $apiUrl;
    private $apiKey;

    public function __construct(string $apiUrl, ?string $apiKey = null)
    {
        $this->apiUrl = rtrim($apiUrl, '/');
        $this->apiKey = $apiKey;
        $this->client = new Client([
            'base_uri' => $this->apiUrl,
            'timeout'  => 10,
        ]);
    }

    /**
     * Analyze and anonymize text using Presidio.
     *
     * @param string $text Input text
     * @param array $options Additional options like entities, score threshold
     * @return string Anonymized text
     * @throws GuzzleException
     */
    public function anonymize(string $text, array $options = []): string
    {
        $headers = ['Content-Type' => 'application/json'];
        if ($this->apiKey) {
            $headers['Authorization'] = 'Bearer ' . $this->apiKey;
        }

        $body = array_merge([
            'text' => $text,
        ], $options);

        $response = $this->client->post('/analyze', [
            'headers' => $headers,
            'json' => $body,
        ]);

        $result = json_decode($response->getBody()->getContents(), true);
        return $result['result'] ?? '';
    }
}
