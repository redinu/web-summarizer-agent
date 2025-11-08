"""
Tests for data models
"""

import pytest
from pydantic import ValidationError

from web_summarizer.models import (
    SummaryData,
    SummaryMetadata,
    SummaryOptions,
    SummaryRequest,
    SummaryResponse,
)


class TestSummaryOptions:
    def test_default_options(self):
        """Test default options are set correctly"""
        options = SummaryOptions()
        assert options.max_summary_sentences == 4
        assert options.num_key_points == 5
        assert options.include_citations is False
        assert options.model == "claude-3-haiku-20240307"
        assert options.timeout_seconds == 15

    def test_custom_options(self):
        """Test custom options can be set"""
        options = SummaryOptions(
            max_summary_sentences=6,
            num_key_points=8,
            include_citations=True,
            model="claude-3-sonnet-20240229",
            timeout_seconds=30,
        )
        assert options.max_summary_sentences == 6
        assert options.num_key_points == 8
        assert options.include_citations is True
        assert options.model == "claude-3-sonnet-20240229"
        assert options.timeout_seconds == 30

    def test_invalid_model(self):
        """Test validation fails for invalid model"""
        with pytest.raises(ValidationError):
            SummaryOptions(model="invalid-model")

    def test_sentence_count_validation(self):
        """Test sentence count must be within bounds"""
        with pytest.raises(ValidationError):
            SummaryOptions(max_summary_sentences=0)

        with pytest.raises(ValidationError):
            SummaryOptions(max_summary_sentences=11)


class TestSummaryRequest:
    def test_valid_request(self):
        """Test valid request creation"""
        request = SummaryRequest(url="https://example.com")
        assert str(request.url) == "https://example.com/"
        assert isinstance(request.options, SummaryOptions)

    def test_http_upgrade_to_https(self):
        """Test HTTP URLs are upgraded to HTTPS"""
        request = SummaryRequest(url="http://example.com")
        assert str(request.url).startswith("https://")

    def test_invalid_url(self):
        """Test invalid URLs are rejected"""
        with pytest.raises(ValidationError):
            SummaryRequest(url="not-a-url")

    def test_custom_options(self):
        """Test request with custom options"""
        options = SummaryOptions(max_summary_sentences=6)
        request = SummaryRequest(url="https://example.com", options=options)
        assert request.options.max_summary_sentences == 6


class TestSummaryResponse:
    def test_success_response(self):
        """Test successful response"""
        metadata = SummaryMetadata(
            tokens_used=1000,
            processing_time_ms=2000,
            model_used="claude-3-haiku-20240307",
            content_length=5000,
            extraction_method="readability",
        )

        data = SummaryData(
            url="https://example.com",
            title="Example Title",
            summary="This is a summary.",
            key_points=["Point 1", "Point 2"],
            category="Technology",
            metadata=metadata,
        )

        response = SummaryResponse(success=True, data=data)
        assert response.success is True
        assert response.data is not None
        assert response.error is None
        assert response.data.title == "Example Title"

    def test_error_response(self):
        """Test error response"""
        response = SummaryResponse(
            success=False,
            error="Something went wrong",
            error_code="TEST_ERROR",
        )
        assert response.success is False
        assert response.data is None
        assert response.error == "Something went wrong"
        assert response.error_code == "TEST_ERROR"

    def test_success_without_data_fails(self):
        """Test that success=True requires data"""
        with pytest.raises(ValidationError):
            SummaryResponse(success=True, data=None)

    def test_failure_without_error_fails(self):
        """Test that success=False requires error"""
        with pytest.raises(ValidationError):
            SummaryResponse(success=False, error=None)
