import time
import logging
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import httpx

from app.config import settings
from app.models import (
    AnalyzeRequest,
    AnonymizeRequest,
    AnalyzeResponse,
    AnonymizeResponse,
    EntityResult,
    EngineInfo
)

logger = logging.getLogger(__name__)


class BaseAnonymizationService(ABC):
    """Base class for anonymization services"""
    
    @abstractmethod
    async def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        pass
    
    @abstractmethod
    async def anonymize(self, request: AnonymizeRequest) -> AnonymizeResponse:
        pass
    
    @abstractmethod
    async def get_engine_info(self) -> EngineInfo:
        pass


class LocalPresidioService(BaseAnonymizationService):
    """Local Presidio service using built-in engines"""
    
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        logger.info("Initialized local Presidio engines")
    
    async def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        start_time = time.time()
        
        try:
            # Run analysis
            analyzer_results = self.analyzer.analyze(
                text=request.text,
                entities=request.entities,
                language=request.language,
                score_threshold=request.score_threshold
            )
            
            # Convert results to our model
            entities = [
                EntityResult(
                    entity_type=result.entity_type,
                    start=result.start,
                    end=result.end,
                    text=request.text[result.start:result.end],
                    score=result.score
                )
                for result in analyzer_results
            ]
            
            processing_time = time.time() - start_time
            
            return AnalyzeResponse(
                entities=entities,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    async def anonymize(self, request: AnonymizeRequest) -> AnonymizeResponse:
        start_time = time.time()
        
        try:
            # First analyze the text
            analyzer_results = self.analyzer.analyze(
                text=request.text,
                entities=request.entities,
                language=request.language,
                score_threshold=request.score_threshold
            )
            
            # Then anonymize
            anonymization_result = self.anonymizer.anonymize(
                text=request.text,
                analyzer_results=analyzer_results,
                anonymizers=request.anonymizers
            )
            
            # Convert analyzer results to our model
            entities = [
                EntityResult(
                    entity_type=result.entity_type,
                    start=result.start,
                    end=result.end,
                    text=request.text[result.start:result.end],
                    score=result.score
                )
                for result in analyzer_results
            ]
            
            processing_time = time.time() - start_time
            
            return AnonymizeResponse(
                text=anonymization_result.text,
                entities=entities,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Anonymization failed: {str(e)}")
            raise
    
    async def get_engine_info(self) -> EngineInfo:
        supported_entities = self.analyzer.get_supported_entities()
        supported_languages = self.analyzer.get_supported_languages()
        
        return EngineInfo(
            name="presidio-local",
            version="2.2.33",
            supported_entities=supported_entities,
            supported_languages=supported_languages
        )


class ExternalPresidioService(BaseAnonymizationService):
    """External Presidio service using HTTP APIs (compatible with current PHP implementation)"""
    
    def __init__(self):
        self.analyzer_url = settings.presidio_analyzer_api_url
        self.anonymizer_url = settings.presidio_anonymizer_api_url
        self.analyzer_key = settings.presidio_analyzer_api_key
        self.anonymizer_key = settings.presidio_anonymizer_api_key
        logger.info(f"Initialized external Presidio service: analyzer={self.analyzer_url}, anonymizer={self.anonymizer_url}")
    
    def _build_headers(self, key: Optional[str]) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers
    
    async def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        start_time = time.time()
        
        try:
            body = {
                "text": request.text,
                "language": request.language,
            }
            if request.entities:
                body["entities"] = request.entities
            if request.score_threshold != 0.35:  # Only add if different from default
                body["score_threshold"] = request.score_threshold
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.analyzer_url}/analyze",
                    json=body,
                    headers=self._build_headers(self.analyzer_key),
                    timeout=30.0
                )
                response.raise_for_status()
                analyzer_results = response.json()
            
            # Convert results to our model
            entities = [
                EntityResult(
                    entity_type=result["entity_type"],
                    start=result["start"],
                    end=result["end"],
                    text=request.text[result["start"]:result["end"]],
                    score=result["score"]
                )
                for result in analyzer_results
            ]
            
            processing_time = time.time() - start_time
            
            return AnalyzeResponse(
                entities=entities,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"External analysis failed: {str(e)}")
            raise
    
    async def anonymize(self, request: AnonymizeRequest) -> AnonymizeResponse:
        start_time = time.time()
        
        try:
            # First analyze
            analyze_request = AnalyzeRequest(
                text=request.text,
                entities=request.entities,
                language=request.language,
                score_threshold=request.score_threshold
            )
            analyze_response = await self.analyze(analyze_request)
            
            # Convert entities back to analyzer format for anonymizer
            analyzer_results = [
                {
                    "entity_type": entity.entity_type,
                    "start": entity.start,
                    "end": entity.end,
                    "score": entity.score
                }
                for entity in analyze_response.entities
            ]
            
            # Then anonymize
            body = {
                "text": request.text,
                "analyzer_results": analyzer_results
            }
            if request.anonymizers:
                body["anonymizers"] = request.anonymizers
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.anonymizer_url}/anonymize",
                    json=body,
                    headers=self._build_headers(self.anonymizer_key),
                    timeout=30.0
                )
                response.raise_for_status()
                anonymization_result = response.json()
            
            processing_time = time.time() - start_time
            
            return AnonymizeResponse(
                text=anonymization_result.get("text", ""),
                entities=analyze_response.entities,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"External anonymization failed: {str(e)}")
            raise
    
    async def get_engine_info(self) -> EngineInfo:
        # For external service, we return a static configuration
        # In a real implementation, you might query the service for this info
        return EngineInfo(
            name="presidio-external",
            version="2.2.33",
            supported_entities=[
                "CREDIT_CARD", "CRYPTO", "DATE_TIME", "EMAIL_ADDRESS", "IBAN_CODE",
                "IP_ADDRESS", "NRP", "LOCATION", "PERSON", "PHONE_NUMBER", "MEDICAL_LICENSE",
                "URL", "US_BANK_NUMBER", "US_DRIVER_LICENSE", "US_ITIN", "US_PASSPORT",
                "US_SSN"
            ],
            supported_languages=["en"]
        )


def get_anonymization_service() -> BaseAnonymizationService:
    """Factory function to get the appropriate anonymization service"""
    if settings.anonymization_mode == "local":
        return LocalPresidioService()
    else:
        return ExternalPresidioService()
