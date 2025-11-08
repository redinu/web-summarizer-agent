"""
Data models for Web Summarizer Agent
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SummaryOptions(BaseModel):
    """Configuration options for summarization"""

    max_summary_sentences: int = Field(default=4, ge=1, le=10)
    num_key_points: int = Field(default=5, ge=1, le=10)
    include_citations: bool = Field(default=False)
    model: str = Field(default="gemini-1.5-flash")
    timeout_seconds: int = Field(default=15, ge=1, le=60)

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name"""
        allowed_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
        ]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of: {', '.join(allowed_models)}")
        return v


class SummaryRequest(BaseModel):
    """Request model for web summarization"""

    url: HttpUrl
    options: Optional[SummaryOptions] = Field(default_factory=SummaryOptions)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: HttpUrl) -> HttpUrl:
        """Ensure URL uses HTTPS"""
        url_str = str(v)
        if url_str.startswith("http://"):
            # Auto-upgrade to HTTPS
            return HttpUrl(url_str.replace("http://", "https://", 1))
        return v


class SummaryMetadata(BaseModel):
    """Metadata about the summarization process"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tokens_used: int = Field(ge=0)
    processing_time_ms: int = Field(ge=0)
    model_used: str
    content_length: int = Field(ge=0)
    extraction_method: str


class SummaryData(BaseModel):
    """Successful summary data"""

    url: str
    title: Optional[str] = None
    summary: str
    key_points: List[str]
    citations: Optional[List[str]] = None
    category: Optional[str] = None
    metadata: SummaryMetadata


class SummaryResponse(BaseModel):
    """Response model for web summarization"""

    success: bool
    data: Optional[SummaryData] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @field_validator("data")
    @classmethod
    def validate_data_on_success(cls, v: Optional[SummaryData], info) -> Optional[SummaryData]:
        """Ensure data is present when success is True"""
        if info.data.get("success") and v is None:
            raise ValueError("data must be provided when success is True")
        return v

    @field_validator("error")
    @classmethod
    def validate_error_on_failure(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure error is present when success is False"""
        if not info.data.get("success") and v is None:
            raise ValueError("error must be provided when success is False")
        return v


class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = False
    error: str
    error_code: str
    details: Optional[dict] = None
