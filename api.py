"""
FastAPI REST API for Web Summarizer Agent
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web_summarizer import WebSummarizerAgent
from web_summarizer.models import SummaryOptions, SummaryRequest, SummaryResponse

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
except ValueError as e:
    print(f"⚠️ Warning: {e}")
    print("Please set GEMINI_API_KEY in your .env file")
    agent = None


# Request models
class SummarizeURLRequest(BaseModel):
    """Simple request model for URL summarization"""
    url: HttpUrl
    max_summary_sentences: Optional[int] = 4
    num_key_points: Optional[int] = 5
    include_citations: Optional[bool] = False
    model: Optional[str] = "gemini-1.5-flash"


class AdvancedSummarizeRequest(BaseModel):
    """Advanced request model with full options"""
    url: HttpUrl
    options: Optional[SummaryOptions] = None


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

            <form id="summarizeForm">
                <div class="form-group">
                    <label for="url">URL to Summarize</label>
                    <input type="text" id="url" name="url"
                           placeholder="https://blog.google/technology/ai/google-gemini-ai/"
                           value="https://blog.google/technology/ai/google-gemini-ai/" required>
                </div>

                <div class="form-group">
                    <label for="model">AI Model</label>
                    <select id="model" name="model">
                        <option value="gemini-1.5-flash" selected>Gemini 1.5 Flash (Fast & Cheap)</option>
                        <option value="gemini-1.5-pro">Gemini 1.5 Pro (Best Quality)</option>
                        <option value="gemini-1.0-pro">Gemini 1.0 Pro (Stable)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="max_summary_sentences">Max Summary Sentences</label>
                    <input type="number" id="max_summary_sentences" name="max_summary_sentences"
                           value="4" min="1" max="10">
                </div>

                <div class="form-group">
                    <label for="num_key_points">Number of Key Points</label>
                    <input type="number" id="num_key_points" name="num_key_points"
                           value="5" min="1" max="10">
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" id="include_citations" name="include_citations">
                        Include Citations
                    </label>
                </div>

                <button type="submit" id="submitBtn">Summarize</button>
            </form>

            <div class="loading" id="loading">
                ⏳ Summarizing content... This may take a few seconds.
            </div>

            <div class="error" id="error"></div>

            <div class="result" id="result">
                <h2 id="resultTitle"></h2>
                <div class="summary">
                    <h3>📝 Summary</h3>
                    <p id="summary"></p>
                </div>
                <div class="key-points">
                    <h3>🔑 Key Points</h3>
                    <ul id="keyPoints"></ul>
                </div>
                <div id="citationsDiv" style="display: none;">
                    <h3>💬 Citations</h3>
                    <ul id="citations"></ul>
                </div>
                <div class="metadata">
                    <strong>Metadata:</strong><br>
                    Category: <span id="category"></span><br>
                    Processing Time: <span id="processingTime"></span>ms<br>
                    Tokens Used: <span id="tokensUsed"></span><br>
                    Model: <span id="modelUsed"></span><br>
                    Content Length: <span id="contentLength"></span> chars
                </div>
            </div>

            <div class="endpoints">
                <h3>📡 API Endpoints</h3>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/</code> - This page
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/health</code> - Health check
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/summarize</code> - Summarize a URL
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
            document.getElementById('summarizeForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const error = document.getElementById('error');

                // Hide previous results
                result.style.display = 'none';
                error.style.display = 'none';

                // Show loading
                loading.style.display = 'block';
                submitBtn.disabled = true;

                // Get form data
                const formData = {
                    url: document.getElementById('url').value,
                    model: document.getElementById('model').value,
                    max_summary_sentences: parseInt(document.getElementById('max_summary_sentences').value),
                    num_key_points: parseInt(document.getElementById('num_key_points').value),
                    include_citations: document.getElementById('include_citations').checked
                };

                try {
                    const response = await fetch('/summarize', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.detail || 'Failed to summarize');
                    }

                    if (data.success) {
                        // Display results
                        document.getElementById('resultTitle').textContent = data.data.title || 'Summary';
                        document.getElementById('summary').textContent = data.data.summary;
                        document.getElementById('category').textContent = data.data.category || 'N/A';

                        // Key points
                        const keyPointsList = document.getElementById('keyPoints');
                        keyPointsList.innerHTML = '';
                        data.data.key_points.forEach(point => {
                            const li = document.createElement('li');
                            li.textContent = point;
                            keyPointsList.appendChild(li);
                        });

                        // Citations
                        if (data.data.citations && data.data.citations.length > 0) {
                            document.getElementById('citationsDiv').style.display = 'block';
                            const citationsList = document.getElementById('citations');
                            citationsList.innerHTML = '';
                            data.data.citations.forEach(citation => {
                                const li = document.createElement('li');
                                li.textContent = `"${citation}"`;
                                citationsList.appendChild(li);
                            });
                        } else {
                            document.getElementById('citationsDiv').style.display = 'none';
                        }

                        // Metadata
                        document.getElementById('processingTime').textContent = data.data.metadata.processing_time_ms;
                        document.getElementById('tokensUsed').textContent = data.data.metadata.tokens_used;
                        document.getElementById('modelUsed').textContent = data.data.metadata.model_used;
                        document.getElementById('contentLength').textContent = data.data.metadata.content_length;

                        result.style.display = 'block';
                    } else {
                        throw new Error(data.error || 'Summarization failed');
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


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Web Summarizer API...")
    print("📖 Open http://localhost:8000 in your browser")
    print("📚 API docs: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
