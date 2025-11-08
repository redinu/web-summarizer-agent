"""
FastAPI REST API for Web Summarizer Agent
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
import io

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web_summarizer import WebSummarizerAgent
from web_summarizer.models import SummaryOptions, SummaryRequest, SummaryResponse
from web_summarizer.topic_aggregator import TopicAggregator
from web_summarizer.spreadsheet_generator import SpreadsheetGenerator
from web_summarizer.web_searcher import WebSearcher

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Web Summarizer API",
    description="AI-powered web content summarization using Google Gemini",
    version="1.0.0",
)

# Add CORS middleware to allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
try:
    agent = WebSummarizerAgent(
        gemini_api_key=os.getenv("GEMINI_API_KEY")
    )
    topic_aggregator = TopicAggregator(agent)
    spreadsheet_generator = SpreadsheetGenerator()
    web_searcher = WebSearcher(search_engine="duckduckgo")
except ValueError as e:
    print(f"⚠️ Warning: {e}")
    print("Please set GEMINI_API_KEY in your .env file")
    agent = None
    topic_aggregator = None
    spreadsheet_generator = None
    web_searcher = None


# Request models
class SummarizeURLRequest(BaseModel):
    """Simple request model for URL summarization"""
    url: HttpUrl
    max_summary_sentences: Optional[int] = 4
    num_key_points: Optional[int] = 5
    include_citations: Optional[bool] = False
    model: Optional[str] = "models/gemini-2.5-flash"


class AdvancedSummarizeRequest(BaseModel):
    """Advanced request model with full options"""
    url: HttpUrl
    options: Optional[SummaryOptions] = None


class TopicAggregatorRequest(BaseModel):
    """Request model for topic aggregation"""
    topic: str
    urls: list[str]
    platforms: Optional[list[str]] = ["twitter", "linkedin", "facebook"]
    max_workers: Optional[int] = 5
    export_format: Optional[str] = "csv"  # csv or excel


class TopicSearchRequest(BaseModel):
    """Request model for topic-based search and aggregation"""
    topic: str
    num_results: Optional[int] = 10
    platforms: Optional[list[str]] = ["twitter", "linkedin", "facebook"]
    max_workers: Optional[int] = 5
    export_format: Optional[str] = "csv"  # csv or excel
    search_type: Optional[str] = "web"  # web or news
    allowed_domains: Optional[list[str]] = None
    blocked_domains: Optional[list[str]] = None


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple HTML test interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Web Summarizer API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #1a73e8;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #333;
            }
            input[type="text"], input[type="number"], select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                box-sizing: border-box;
            }
            input[type="checkbox"] {
                margin-right: 5px;
            }
            button {
                background: #1a73e8;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                font-weight: 500;
            }
            button:hover {
                background: #1557b0;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .loading {
                display: none;
                margin-top: 20px;
                padding: 15px;
                background: #e3f2fd;
                border-radius: 5px;
                color: #1976d2;
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 5px;
                display: none;
            }
            .result h2 {
                margin-top: 0;
                color: #1a73e8;
            }
            .result .summary {
                background: white;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                border-left: 4px solid #1a73e8;
            }
            .result .key-points {
                background: white;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .result .metadata {
                font-size: 12px;
                color: #666;
                margin-top: 15px;
                padding: 10px;
                background: white;
                border-radius: 5px;
            }
            .error {
                background: #ffebee;
                color: #c62828;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
                display: none;
            }
            .endpoints {
                margin-top: 30px;
                padding: 20px;
                background: #f0f7ff;
                border-radius: 5px;
            }
            .endpoints h3 {
                margin-top: 0;
            }
            .endpoint {
                margin: 10px 0;
                padding: 10px;
                background: white;
                border-radius: 5px;
            }
            .method {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #4caf50; color: white; }
            .post { background: #2196f3; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Web Summarizer API</h1>
            <p class="subtitle">AI-powered web content summarization using Google Gemini</p>

            <form id="topicForm">
                <div class="form-group">
                    <label for="topic">Topic to Research</label>
                    <input type="text" id="topic" name="topic"
                           placeholder="Enter a topic (e.g., artificial intelligence, climate change)"
                           value="artificial intelligence" required>
                </div>

                <div class="form-group">
                    <label for="num_results">Number of Articles to Find</label>
                    <input type="number" id="num_results" name="num_results"
                           value="5" min="1" max="20">
                </div>

                <div class="form-group">
                    <label for="search_type">Search Type</label>
                    <select id="search_type" name="search_type">
                        <option value="web" selected>General Web Search</option>
                        <option value="news">News Articles Only</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="export_format">Export Format</label>
                    <select id="export_format" name="export_format">
                        <option value="json" selected>JSON (View in Browser)</option>
                        <option value="csv">CSV (Download)</option>
                        <option value="excel">Excel (Download)</option>
                        <option value="pdf">PDF Report (Download)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Social Media Platforms</label>
                    <div>
                        <label style="display: inline-block; margin-right: 15px;">
                            <input type="checkbox" name="platforms" value="twitter" checked> Twitter
                        </label>
                        <label style="display: inline-block; margin-right: 15px;">
                            <input type="checkbox" name="platforms" value="linkedin" checked> LinkedIn
                        </label>
                        <label style="display: inline-block;">
                            <input type="checkbox" name="platforms" value="facebook" checked> Facebook
                        </label>
                    </div>
                </div>

                <button type="submit" id="submitBtn">🔍 Research & Generate Content</button>
            </form>

            <div class="loading" id="loading">
                ⏳ Summarizing content... This may take a few seconds.
            </div>

            <div class="error" id="error"></div>

            <div class="result" id="result"></div>

            <div class="endpoints">
                <h3>📡 API Endpoints</h3>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/</code> - This page (Topic-based research interface)
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/health</code> - Health check
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/search-and-aggregate</code> - Research topic and generate social media posts
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/search-and-aggregate/export</code> - Research topic and export to CSV/Excel
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/summarize</code> - Summarize a single URL
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/docs</code> - Interactive API documentation (Swagger)
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/redoc</code> - Alternative API documentation
                </div>
            </div>
        </div>

        <script>
            console.log('Script loaded!');

            // Function to download spreadsheet
            async function downloadSpreadsheet(topic, platformsStr, format = 'excel') {
                const platforms = platformsStr.split(',');
                const numResults = parseInt(document.getElementById('num_results').value);
                const searchType = document.getElementById('search_type').value;

                const formData = {
                    topic: topic,
                    num_results: numResults,
                    search_type: searchType,
                    platforms: platforms,
                    export_format: format,
                };

                try {
                    const response = await fetch('/search-and-aggregate/export', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });

                    if (!response.ok) {
                        const data = await response.json();
                        alert('Download failed: ' + (data.detail || 'Unknown error'));
                        return;
                    }

                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;

                    // Set correct filename based on format
                    let filename;
                    if (format === 'csv') {
                        filename = topic.replace(/ /g, '_') + '_social_media.csv';
                    } else if (format === 'pdf') {
                        filename = topic.replace(/ /g, '_') + '_report.pdf';
                    } else {
                        filename = topic.replace(/ /g, '_') + '_social_media.xlsx';
                    }

                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    a.remove();
                } catch (err) {
                    alert('Download failed: ' + err.message);
                }
            }

            function copyToClipboard(textareaId) {
                const textarea = document.getElementById(textareaId);
                textarea.select();
                document.execCommand('copy');
                alert('Copied to clipboard!');
            }

            document.getElementById('topicForm').addEventListener('submit', async (e) => {
                console.log('Form submitted!');
                e.preventDefault();
                console.log('Default prevented!');

                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const error = document.getElementById('error');

                // Hide previous results
                result.style.display = 'none';
                error.style.display = 'none';

                // Show loading
                loading.style.display = 'block';
                loading.textContent = '⏳ Researching topic and generating content... This may take 30-60 seconds.';
                submitBtn.disabled = true;

                // Get selected platforms
                const platformCheckboxes = document.querySelectorAll('input[name="platforms"]:checked');
                const platforms = Array.from(platformCheckboxes).map(cb => cb.value);

                // Get form data
                const topic = document.getElementById('topic').value;
                const exportFormat = document.getElementById('export_format').value;
                const formData = {
                    topic: topic,
                    num_results: parseInt(document.getElementById('num_results').value),
                    search_type: document.getElementById('search_type').value,
                    platforms: platforms,
                    export_format: exportFormat === 'json' ? 'csv' : exportFormat,
                };

                try {
                    let endpoint = '/search-and-aggregate';

                    // Use export endpoint for CSV/Excel
                    if (exportFormat !== 'json') {
                        endpoint = '/search-and-aggregate/export';
                    }

                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });

                    // Handle file downloads
                    if (exportFormat !== 'json') {
                        if (!response.ok) {
                            const data = await response.json();
                            throw new Error(data.detail || 'Failed to generate export');
                        }

                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${topic}_social_media.${exportFormat}`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        a.remove();

                        loading.style.display = 'none';
                        submitBtn.disabled = false;

                        result.innerHTML = `
                            <h2>✅ Success!</h2>
                            <p>Your ${exportFormat.toUpperCase()} file has been downloaded.</p>
                            <p><strong>Topic:</strong> ${topic}</p>
                            <p><strong>Articles Processed:</strong> ${formData.num_results}</p>
                        `;
                        result.style.display = 'block';
                        return;
                    }

                    // Handle JSON response
                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.detail || 'Failed to process topic');
                    }

                    if (data.success) {
                        // Display results
                        const resultData = data.data;

                        let html = `
                            <h2>📊 Research Results: ${topic}</h2>
                            <p style="color: #666; margin-bottom: 20px;">
                                Analyzed ${resultData.successful_summaries} articles and generated social media content
                            </p>

                            <div class="summary">
                                <h3>📝 Master Summary (Based on All ${resultData.successful_summaries} Articles)</h3>
                                <p style="white-space: pre-wrap;">${resultData.master_summary}</p>
                            </div>
                        `;

                        // Display social media posts
                        if (resultData.social_media_posts) {
                            html += '<div class="key-points"><h3>📱 Social Media Posts (Ready to Publish)</h3>';
                            html += '<p style="color: #666; font-size: 14px; margin-bottom: 15px;">These posts are generated from insights across all articles:</p>';

                            for (const [platform, post] of Object.entries(resultData.social_media_posts)) {
                                // Format with newlines preserved
                                const formattedPost = post.replace(/\\n/g, '<br>');
                                const postId = 'post_' + platform;
                                html += `
                                    <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #1a73e8;">
                                        <strong style="font-size: 16px;">${platform.toUpperCase()}</strong>
                                        <button onclick="copyToClipboard('${postId}')"
                                                style="float: right; padding: 5px 10px; background: #1a73e8; color: white; border: none; border-radius: 3px; cursor: pointer;">
                                            Copy
                                        </button>
                                        <textarea id="${postId}" style="position: absolute; left: -9999px;">${post}</textarea>
                                        <p style="margin-top: 10px; white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">${formattedPost}</p>
                                        <small style="color: #666;">${post.length} characters</small>
                                    </div>
                                `;
                            }

                            html += '</div>';
                        }

                        // Display article summaries in collapsible section
                        if (resultData.summaries && resultData.summaries.length > 0) {
                            const successfulSummaries = resultData.summaries.filter(s => s.success);
                            html += `
                                <div class="key-points">
                                    <h3>📰 Source Articles (${successfulSummaries.length})</h3>
                                    <details>
                                        <summary style="cursor: pointer; padding: 10px; background: #f0f7ff; border-radius: 5px; margin-bottom: 15px;">
                                            Click to view individual article summaries
                                        </summary>
                            `;

                            successfulSummaries.forEach((summary, idx) => {
                                html += `
                                    <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 5px; border-left: 3px solid #ddd;">
                                        <strong>Article ${idx + 1}:</strong> ${summary.data.title}<br>
                                        <small><a href="${summary.url}" target="_blank" style="color: #1a73e8;">${summary.url}</a></small>
                                        <p style="margin-top: 10px; color: #333;">${summary.data.summary}</p>
                                    </div>
                                `;
                            });

                            html += '</details></div>';
                        }

                        // Add download button
                        html += `
                            <div style="margin-top: 30px; padding: 20px; background: #f0f7ff; border-radius: 5px; text-align: center;">
                                <h3>📥 Download Complete Report</h3>
                                <p style="color: #666; margin-bottom: 15px;">Get all articles, summaries, and social media posts</p>
                                <button onclick="downloadSpreadsheet('${topic}', '${platforms.join(',')}')"
                                        style="padding: 12px 30px; background: #1a73e8; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin: 5px;">
                                    📊 Excel
                                </button>
                                <button onclick="downloadSpreadsheet('${topic}', '${platforms.join(',')}', 'csv')"
                                        style="padding: 12px 30px; background: #34a853; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin: 5px;">
                                    📄 CSV
                                </button>
                                <button onclick="downloadSpreadsheet('${topic}', '${platforms.join(',')}', 'pdf')"
                                        style="padding: 12px 30px; background: #ea4335; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin: 5px;">
                                    📕 PDF
                                </button>
                            </div>
                        `;

                        result.innerHTML = html;
                        result.style.display = 'block';
                    } else {
                        throw new Error(data.error || 'Processing failed');
                    }
                } catch (err) {
                    error.textContent = '❌ Error: ' + err.message;
                    error.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                    submitBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Web Summarizer API",
        "version": "1.0.0",
        "gemini_configured": agent is not None
    }


@app.post("/summarize", response_model=SummaryResponse)
async def summarize_url(request: SummarizeURLRequest):
    """
    Summarize a web page from URL

    Returns structured summary with key points, citations, and metadata.
    """
    if agent is None:
        raise HTTPException(
            status_code=500,
            detail="Agent not initialized. Please set GEMINI_API_KEY in .env file"
        )

    try:
        # Convert to string for agent
        url = str(request.url)

        # Summarize
        response = agent.summarize_url(
            url=url,
            max_summary_sentences=request.max_summary_sentences,
            num_key_points=request.num_key_points,
            include_citations=request.include_citations,
            model=request.model,
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(e)}"
        )


@app.post("/summarize/advanced", response_model=SummaryResponse)
async def summarize_advanced(request: AdvancedSummarizeRequest):
    """
    Advanced summarization with full configuration options

    Allows complete control over summarization options via SummaryOptions model.
    """
    if agent is None:
        raise HTTPException(
            status_code=500,
            detail="Agent not initialized. Please set GEMINI_API_KEY in .env file"
        )

    try:
        # Create full request
        summary_request = SummaryRequest(
            url=request.url,
            options=request.options
        )

        # Summarize
        response = agent.summarize(summary_request)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(e)}"
        )


@app.post("/aggregate-topic")
async def aggregate_topic(request: TopicAggregatorRequest):
    """
    Aggregate summaries from multiple URLs for a specific topic
    and generate social media posts

    Returns aggregated data with social media content
    """
    if topic_aggregator is None:
        raise HTTPException(
            status_code=500,
            detail="Agent not initialized. Please set GEMINI_API_KEY in .env file"
        )

    try:
        # Aggregate content
        result = topic_aggregator.aggregate_topic(
            topic=request.topic,
            urls=request.urls,
            platforms=request.platforms,
            max_workers=request.max_workers,
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Topic aggregation failed: {str(e)}"
        )


@app.post("/aggregate-topic/export")
async def aggregate_topic_export(request: TopicAggregatorRequest):
    """
    Aggregate summaries and export to spreadsheet (CSV or Excel)

    Returns downloadable file
    """
    if topic_aggregator is None or spreadsheet_generator is None:
        raise HTTPException(
            status_code=500,
            detail="Agent not initialized. Please set GEMINI_API_KEY in .env file"
        )

    try:
        # Aggregate content
        result = topic_aggregator.aggregate_topic(
            topic=request.topic,
            urls=request.urls,
            platforms=request.platforms,
            max_workers=request.max_workers,
        )

        # Generate spreadsheet
        export_format = request.export_format.lower()

        if export_format == "csv":
            # Generate CSV
            csv_content = spreadsheet_generator.generate_csv(
                result,
                output_path=None,
                include_metadata=True,
            )

            # Return as downloadable file
            output = io.StringIO(csv_content)
            response = StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
            )
            response.headers["Content-Disposition"] = f"attachment; filename={request.topic}_social_media.csv"
            return response

        elif export_format == "excel":
            # For Excel, we need to save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx') as tmp:
                tmp_path = tmp.name

            spreadsheet_generator.generate_excel(
                result,
                output_path=tmp_path,
                include_metadata=True,
            )

            # Read and return the file
            with open(tmp_path, 'rb') as f:
                excel_content = f.read()

            # Clean up temp file
            os.unlink(tmp_path)

            response = StreamingResponse(
                io.BytesIO(excel_content),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response.headers["Content-Disposition"] = f"attachment; filename={request.topic}_social_media.xlsx"
            return response

        elif export_format == "pdf":
            # For PDF, we need to save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pdf') as tmp:
                tmp_path = tmp.name

            spreadsheet_generator.generate_pdf(
                result,
                output_path=tmp_path,
                include_metadata=True,
            )

            # Read and return the file
            with open(tmp_path, 'rb') as f:
                pdf_content = f.read()

            # Clean up temp file
            os.unlink(tmp_path)

            response = StreamingResponse(
                io.BytesIO(pdf_content),
                media_type="application/pdf",
            )
            response.headers["Content-Disposition"] = f"attachment; filename={request.topic}_report.pdf"
            return response

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported export format: {export_format}. Use 'csv', 'excel', or 'pdf'"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@app.post("/search-and-aggregate")
async def search_and_aggregate(request: TopicSearchRequest):
    """
    Search the web for a topic, then aggregate summaries and generate social media posts

    Just provide a topic - we'll find the URLs automatically!
    """
    if web_searcher is None or topic_aggregator is None:
        raise HTTPException(
            status_code=500,
            detail="Services not initialized. Please set GEMINI_API_KEY in .env file"
        )

    try:
        # Search for articles
        if request.search_type == "news":
            search_results = web_searcher.search_news(
                query=request.topic,
                num_results=request.num_results,
            )
        else:
            search_results = web_searcher.search(
                query=request.topic,
                num_results=request.num_results,
            )

        # Filter by domain if specified
        if request.allowed_domains or request.blocked_domains:
            search_results = web_searcher.filter_by_domain(
                search_results,
                allowed_domains=request.allowed_domains,
                blocked_domains=request.blocked_domains,
            )

        # Extract URLs
        urls = [result["url"] for result in search_results]

        if not urls:
            raise HTTPException(
                status_code=404,
                detail="No search results found for the topic"
            )

        # Aggregate summaries
        result = topic_aggregator.aggregate_topic(
            topic=request.topic,
            urls=urls,
            platforms=request.platforms,
            max_workers=request.max_workers,
        )

        # Add search results metadata
        result["search_results_count"] = len(search_results)
        result["search_type"] = request.search_type

        return {
            "success": True,
            "data": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search and aggregation failed: {str(e)}"
        )


@app.post("/search-and-aggregate/export")
async def search_and_aggregate_export(request: TopicSearchRequest):
    """
    Search for a topic, aggregate summaries, and export to spreadsheet

    The easiest way - just provide a topic and get a spreadsheet!
    """
    if web_searcher is None or topic_aggregator is None or spreadsheet_generator is None:
        raise HTTPException(
            status_code=500,
            detail="Services not initialized. Please set GEMINI_API_KEY in .env file"
        )

    try:
        # Search for articles
        if request.search_type == "news":
            search_results = web_searcher.search_news(
                query=request.topic,
                num_results=request.num_results,
            )
        else:
            search_results = web_searcher.search(
                query=request.topic,
                num_results=request.num_results,
            )

        # Filter by domain if specified
        if request.allowed_domains or request.blocked_domains:
            search_results = web_searcher.filter_by_domain(
                search_results,
                allowed_domains=request.allowed_domains,
                blocked_domains=request.blocked_domains,
            )

        # Extract URLs
        urls = [result["url"] for result in search_results]

        if not urls:
            raise HTTPException(
                status_code=404,
                detail="No search results found for the topic"
            )

        # Aggregate summaries
        result = topic_aggregator.aggregate_topic(
            topic=request.topic,
            urls=urls,
            platforms=request.platforms,
            max_workers=request.max_workers,
        )

        # Generate spreadsheet
        export_format = request.export_format.lower()

        if export_format == "csv":
            csv_content = spreadsheet_generator.generate_csv(
                result,
                output_path=None,
                include_metadata=True,
            )

            response = StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
            )
            response.headers["Content-Disposition"] = f"attachment; filename={request.topic}_social_media.csv"
            return response

        elif export_format == "excel":
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx') as tmp:
                tmp_path = tmp.name

            spreadsheet_generator.generate_excel(
                result,
                output_path=tmp_path,
                include_metadata=True,
            )

            with open(tmp_path, 'rb') as f:
                excel_content = f.read()

            os.unlink(tmp_path)

            response = StreamingResponse(
                io.BytesIO(excel_content),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response.headers["Content-Disposition"] = f"attachment; filename={request.topic}_social_media.xlsx"
            return response

        elif export_format == "pdf":
            # For PDF, we need to save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pdf') as tmp:
                tmp_path = tmp.name

            spreadsheet_generator.generate_pdf(
                result,
                output_path=tmp_path,
                include_metadata=True,
            )

            # Read and return the file
            with open(tmp_path, 'rb') as f:
                pdf_content = f.read()

            # Clean up temp file
            os.unlink(tmp_path)

            response = StreamingResponse(
                io.BytesIO(pdf_content),
                media_type="application/pdf",
            )
            response.headers["Content-Disposition"] = f"attachment; filename={request.topic}_report.pdf"
            return response

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported export format: {export_format}. Use 'csv', 'excel', or 'pdf'"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Web Summarizer API...")
    print("📖 Open http://localhost:8000 in your browser")
    print("📚 API docs: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
