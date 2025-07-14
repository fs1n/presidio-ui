<?php
namespace App;

class FilePiiProcessor
{
    private PresidioClient $client;

    public function __construct(PresidioClient $client)
    {
        $this->client = $client;
    }

    /**
     * Extract text from various document types and anonymize it using Presidio.
     * This is a best-effort helper which relies on optional CLI tools
     * such as `pandoc`, `pdftotext` and `tesseract` when available.
     */
    public function process(string $filePath): string
    {
        $ext = strtolower(pathinfo($filePath, PATHINFO_EXTENSION));
        $text = '';

        switch ($ext) {
            case 'txt':
            case 'md':
            case 'csv':
                $text = @file_get_contents($filePath) ?: '';
                break;
            case 'pdf':
                $cmd = 'pdftotext ' . escapeshellarg($filePath) . ' -';
                $text = shell_exec($cmd) ?? '';
                break;
            case 'png':
            case 'jpg':
            case 'jpeg':
            case 'gif':
            case 'tif':
            case 'tiff':
            case 'bmp':
                $cmd = 'tesseract ' . escapeshellarg($filePath) . ' stdout 2>/dev/null';
                $text = shell_exec($cmd) ?? '';
                break;
            case 'docx':
            case 'xlsx':
            case 'pptx':
                $cmd = 'pandoc ' . escapeshellarg($filePath) . ' -t plain';
                $text = shell_exec($cmd) ?? '';
                break;
            default:
                $text = @file_get_contents($filePath) ?: '';
        }

        $text = trim($text);
        if ($text === '') {
            return '';
        }

        return $this->client->analyzeAndAnonymize($text);
    }
}
