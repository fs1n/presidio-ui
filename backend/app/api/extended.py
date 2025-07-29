import logging
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import Response, JSONResponse

from app.services.extended_anonymization import ExtendedAnonymizationService
from app.services.file_service import FileService

router = APIRouter(prefix="/api/v1/extended", tags=["extended-anonymization"])
logger = logging.getLogger(__name__)


def get_extended_service():
    return ExtendedAnonymizationService()


def get_file_service():
    return FileService()


@router.post("/anonymize/advanced")
async def anonymize_text_advanced(
    text: str = Form(...),
    entities: str = Form(None),
    language: str = Form("en"),
    score_threshold: float = Form(0.35),
    service: ExtendedAnonymizationService = Depends(get_extended_service)
):
    """
    Advanced text anonymization with detailed analysis and statistics.
    
    Provides enhanced anonymization with additional analytics and insights
    about the processing results.
    """
    try:
        # Parse entities if provided
        entity_list = None
        if entities:
            entity_list = [e.strip() for e in entities.split(",") if e.strip()]
        
        result = await service.anonymize_text_advanced(
            text=text,
            entities=entity_list,
            language=language,
            score_threshold=score_threshold
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Advanced text anonymization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anonymize/pdf/text")
async def anonymize_pdf_text(
    file: UploadFile = File(...),
    service: ExtendedAnonymizationService = Depends(get_extended_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Anonymize PDF content by extracting and processing text directly.
    
    This approach works best with PDFs that contain selectable text.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process PDF
        result = await service.anonymize_pdf_text_only(content)
        
        return result
        
    except Exception as e:
        logger.error(f"PDF text anonymization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anonymize/pdf/ocr")
async def anonymize_pdf_ocr(
    file: UploadFile = File(...),
    service: ExtendedAnonymizationService = Depends(get_extended_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Anonymize PDF content using OCR (Optical Character Recognition).
    
    This approach converts PDF pages to images, applies OCR to extract text,
    and then anonymizes the extracted text. Best for scanned PDFs or image-based content.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process PDF with OCR
        result = await service.anonymize_pdf_ocr(content)
        
        return result
        
    except Exception as e:
        logger.error(f"PDF OCR anonymization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anonymize/pdf/mixed")
async def anonymize_pdf_mixed(
    file: UploadFile = File(...),
    service: ExtendedAnonymizationService = Depends(get_extended_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Comprehensive PDF anonymization handling both text and image content.
    
    This approach automatically determines the best processing method for each page
    based on content analysis, using direct text extraction for text-rich pages
    and OCR for image-based pages.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Process PDF with mixed approach
        result = await service.anonymize_pdf_mixed_content(content)
        
        return result
        
    except Exception as e:
        logger.error(f"Mixed PDF anonymization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anonymize/image")
async def anonymize_image(
    file: UploadFile = File(...),
    service: ExtendedAnonymizationService = Depends(get_extended_service)
):
    """
    Anonymize images by detecting and redacting PII in visual content.
    
    Uses Presidio Image Redactor to identify and mask sensitive information
    directly in images.
    """
    try:
        # Validate file type
        valid_extensions = ['.png', '.jpg', '.jpeg']
        if not any(file.filename.lower().endswith(ext) for ext in valid_extensions):
            raise HTTPException(
                status_code=400, 
                detail="Only PNG, JPG, and JPEG files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Process image
        anonymized_content = await service.anonymize_image_with_presidio(content)
        
        # Return anonymized image
        return Response(
            content=anonymized_content,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=anonymized_{file.filename}"}
        )
        
    except Exception as e:
        logger.error(f"Image anonymization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def get_extended_capabilities():
    """
    Get information about extended anonymization capabilities.
    
    Returns details about supported file types, processing methods,
    and additional features available in the extended service.
    """
    return {
        "supported_file_types": {
            "text": [".txt"],
            "pdf": [".pdf"],
            "images": [".png", ".jpg", ".jpeg"]
        },
        "processing_methods": {
            "text": ["direct_anonymization", "advanced_analysis"],
            "pdf": ["text_extraction", "ocr", "mixed_content"],
            "images": ["visual_redaction"]
        },
        "features": [
            "detailed_analytics",
            "batch_processing",
            "multi_language_support",
            "custom_entity_recognition",
            "performance_metrics"
        ],
        "ocr_languages": ["eng", "deu", "fra", "spa"],  # Expandable based on Tesseract config
        "max_file_size": "10MB",
        "supported_image_formats": ["PNG", "JPEG", "JPG"]
    }
