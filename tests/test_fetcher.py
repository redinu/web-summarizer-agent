"""
Tests for URL fetcher
"""

import pytest
import requests_mock

from web_summarizer.fetcher import FetchError, URLFetcher


class TestURLFetcher:
    def test_successful_fetch(self):
        """Test successful URL fetch"""
        fetcher = URLFetcher()

        with requests_mock.Mocker() as m:
            m.get(
                "https://example.com",
                text="<html><body>Hello World</body></html>",
                headers={"Content-Type": "text/html"},
            )

            html, final_url = fetcher.fetch("https://example.com")

            assert "Hello World" in html
            assert final_url == "https://example.com"

    def test_http_upgrade(self):
        """Test HTTP URLs are upgraded to HTTPS"""
        fetcher = URLFetcher()

        with requests_mock.Mocker() as m:
            m.get(
                "https://example.com",
                text="<html><body>Content</body></html>",
            )

            html, final_url = fetcher.fetch("http://example.com")
            assert html is not None

    def test_invalid_url_format(self):
        """Test invalid URL format raises error"""
        fetcher = URLFetcher()

        with pytest.raises(FetchError) as exc_info:
            fetcher.fetch("not-a-url")

        assert exc_info.value.error_code == "INVALID_URL"

    def test_404_error(self):
        """Test 404 error handling"""
        fetcher = URLFetcher()

        with requests_mock.Mocker() as m:
            m.get("https://example.com", status_code=404)

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch("https://example.com")

            assert exc_info.value.error_code == "NOT_FOUND"
            assert "404" in exc_info.value.message

    def test_403_error(self):
        """Test 403 forbidden error handling"""
        fetcher = URLFetcher()

        with requests_mock.Mocker() as m:
            m.get("https://example.com", status_code=403)

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch("https://example.com")

            assert exc_info.value.error_code == "FORBIDDEN"

    def test_500_error(self):
        """Test 500 server error handling"""
        fetcher = URLFetcher()

        with requests_mock.Mocker() as m:
            m.get("https://example.com", status_code=500)

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch("https://example.com")

            assert exc_info.value.error_code == "SERVER_ERROR"

    def test_timeout(self):
        """Test timeout handling"""
        fetcher = URLFetcher(timeout=1)

        with requests_mock.Mocker() as m:
            m.get("https://example.com", exc=requests.exceptions.Timeout)

            with pytest.raises(FetchError) as exc_info:
                fetcher.fetch("https://example.com")

            assert exc_info.value.error_code == "TIMEOUT"

    def test_redirects(self):
        """Test redirect following"""
        fetcher = URLFetcher()

        with requests_mock.Mocker() as m:
            m.get(
                "https://example.com/old",
                status_code=301,
                headers={"Location": "https://example.com/new"},
            )
            m.get(
                "https://example.com/new",
                text="<html><body>New content</body></html>",
            )

            html, final_url = fetcher.fetch("https://example.com/old")

            assert "New content" in html
            assert "new" in final_url

    def test_custom_user_agent(self):
        """Test custom user agent is used"""
        fetcher = URLFetcher(user_agent="CustomAgent/1.0")

        with requests_mock.Mocker() as m:
            m.get("https://example.com", text="<html></html>")

            fetcher.fetch("https://example.com")

            assert m.request_history[0].headers["User-Agent"] == "CustomAgent/1.0"


# Import requests for timeout test
import requests
