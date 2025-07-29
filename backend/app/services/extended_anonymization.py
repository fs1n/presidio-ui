import io
import time
import logging
from typing import List, Optional
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageDraw
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_image_redactor import ImageRedactorEngine
from python_docx import Document

from app.config import settings
from app.models import EntityResult

logger = logging.getLogger(__name__)


class ExtendedAnonymizationService:
    """Extended anonymization service with features from peterhubina/anonymization repository"""
    
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.image_redactor = ImageRedactorEngine()
        
        # Set Tesseract command if configured
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        
        logger.info("Initialized extended anonymization service")
    
    async def anonymize_text_advanced(self, text: str, **kwargs) -> dict:
        """Advanced text anonymization with detailed analysis"""
        start_time = time.time()
        
        try:
            # Analyze text
            analyzer_results = self.analyzer.analyze(
                text=text,
                entities=kwargs.get('entities'),
                language=kwargs.get('language', 'en'),
                score_threshold=kwargs.get('score_threshold', 0.35)
            )
            
            # Anonymize text
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                anonymizers=kwargs.get('anonymizers')
            )
            
            # Convert results
            entities = [
                EntityResult(
                    entity_type=result.entity_type,
                    start=result.start,
                    end=result.end,
                    text=text[result.start:result.end],
                    score=result.score
                )
                for result in analyzer_results
            ]
            
            processing_time = time.time() - start_time
            
            return {
                "original_text": text,
                "anonymized_text": anonymized_result.text,
                "entities": entities,
                "processing_time": processing_time,
                "analysis_details": {
                    "total_entities": len(entities),
                    "entity_types": list(set(e.entity_type for e in entities)),
                    "average_confidence": sum(e.score for e in entities) / len(entities) if entities else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Advanced text anonymization failed: {str(e)}")
            raise
    
    async def anonymize_pdf_text_only(self, pdf_content: bytes) -> dict:
        """Extract and anonymize text from PDF (text-based approach)"""
        start_time = time.time()
        
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            anonymized_pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():  # Only process pages with text
                    # Analyze text
                    results = self.analyzer.analyze(text=text, language='en')
                    
                    # Anonymize text
                    anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=results)
                    
                    anonymized_pages.append({
                        "page_number": page_num + 1,
                        "original_text": text,
                        "anonymized_text": anonymized_result.text,
                        "entities_found": len(results)
                    })
            
            doc.close()
            processing_time = time.time() - start_time
            
            return {
                "total_pages": len(doc),
                "processed_pages": len(anonymized_pages),
                "pages": anonymized_pages,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"PDF text anonymization failed: {str(e)}")
            raise
    
    async def anonymize_pdf_ocr(self, pdf_content: bytes) -> dict:
        """Convert PDF to images, apply OCR, and anonymize text"""
        start_time = time.time()
        
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            full_text = ""
            page_texts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                # Apply OCR
                text = pytesseract.image_to_string(img, lang=settings.ocr_language)
                full_text += text + "\n"
                page_texts.append({
                    "page_number": page_num + 1,
                    "text": text
                })
            
            # Analyze full text
            results = self.analyzer.analyze(text=full_text, language='en')
            
            # Anonymize full text
            anonymized_result = self.anonymizer.anonymize(text=full_text, analyzer_results=results)
            
            doc.close()
            processing_time = time.time() - start_time
            
            return {
                "total_pages": len(doc),
                "original_text": full_text,
                "anonymized_text": anonymized_result.text,
                "pages": page_texts,
                "entities_found": len(results),
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"PDF OCR anonymization failed: {str(e)}")
            raise
    
    async def anonymize_image_with_presidio(self, image_content: bytes) -> bytes:
        """Anonymize an image using Presidio Image Redactor"""
        try:
            # Convert bytes to PIL Image
            img = Image.open(io.BytesIO(image_content))
            
            # Use Presidio Image Redactor
            redacted_image = self.image_redactor.redact(img)
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            redacted_image.save(output_buffer, format='PNG')
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Image anonymization failed: {str(e)}")
            raise
    
    async def anonymize_pdf_mixed_content(self, pdf_content: bytes) -> dict:
        """Process PDF with both text and images (comprehensive approach)"""
        start_time = time.time()
        
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            results = {
                "total_pages": len(doc),
                "text_pages": [],
                "image_pages": [],
                "processing_time": 0
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Determine page type
                if len(text.strip()) > 100:  # Text-rich page
                    # Process as text page
                    analysis_results = self.analyzer.analyze(text=text, language='en')
                    anonymized_result = self.anonymizer.anonymize(text=text, analyzer_results=analysis_results)
                    
                    results["text_pages"].append({
                        "page_number": page_num + 1,
                        "original_text": text,
                        "anonymized_text": anonymized_result.text,
                        "entities_found": len(analysis_results)
                    })
                else:
                    # Process as image page
                    pix = page.get_pixmap(dpi=300)
                    img_data = pix.tobytes("png")
                    
                    # Apply OCR
                    img = Image.open(io.BytesIO(img_data))
                    ocr_text = pytesseract.image_to_string(img, lang=settings.ocr_language)
                    
                    # Anonymize OCR text
                    if ocr_text.strip():
                        analysis_results = self.analyzer.analyze(text=ocr_text, language='en')
                        anonymized_text = self.anonymizer.anonymize(text=ocr_text, analyzer_results=analysis_results)
                        
                        results["image_pages"].append({
                            "page_number": page_num + 1,
                            "ocr_text": ocr_text,
                            "anonymized_text": anonymized_text.text,
                            "entities_found": len(analysis_results)
                        })
            
            doc.close()
            results["processing_time"] = time.time() - start_time
            
            return results
            
        except Exception as e:
            logger.error(f"Mixed content PDF anonymization failed: {str(e)}")
            raise
    
    def _is_text_page(self, page, threshold: int = 100) -> bool:
        """Simple heuristic to determine if a page is primarily text"""
        text = page.get_text()
        return len(text.strip()) > threshold
