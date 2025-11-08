# Multi-stage build for Web Summarizer Agent
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x api.py || true

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Environment variables with defaults
ENV GEMINI_API_KEY="" \
    DEFAULT_MODEL="models/gemini-2.5-flash" \
    MAX_TOKENS=2048 \
    TIMEOUT_SECONDS=15 \
    MAX_CONTENT_LENGTH=50000 \
    USER_AGENT="WebSummarizerAgent/1.0.0" \
    MAX_REDIRECTS=3 \
    REQUEST_TIMEOUT=10

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Run the API server
CMD ["python3", "api.py"]
