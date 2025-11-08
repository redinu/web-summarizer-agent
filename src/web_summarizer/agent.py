"""
Main Web Summarizer Agent
"""

import logging
import time
from typing import Optional

from web_summarizer.extractor import ContentExtractor, ExtractionError
from web_summarizer.fetcher import FetchError, URLFetcher
from web_summarizer.models import (
    ErrorResponse,
    SummaryData,
    SummaryMetadata,
    SummaryOptions,
    SummaryRequest,
    SummaryResponse,
)
from web_summarizer.summarizer import AISummarizer, SummarizationError

logger = logging.getLogger(__name__)


class WebSummarizerAgent:
    """
    Main agent for web content summarization

    Coordinates URL fetching, content extraction, and AI summarization
    to turn any webpage into structured, summarized information.
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        timeout: int = 10,
        max_redirects: int = 3,
        user_agent: str = "WebSummarizerAgent/1.0.0",
        min_content_length: int = 100,
        max_content_length: int = 50000,
    ):
        """
        Initialize the Web Summarizer Agent

        Args:
            gemini_api_key: API key for Google Gemini
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
            user_agent: User agent string for requests
            min_content_length: Minimum content length to process
            max_content_length: Maximum content length (will be truncated)
        """
        self.fetcher = URLFetcher(
            timeout=timeout,
            max_redirects=max_redirects,
            user_agent=user_agent,
        )
        self.extractor = ContentExtractor(
            min_content_length=min_content_length,
            max_content_length=max_content_length,
        )
        self.summarizer = AISummarizer(api_key=gemini_api_key)

        logger.info("WebSummarizerAgent initialized")

    def summarize(self, request: SummaryRequest) -> SummaryResponse:
        """
        Summarize a webpage from a URL

        Args:
            request: SummaryRequest containing URL and options

        Returns:
            SummaryResponse with success status and data/error
        """
        start_time = time.time()
        url = str(request.url)
        options = request.options or SummaryOptions()

        logger.info(f"Starting summarization for: {url}")

        try:
            # Step 1: Fetch the webpage
            html, final_url = self.fetcher.fetch(url)

            # Step 2: Extract content
            cleaned_text, title = self.extractor.extract(html, final_url)

            # Step 3: Summarize with AI
            summary_result = self.summarizer.summarize(
                text=cleaned_text,
                title=title,
                model=options.model,
                max_summary_sentences=options.max_summary_sentences,
                num_key_points=options.num_key_points,
                include_citations=options.include_citations,
                timeout=options.timeout_seconds,
            )

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Build response
            metadata = SummaryMetadata(
                tokens_used=summary_result.get("tokens_used", 0),
                processing_time_ms=processing_time_ms,
                model_used=summary_result.get("model_used", options.model),
                content_length=len(cleaned_text),
                extraction_method="readability",
            )

            data = SummaryData(
                url=final_url,
                title=title,
                summary=summary_result.get("summary", ""),
                key_points=summary_result.get("key_points", []),
                citations=summary_result.get("citations") if options.include_citations else None,
                category=summary_result.get("category"),
                metadata=metadata,
            )

            logger.info(f"Successfully summarized {url} in {processing_time_ms}ms")

            return SummaryResponse(success=True, data=data)

        except FetchError as e:
            logger.error(f"Fetch error: {e.message}")
            return SummaryResponse(
                success=False,
                error=e.message,
                error_code=e.error_code,
            )

        except ExtractionError as e:
            logger.error(f"Extraction error: {e.message}")
            return SummaryResponse(
                success=False,
                error=e.message,
                error_code=e.error_code,
            )

        except SummarizationError as e:
            logger.error(f"Summarization error: {e.message}")
            return SummaryResponse(
                success=False,
                error=e.message,
                error_code=e.error_code,
            )

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return SummaryResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                error_code="UNKNOWN_ERROR",
            )

    def summarize_url(
        self,
        url: str,
        max_summary_sentences: int = 4,
        num_key_points: int = 5,
        include_citations: bool = False,
        model: str = "models/gemini-2.5-flash",
    ) -> SummaryResponse:
        """
        Convenience method to summarize a URL with simple parameters

        Args:
            url: The URL to summarize
            max_summary_sentences: Maximum sentences in summary
            num_key_points: Number of key points to extract
            include_citations: Whether to include notable quotes
            model: AI model to use

        Returns:
            SummaryResponse with success status and data/error
        """
        request = SummaryRequest(
            url=url,
            options=SummaryOptions(
                max_summary_sentences=max_summary_sentences,
                num_key_points=num_key_points,
                include_citations=include_citations,
                model=model,
            ),
        )
        return self.summarize(request)
