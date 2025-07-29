from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AnonymizationMode(str, Enum):
    REPLACE = "replace"
    REDACT = "redact"
    HASH = "hash"
    MASK = "mask"
    ENCRYPT = "encrypt"


class AnonymizationEngine(str, Enum):
    PRESIDIO = "presidio"
    EXTENDED = "extended"  # With additional features from peterhubina/anonymization
    

class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for PII")
    entities: Optional[List[str]] = Field(
        default=None, 
        description="List of entity types to detect. If None, all supported entities will be used"
    )
    language: str = Field(default="en", description="Language of the text")
    score_threshold: float = Field(
        default=0.35, 
        ge=0.0, 
        le=1.0, 
        description="Minimum confidence score for entity detection"
    )


class AnonymizeRequest(BaseModel):
    text: str = Field(..., description="Text to anonymize")
    entities: Optional[List[str]] = Field(
        default=None,
        description="List of entity types to anonymize. If None, all detected entities will be anonymized"
    )
    language: str = Field(default="en", description="Language of the text")
    score_threshold: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for entity detection"
    )
    anonymization_mode: AnonymizationMode = Field(
        default=AnonymizationMode.REPLACE,
        description="Anonymization strategy to use"
    )
    anonymizers: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Custom anonymizers configuration"
    )


class BatchAnonymizeRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to anonymize")
    entities: Optional[List[str]] = Field(default=None)
    language: str = Field(default="en")
    score_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    anonymization_mode: AnonymizationMode = Field(default=AnonymizationMode.REPLACE)


class EntityResult(BaseModel):
    entity_type: str = Field(..., description="Type of detected entity")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text") 
    text: str = Field(..., description="Detected entity text")
    score: float = Field(..., description="Confidence score")


class AnalyzeResponse(BaseModel):
    entities: List[EntityResult] = Field(..., description="List of detected entities")
    processing_time: float = Field(..., description="Processing time in seconds")


class AnonymizeResponse(BaseModel):
    text: str = Field(..., description="Anonymized text")
    entities: List[EntityResult] = Field(..., description="List of anonymized entities")
    processing_time: float = Field(..., description="Processing time in seconds")


class BatchAnonymizeResponse(BaseModel):
    results: List[AnonymizeResponse] = Field(..., description="List of anonymization results")
    total_processing_time: float = Field(..., description="Total processing time in seconds")


class EngineInfo(BaseModel):
    name: str = Field(..., description="Engine name")
    version: str = Field(..., description="Engine version")
    supported_entities: List[str] = Field(..., description="List of supported entity types")
    supported_languages: List[str] = Field(..., description="List of supported languages")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    engines: List[EngineInfo] = Field(..., description="Available anonymization engines")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    code: Optional[str] = Field(default=None, description="Error code")
