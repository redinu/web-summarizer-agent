"""
AI-powered summarization module using Google Gemini
"""

import json
import logging
import os
from typing import Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)


class SummarizationError(Exception):
    """Exception raised when summarization fails"""

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AISummarizer:
    """AI-powered text summarization using Google Gemini"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment or provided")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

    def summarize(
        self,
        text: str,
        title: Optional[str] = None,
        model: str = "gemini-1.5-flash",
        max_summary_sentences: int = 4,
        num_key_points: int = 5,
        include_citations: bool = False,
        timeout: int = 30,
    ) -> Dict:
        """
        Summarize text using AI

        Args:
            text: The text to summarize
            title: Optional document title
            model: AI model to use
            max_summary_sentences: Maximum sentences in summary
            num_key_points: Number of key points to extract
            include_citations: Whether to include notable quotes
            timeout: Request timeout in seconds

        Returns:
            Dictionary with summary, key_points, citations, category, tokens_used

        Raises:
            SummarizationError: If summarization fails
        """
        if not text or len(text.strip()) < 50:
            raise SummarizationError(
                "Text is too short to summarize",
                error_code="TEXT_TOO_SHORT",
            )

        try:
            # Build the prompt
            prompt = self._build_prompt(
                text=text,
                title=title,
                max_summary_sentences=max_summary_sentences,
                num_key_points=num_key_points,
                include_citations=include_citations,
            )

            logger.info(f"Sending {len(text)} characters to {model} for summarization")

            # Initialize Gemini model
            gemini_model = genai.GenerativeModel(model)

            # Configure generation
            generation_config = GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048,
            )

            # Call Gemini API
            response = gemini_model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={"timeout": timeout},
            )

            # Extract response content
            content = response.text

            # Parse JSON response
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If response is not JSON, try to extract it
                logger.warning("Response is not valid JSON, attempting to extract")
                result = self._extract_from_text(content)

            # Add metadata
            # Gemini provides token counts in usage_metadata
            tokens_used = 0
            if hasattr(response, 'usage_metadata'):
                tokens_used = (
                    response.usage_metadata.prompt_token_count +
                    response.usage_metadata.candidates_token_count
                )

            result["tokens_used"] = tokens_used
            result["model_used"] = model

            logger.info(f"Summarization complete. Tokens used: {result['tokens_used']}")

            return result

        except Exception as e:
            error_message = str(e)

            # Check for timeout
            if "timeout" in error_message.lower():
                raise SummarizationError(
                    f"AI request timeout after {timeout} seconds",
                    error_code="AI_TIMEOUT",
                )

            # Check for API errors
            if "api" in error_message.lower() or "quota" in error_message.lower():
                logger.error(f"Gemini API error: {e}")
                raise SummarizationError(
                    f"AI API error: {str(e)}",
                    error_code="AI_API_ERROR",
                )

            logger.error(f"Summarization failed: {e}")
            raise SummarizationError(
                f"Failed to summarize content: {str(e)}",
                error_code="SUMMARIZATION_FAILED",
            )

    def _build_prompt(
        self,
        text: str,
        title: Optional[str],
        max_summary_sentences: int,
        num_key_points: int,
        include_citations: bool,
    ) -> str:
        """Build the AI prompt for summarization"""
        title_info = f"Title: {title}\n\n" if title else ""

        citations_instruction = ""
        if include_citations:
            citations_instruction = """
  - "citations": Array of 2-3 notable quotes or key statements from the text (verbatim)
"""

        prompt = f"""You are an expert content summarizer. Analyze the following web content and provide a structured summary.

{title_info}Content:
{text}

Please provide a JSON response with the following structure:
{{
  "summary": "A concise summary in {max_summary_sentences} sentences or less that captures the main message and purpose",
  "key_points": Array of {num_key_points} key takeaways or main points (as strings){citations_instruction},
  "category": "The primary category or topic (e.g., Technology, Business, Health, Politics, etc.)"
}}

Focus on:
- The main message and thesis
- Key facts, findings, or arguments
- Important conclusions or recommendations
- Actionable insights if present

Ensure your response is valid JSON only, with no additional text or explanation."""

        return prompt

    def _extract_from_text(self, text: str) -> Dict:
        """Fallback: Extract structured data from non-JSON response"""
        logger.warning("Using fallback extraction method")

        # Try to find JSON in the text
        import re

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # If all else fails, return a basic structure
        return {
            "summary": text[:500] if len(text) > 500 else text,
            "key_points": ["Unable to extract structured data"],
            "category": "Unknown",
        }
