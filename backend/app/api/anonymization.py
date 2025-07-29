import time
import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models import (
    AnalyzeRequest,
    AnonymizeRequest,
    BatchAnonymizeRequest,
    AnalyzeResponse,
    AnonymizeResponse,
    BatchAnonymizeResponse,
    ErrorResponse
)
from app.services.anonymization import BaseAnonymizationService, get_anonymization_service

router = APIRouter(prefix="/api/v1", tags=["anonymization"])
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    service: BaseAnonymizationService = Depends(get_anonymization_service)
) -> AnalyzeResponse:
    """
    Analyze text for PII entities without anonymizing it.
    
    This endpoint identifies potentially sensitive information in the provided text
    and returns details about detected entities including their location and confidence scores.
    """
    try:
        logger.info(f"Analyzing text of length {len(request.text)}")
        result = await service.analyze(request)
        logger.info(f"Analysis completed in {result.processing_time:.3f}s, found {len(result.entities)} entities")
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize_text(
    request: AnonymizeRequest,
    service: BaseAnonymizationService = Depends(get_anonymization_service)
) -> AnonymizeResponse:
    """
    Anonymize text by detecting and replacing PII entities.
    
    This endpoint analyzes the text for sensitive information and returns an anonymized
    version with PII entities replaced according to the specified anonymization strategy.
    """
    try:
        logger.info(f"Anonymizing text of length {len(request.text)}")
        result = await service.anonymize(request)
        logger.info(f"Anonymization completed in {result.processing_time:.3f}s, processed {len(result.entities)} entities")
        return result
    except Exception as e:
        logger.error(f"Anonymization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchAnonymizeResponse)
async def batch_anonymize(
    request: BatchAnonymizeRequest,
    service: BaseAnonymizationService = Depends(get_anonymization_service)
) -> BatchAnonymizeResponse:
    """
    Anonymize multiple texts in a single batch request.
    
    This endpoint processes multiple texts simultaneously, which can be more efficient
    than making individual requests for each text.
    """
    try:
        start_time = time.time()
        logger.info(f"Processing batch of {len(request.texts)} texts")
        
        results = []
        for i, text in enumerate(request.texts):
            # Create individual request
            individual_request = AnonymizeRequest(
                text=text,
                entities=request.entities,
                language=request.language,
                score_threshold=request.score_threshold,
                anonymization_mode=request.anonymization_mode
            )
            
            # Process individual text
            result = await service.anonymize(individual_request)
            results.append(result)
            
            logger.debug(f"Processed text {i+1}/{len(request.texts)}")
        
        total_processing_time = time.time() - start_time
        logger.info(f"Batch processing completed in {total_processing_time:.3f}s")
        
        return BatchAnonymizeResponse(
            results=results,
            total_processing_time=total_processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch anonymization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/engines")
async def get_engines(
    service: BaseAnonymizationService = Depends(get_anonymization_service)
):
    """
    Get information about available anonymization engines.
    
    Returns details about the current anonymization engine including
    supported entities and languages.
    """
    try:
        engine_info = await service.get_engine_info()
        return engine_info
    except Exception as e:
        logger.error(f"Failed to get engine info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
