"""
URL fetching and content retrieval module
"""

import logging
from typing import Tuple
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)


class FetchError(Exception):
    """Base exception for fetch errors"""

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class URLFetcher:
    """Handles fetching webpage content"""

    def __init__(
        self,
        timeout: int = 10,
        max_redirects: int = 3,
        user_agent: str = "WebSummarizerAgent/1.0.0",
    ):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.user_agent = user_agent

    def fetch(self, url: str) -> Tuple[str, str]:
        """
        Fetch content from a URL

        Args:
            url: The URL to fetch

        Returns:
            Tuple of (html_content, final_url)

        Raises:
            FetchError: If fetching fails
        """
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise FetchError(
                f"Invalid URL format: {url}",
                error_code="INVALID_URL",
            )

        # Ensure HTTPS
        if parsed.scheme == "http":
            url = url.replace("http://", "https://", 1)
            logger.info(f"Upgraded HTTP to HTTPS: {url}")

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            logger.info(f"Fetching URL: {url}")
            # Create session to configure max redirects
            session = requests.Session()
            session.max_redirects = self.max_redirects

            response = session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
            )

            # Check for HTTP errors
            if response.status_code == 404:
                raise FetchError(
                    f"Page not found (404): {url}",
                    error_code="NOT_FOUND",
                )
            elif response.status_code == 403:
                raise FetchError(
                    f"Access forbidden (403): {url}",
                    error_code="FORBIDDEN",
                )
            elif response.status_code == 500:
                raise FetchError(
                    f"Server error (500): {url}",
                    error_code="SERVER_ERROR",
                )
            elif response.status_code >= 400:
                raise FetchError(
                    f"HTTP error {response.status_code}: {url}",
                    error_code=f"HTTP_{response.status_code}",
                )

            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                logger.warning(f"Unexpected content type: {content_type}")

            # Get final URL after redirects
            final_url = response.url

            logger.info(f"Successfully fetched {len(response.text)} bytes from {final_url}")

            return response.text, final_url

        except FetchError:
            # Re-raise FetchError as-is
            raise
        except Timeout:
            raise FetchError(
                f"Request timeout after {self.timeout} seconds: {url}",
                error_code="TIMEOUT",
            )
        except RequestException as e:
            logger.error(f"Request failed: {e}")
            raise FetchError(
                f"Failed to fetch URL: {str(e)}",
                error_code="REQUEST_FAILED",
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise FetchError(
                f"Unexpected error while fetching URL: {str(e)}",
                error_code="UNKNOWN_ERROR",
            )
