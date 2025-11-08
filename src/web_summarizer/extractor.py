"""
Content extraction and cleaning module
"""

import logging
import re
from typing import Optional, Tuple

from bs4 import BeautifulSoup
from readability import Document

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Exception raised when content extraction fails"""

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ContentExtractor:
    """Extracts and cleans readable content from HTML"""

    def __init__(self, min_content_length: int = 100, max_content_length: int = 50000):
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length

    def extract(self, html: str, url: str) -> Tuple[str, Optional[str]]:
        """
        Extract clean readable content from HTML

        Args:
            html: Raw HTML content
            url: Source URL (for context)

        Returns:
            Tuple of (cleaned_text, title)

        Raises:
            ExtractionError: If extraction fails or content is insufficient
        """
        if not html or not html.strip():
            raise ExtractionError(
                "Empty HTML content provided",
                error_code="EMPTY_CONTENT",
            )

        try:
            # Use readability to extract main content
            doc = Document(html)
            title = doc.title()
            content_html = doc.summary()

            logger.info(f"Extracted title: {title}")

            # Parse with BeautifulSoup for cleaning
            soup = BeautifulSoup(content_html, "lxml")

            # Remove unwanted elements
            self._remove_unwanted_elements(soup)

            # Extract text
            text = soup.get_text(separator="\n", strip=True)

            # Clean the text
            cleaned_text = self._clean_text(text)

            # Validate content length
            if len(cleaned_text) < self.min_content_length:
                raise ExtractionError(
                    f"Insufficient content extracted ({len(cleaned_text)} chars, minimum {self.min_content_length})",
                    error_code="INSUFFICIENT_CONTENT",
                )

            # Truncate if too long
            if len(cleaned_text) > self.max_content_length:
                logger.warning(
                    f"Content exceeds max length ({len(cleaned_text)} chars), truncating to {self.max_content_length}"
                )
                cleaned_text = cleaned_text[: self.max_content_length] + "..."

            logger.info(f"Extracted {len(cleaned_text)} characters of clean text")

            return cleaned_text, title

        except ExtractionError:
            raise
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise ExtractionError(
                f"Failed to extract content: {str(e)}",
                error_code="EXTRACTION_FAILED",
            )

    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """Remove unwanted HTML elements"""
        # Remove script and style elements
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        # Remove navigation elements
        for element in soup.find_all(["nav", "header", "footer", "aside"]):
            element.decompose()

        # Remove elements with common ad/menu classes
        unwanted_classes = [
            "ad",
            "advertisement",
            "sidebar",
            "menu",
            "navigation",
            "nav",
            "footer",
            "header",
            "social",
            "share",
            "comments",
            "related",
            "recommended",
            "popup",
            "modal",
        ]

        for class_name in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_name, re.IGNORECASE)):
                element.decompose()

        # Remove elements with common ad/menu IDs
        for id_name in unwanted_classes:
            for element in soup.find_all(id=re.compile(id_name, re.IGNORECASE)):
                element.decompose()

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Replace multiple newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove excessive whitespace
        text = re.sub(r"[ \t]+", " ", text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]

        # Remove empty lines
        lines = [line for line in lines if line]

        # Join lines back together
        text = "\n".join(lines)

        return text.strip()
