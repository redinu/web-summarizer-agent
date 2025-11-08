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
            search_results = ddgs.text(
                query,
                max_results=num_results,
                backend="api"  # Use API backend for more reliable results
            )

            # Convert generator to list and process results
            for result in search_results:
                if isinstance(result, dict):
                    url = result.get("href") or result.get("url") or result.get("link", "")
                    if url:  # Only add if we have a valid URL
                        results.append({
                            "title": result.get("title", ""),
                            "url": url,
                            "snippet": result.get("body", "") or result.get("snippet", ""),
                        })

            logger.info(f"Found {len(results)} results for query: {query}")

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            # Try with different backend as fallback
            try:
                logger.info("Retrying with alternative backend...")
                ddgs = DDGS()
                search_results = ddgs.text(query, max_results=num_results)

                for result in search_results:
                    if isinstance(result, dict):
                        url = result.get("href") or result.get("url") or result.get("link", "")
                        if url:
                            results.append({
                                "title": result.get("title", ""),
                                "url": url,
                                "snippet": result.get("body", "") or result.get("snippet", ""),
                            })

                logger.info(f"Fallback search found {len(results)} results")

            except Exception as fallback_error:
                logger.error(f"Fallback search also failed: {fallback_error}")
                raise WebSearchError(
                    f"Search failed: {str(e)}. Fallback also failed: {str(fallback_error)}",
                    error_code="SEARCH_FAILED"
                )

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
                if isinstance(result, dict):
                    url = result.get("url") or result.get("href") or result.get("link", "")
                    if url:
                        results.append({
                            "title": result.get("title", ""),
                            "url": url,
                            "snippet": result.get("body", "") or result.get("snippet", ""),
                            "date": result.get("date", ""),
                            "source": result.get("source", ""),
                        })

            logger.info(f"Found {len(results)} news articles for query: {query}")

        except Exception as e:
            logger.error(f"News search failed: {e}")
            # Fallback to regular search if news search fails
            try:
                logger.info("News search failed, falling back to regular search...")
                ddgs = DDGS()
                search_results = ddgs.text(query, max_results=num_results)

                for result in search_results:
                    if isinstance(result, dict):
                        url = result.get("href") or result.get("url") or result.get("link", "")
                        if url:
                            results.append({
                                "title": result.get("title", ""),
                                "url": url,
                                "snippet": result.get("body", "") or result.get("snippet", ""),
                                "date": "",
                                "source": "",
                            })

                logger.info(f"Fallback search found {len(results)} results")

            except Exception as fallback_error:
                logger.error(f"Fallback search also failed: {fallback_error}")
                raise WebSearchError(
                    f"News search failed: {str(e)}. Fallback also failed: {str(fallback_error)}",
                    error_code="NEWS_SEARCH_FAILED"
                )

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
