"""
Web search module for finding relevant articles on a topic
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class WebSearchError(Exception):
    """Exception raised when web search fails"""

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class WebSearcher:
    """Search the web for relevant articles using DuckDuckGo"""

    def __init__(self, search_engine: str = "duckduckgo"):
        """Initialize web searcher"""
        self.search_engine = search_engine.lower()

    def search(
        self,
        query: str,
        num_results: int = 10,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, str]]:
        """Search the web for articles"""
        logger.info(f"Searching for: {query}")

        try:
            from duckduckgo_search import DDGS
        except ImportError:
            raise WebSearchError(
                "duckduckgo-search is not installed. Install with: pip install duckduckgo-search",
                error_code="MISSING_DEPENDENCY"
            )

        results = []

        try:
            ddgs = DDGS()
            search_results = ddgs.text(query, max_results=num_results)

            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise WebSearchError(
                f"Search failed: {str(e)}",
                error_code="SEARCH_FAILED"
            )

        logger.info(f"Found {len(results)} results")
        return results

    def search_news(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, str]]:
        """Search for news articles"""
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            raise WebSearchError(
                "duckduckgo-search is not installed. Install with: pip install duckduckgo-search",
                error_code="MISSING_DEPENDENCY"
            )

        results = []

        try:
            ddgs = DDGS()
            news_results = ddgs.news(query, max_results=num_results)

            for result in news_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", ""),
                })
        except Exception as e:
            logger.error(f"News search failed: {e}")
            raise WebSearchError(
                f"News search failed: {str(e)}",
                error_code="NEWS_SEARCH_FAILED"
            )

        logger.info(f"Found {len(results)} news articles")
        return results

    def filter_by_domain(
        self,
        results: List[Dict[str, str]],
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """Filter search results by domain"""
        from urllib.parse import urlparse

        filtered = []

        for result in results:
            url = result.get("url", "")
            try:
                domain = urlparse(url).netloc.lower()

                if domain.startswith("www."):
                    domain = domain[4:]

                if blocked_domains:
                    if any(blocked in domain for blocked in blocked_domains):
                        continue

                if allowed_domains:
                    if not any(allowed in domain for allowed in allowed_domains):
                        continue

                filtered.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse URL {url}: {e}")
                continue

        logger.info(f"Filtered {len(results)} results to {len(filtered)}")
        return filtered
