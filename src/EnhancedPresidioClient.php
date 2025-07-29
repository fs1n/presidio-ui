<?php
namespace App;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

/**
 * Enhanced Presidio Client that can work with both the new Python backend
 * and the original external Presidio services for backward compatibility
 */
class EnhancedPresidioClient
{
    private Client $backendClient;
    private ?string $backendApiKey;
    private bool $useNewBackend;
    
    // Fallback to original implementation
    private ?PresidioClient $fallbackClient;

    public function __construct(
        string $backendUrl,
        ?string $backendApiKey = null,
        bool $useNewBackend = true,
        // Fallback parameters
        ?string $analyzerUrl = null,
        ?string $anonymizerUrl = null,
        ?string $analyzerKey = null,
        ?string $anonymizerKey = null
    ) {
        $this->backendClient = new Client([
            'base_uri' => rtrim($backendUrl, '/'),
            'timeout'  => 30,
        ]);
        $this->backendApiKey = $backendApiKey;
        $this->useNewBackend = $useNewBackend;
        
        // Initialize fallback client if parameters provided
        if ($analyzerUrl && $anonymizerUrl) {
            $this->fallbackClient = new PresidioClient(
                $analyzerUrl, 
                $anonymizerUrl, 
                $analyzerKey, 
                $anonymizerKey
            );
        }
    }

    /**
     * Build HTTP headers for requests.
     */
    private function buildHeaders(?string $key): array
    {
        $headers = ['Content-Type' => 'application/json'];
        if ($key) {
            $headers['Authorization'] = 'Bearer ' . $key;
        }
        return $headers;
    }

    /**
     * Analyze text using the new backend API
     */
    public function analyze(string $text, array $options = []): array
    {
        if (!$this->useNewBackend && $this->fallbackClient) {
            return $this->fallbackClient->analyze($text, $options);
        }

        try {
            $body = array_merge([
                'text' => $text,
                'language' => 'en',
                'score_threshold' => 0.35
            ], $options);

            $response = $this->backendClient->post('/api/v1/analyze', [
                'headers' => $this->buildHeaders($this->backendApiKey),
                'json'    => $body,
            ]);

            $result = json_decode($response->getBody()->getContents(), true);
            
            // Convert new backend format to original format for compatibility
            return $this->convertAnalysisResponse($result);

        } catch (GuzzleException $e) {
            // Fallback to original client if available
            if ($this->fallbackClient) {
                return $this->fallbackClient->analyze($text, $options);
            }
            throw $e;
        }
    }

    /**
     * Anonymize text using the new backend API
     */
    public function anonymize(string $text, array $analyzerResults, array $anonymizers = []): string
    {
        if (!$this->useNewBackend && $this->fallbackClient) {
            return $this->fallbackClient->anonymize($text, $analyzerResults, $anonymizers);
        }

        try {
            $body = [
                'text' => $text,
                'language' => 'en'
            ];
            
            if (!empty($anonymizers)) {
                $body['anonymizers'] = $anonymizers;
            }

            $response = $this->backendClient->post('/api/v1/anonymize', [
                'headers' => $this->buildHeaders($this->backendApiKey),
                'json'    => $body,
            ]);

            $result = json_decode($response->getBody()->getContents(), true);
            return $result['text'] ?? '';

        } catch (GuzzleException $e) {
            // Fallback to original client if available
            if ($this->fallbackClient) {
                return $this->fallbackClient->anonymize($text, $analyzerResults, $anonymizers);
            }
            throw $e;
        }
    }

    /**
     * Convenience method to analyze and immediately anonymize text.
     */
    public function analyzeAndAnonymize(string $text, array $options = []): string
    {
        if (!$this->useNewBackend && $this->fallbackClient) {
            return $this->fallbackClient->analyzeAndAnonymize($text, $options);
        }

        try {
            $body = array_merge([
                'text' => $text,
                'language' => 'en',
                'score_threshold' => 0.35
            ], $options);

            $response = $this->backendClient->post('/api/v1/anonymize', [
                'headers' => $this->buildHeaders($this->backendApiKey),
                'json'    => $body,
            ]);

            $result = json_decode($response->getBody()->getContents(), true);
            return $result['text'] ?? '';

        } catch (GuzzleException $e) {
            // Fallback to original client if available
            if ($this->fallbackClient) {
                return $this->fallbackClient->analyzeAndAnonymize($text, $options);
            }
            throw $e;
        }
    }

    /**
     * Advanced anonymization with detailed results (new feature)
     */
    public function advancedAnonymize(string $text, array $options = []): array
    {
        if (!$this->useNewBackend) {
            // For backward compatibility, use standard anonymization
            $anonymizedText = $this->analyzeAndAnonymize($text, $options);
            return [
                'anonymized_text' => $anonymizedText,
                'original_text' => $text,
                'processing_time' => 0,
                'entities' => [],
                'analysis_details' => []
            ];
        }

        try {
            // Use extended API endpoint
            $formData = [
                'text' => $text,
                'language' => $options['language'] ?? 'en',
                'score_threshold' => $options['score_threshold'] ?? 0.35
            ];
            
            if (!empty($options['entities'])) {
                $formData['entities'] = implode(',', $options['entities']);
            }

            $response = $this->backendClient->post('/api/v1/extended/anonymize/advanced', [
                'headers' => ['Content-Type' => 'application/x-www-form-urlencoded'],
                'form_params' => $formData
            ]);

            return json_decode($response->getBody()->getContents(), true);

        } catch (GuzzleException $e) {
            // Fallback to basic anonymization
            $anonymizedText = $this->analyzeAndAnonymize($text, $options);
            return [
                'anonymized_text' => $anonymizedText,
                'original_text' => $text,
                'processing_time' => 0,
                'entities' => [],
                'analysis_details' => [],
                'error' => $e->getMessage()
            ];
        }
    }

    /**
     * Get backend health and capabilities
     */
    public function getBackendHealth(): array
    {
        if (!$this->useNewBackend) {
            return ['status' => 'fallback_mode', 'backend' => 'original'];
        }

        try {
            $response = $this->backendClient->get('/health');
            return json_decode($response->getBody()->getContents(), true);
        } catch (GuzzleException $e) {
            return ['status' => 'error', 'message' => $e->getMessage()];
        }
    }

    /**
     * Convert new backend analysis response to original format
     */
    private function convertAnalysisResponse(array $newFormat): array
    {
        if (!isset($newFormat['entities'])) {
            return [];
        }

        return array_map(function($entity) {
            return [
                'entity_type' => $entity['entity_type'],
                'start' => $entity['start'],
                'end' => $entity['end'],
                'score' => $entity['score']
            ];
        }, $newFormat['entities']);
    }

    /**
     * Check if new backend is available and healthy
     */
    public function isNewBackendAvailable(): bool
    {
        if (!$this->useNewBackend) {
            return false;
        }

        try {
            $response = $this->backendClient->get('/health', ['timeout' => 5]);
            $health = json_decode($response->getBody()->getContents(), true);
            return isset($health['status']) && $health['status'] === 'healthy';
        } catch (Exception $e) {
            return false;
        }
    }
}
