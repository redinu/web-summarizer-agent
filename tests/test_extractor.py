"""
Tests for content extractor
"""

import pytest

from web_summarizer.extractor import ContentExtractor, ExtractionError


class TestContentExtractor:
    def test_basic_extraction(self):
        """Test basic content extraction"""
        html = """
        <html>
        <head><title>Test Article</title></head>
        <body>
            <article>
                <h1>Main Title</h1>
                <p>This is the main content of the article.</p>
                <p>It contains multiple paragraphs with useful information.</p>
            </article>
        </body>
        </html>
        """

        extractor = ContentExtractor()
        text, title = extractor.extract(html, "https://example.com")

        assert "main content" in text.lower()
        assert "Test Article" in title
        assert len(text) >= 100

    def test_remove_navigation(self):
        """Test that navigation elements are removed"""
        html = """
        <html>
        <body>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
            </nav>
            <article>
                <p>This is the main content that should be extracted from this important article.</p>
                <p>More important content here with additional details to reach minimum length.</p>
                <p>Even more content to ensure we have enough text for extraction to succeed.</p>
            </article>
        </body>
        </html>
        """

        extractor = ContentExtractor()
        text, _ = extractor.extract(html, "https://example.com")

        assert "Home" not in text
        assert "About" not in text
        assert "main content" in text

    def test_remove_scripts_and_styles(self):
        """Test that script and style tags are removed"""
        html = """
        <html>
        <head>
            <style>body { color: red; }</style>
        </head>
        <body>
            <script>console.log('test');</script>
            <article>
                <p>This is the actual content we want to keep from the article.</p>
                <p>And more important text here with useful information for the reader.</p>
                <p>Additional paragraphs ensure we meet the minimum content length requirement.</p>
            </article>
        </body>
        </html>
        """

        extractor = ContentExtractor()
        text, _ = extractor.extract(html, "https://example.com")

        assert "console.log" not in text
        assert "color: red" not in text
        assert "actual content" in text

    def test_remove_ads_and_sidebars(self):
        """Test that ads and sidebars are removed"""
        html = """
        <html>
        <body>
            <div class="advertisement">Buy our product!</div>
            <aside class="sidebar">Related articles</aside>
            <article>
                <p>Main article content that is important and contains valuable information for readers.</p>
                <p>This should be extracted successfully without any advertising or sidebar content.</p>
                <p>Additional text to ensure we meet the minimum required length for extraction.</p>
            </article>
        </body>
        </html>
        """

        extractor = ContentExtractor()
        text, _ = extractor.extract(html, "https://example.com")

        assert "Buy our product" not in text
        assert "Related articles" not in text
        assert "Main article" in text

    def test_empty_content_error(self):
        """Test that empty content raises error"""
        extractor = ContentExtractor()

        with pytest.raises(ExtractionError) as exc_info:
            extractor.extract("", "https://example.com")

        assert exc_info.value.error_code == "EMPTY_CONTENT"

    def test_insufficient_content_error(self):
        """Test that insufficient content raises error"""
        html = "<html><body><p>Too short</p></body></html>"

        extractor = ContentExtractor(min_content_length=100)

        with pytest.raises(ExtractionError) as exc_info:
            extractor.extract(html, "https://example.com")

        assert exc_info.value.error_code == "INSUFFICIENT_CONTENT"

    def test_content_truncation(self):
        """Test that long content is truncated"""
        long_text = "A" * 60000
        html = f"<html><body><article><p>{long_text}</p></article></body></html>"

        extractor = ContentExtractor(max_content_length=50000)
        text, _ = extractor.extract(html, "https://example.com")

        assert len(text) <= 50003  # 50000 + "..."

    def test_clean_whitespace(self):
        """Test that excessive whitespace is cleaned"""
        html = """
        <html>
        <body>
            <article>
                <p>This    has    extra    spaces    that    should    be    cleaned    properly.</p>


                <p>And multiple blank lines that need to be normalized in the extracted content.</p>
                <p>Additional content to ensure we meet minimum length requirements for extraction.</p>
            </article>
        </body>
        </html>
        """

        extractor = ContentExtractor()
        text, _ = extractor.extract(html, "https://example.com")

        # Should not have multiple consecutive spaces
        assert "    " not in text
        # Should not have more than 2 consecutive newlines
        assert "\n\n\n" not in text

    def test_preserve_paragraphs(self):
        """Test that paragraph structure is preserved"""
        html = """
        <html>
        <body>
            <article>
                <p>First paragraph with important content.</p>
                <p>Second paragraph with more information.</p>
                <p>Third paragraph with additional details.</p>
            </article>
        </body>
        </html>
        """

        extractor = ContentExtractor()
        text, _ = extractor.extract(html, "https://example.com")

        # Check that text contains all paragraphs
        assert "First paragraph" in text
        assert "Second paragraph" in text
        assert "Third paragraph" in text
