import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import HealthResponse, EngineInfo
from app.services.anonymization import BaseAnonymizationService, get_anonymization_service

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(
    service: BaseAnonymizationService = Depends(get_anonymization_service)
) -> HealthResponse:
    """
    Health check endpoint to verify service status and capabilities.
    
    Returns information about the service status, version, and available
    anonymization engines with their capabilities.
    """
    try:
        # Get engine information
        engine_info = await service.get_engine_info()
        
        # Return health response
        return HealthResponse(
            status="healthy",
            version=settings.api_version,
            engines=[engine_info]
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api/v1",
            "extended": "/api/v1/extended"
        }
    }


@router.get("/info")
async def get_api_info():
    """
    Get detailed API information and configuration.
    """
    return {
        "api": {
            "title": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description
        },
        "configuration": {
            "anonymization_mode": settings.anonymization_mode,
            "max_file_size": settings.max_file_size,
            "ocr_language": settings.ocr_language,
            "debug": settings.debug
        },
        "features": {
            "text_anonymization": True,
            "batch_processing": True,
            "pdf_processing": True,
            "image_processing": True,
            "ocr_support": True,
            "advanced_analytics": True
        }
    }
