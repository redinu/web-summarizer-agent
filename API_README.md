# Web Summarizer API Documentation

## Quick Start

### 1. Start the API Server

```bash
# Make sure you have GEMINI_API_KEY in your .env file
python3 api.py
```

The server will start at **http://localhost:8000**

### 2. Open in Browser

Open your browser and go to:
- **http://localhost:8000** - Interactive web interface
- **http://localhost:8000/docs** - Swagger API documentation
- **http://localhost:8000/redoc** - ReDoc API documentation

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running and configured properly.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Web Summarizer API",
  "version": "1.0.0",
  "gemini_configured": true
}
```

### 2. Summarize URL (Simple)

**POST** `/summarize`

Summarize a webpage with simple options.

**Request Body:**
```json
{
  "url": "https://blog.google/technology/ai/google-gemini-ai/",
  "max_summary_sentences": 4,
  "num_key_points": 5,
  "include_citations": false,
  "model": "gemini-1.5-flash"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://blog.google/technology/ai/google-gemini-ai/",
    "max_summary_sentences": 4,
    "num_key_points": 5,
    "include_citations": false,
    "model": "gemini-1.5-flash"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://blog.google/technology/ai/google-gemini-ai/",
    "title": "Article Title",
    "summary": "A concise summary of the content...",
    "key_points": [
      "First key point",
      "Second key point",
      "Third key point"
    ],
    "citations": null,
    "category": "Technology",
    "metadata": {
      "timestamp": "2025-11-08T12:00:00Z",
      "tokens_used": 1500,
      "processing_time_ms": 2500,
      "model_used": "gemini-1.5-flash",
      "content_length": 5000,
      "extraction_method": "readability"
    }
  },
  "error": null,
  "error_code": null
}
```

### 3. Advanced Summarization

**POST** `/summarize/advanced`

Summarize with full configuration control.

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "options": {
    "max_summary_sentences": 6,
    "num_key_points": 8,
    "include_citations": true,
    "model": "gemini-1.5-pro",
    "timeout_seconds": 30
  }
}
```

## JavaScript/Browser Usage

### Fetch API Example

```javascript
async function summarizeURL(url) {
  const response = await fetch('http://localhost:8000/summarize', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url: url,
      max_summary_sentences: 4,
      num_key_points: 5,
      include_citations: false,
      model: 'gemini-1.5-flash'
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Summary:', data.data.summary);
    console.log('Key Points:', data.data.key_points);
  } else {
    console.error('Error:', data.error);
  }

  return data;
}

// Use it
summarizeURL('https://blog.google/technology/ai/');
```

### jQuery Example

```javascript
$.ajax({
  url: 'http://localhost:8000/summarize',
  type: 'POST',
  contentType: 'application/json',
  data: JSON.stringify({
    url: 'https://blog.google/technology/ai/',
    model: 'gemini-1.5-flash'
  }),
  success: function(data) {
    if (data.success) {
      console.log('Summary:', data.data.summary);
    }
  },
  error: function(xhr, status, error) {
    console.error('Error:', error);
  }
});
```

## Python Client Example

```python
import requests

url = "http://localhost:8000/summarize"

payload = {
    "url": "https://blog.google/technology/ai/",
    "max_summary_sentences": 4,
    "num_key_points": 5,
    "model": "gemini-1.5-flash"
}

response = requests.post(url, json=payload)
data = response.json()

if data['success']:
    print(f"Summary: {data['data']['summary']}")
    print(f"Key Points: {data['data']['key_points']}")
else:
    print(f"Error: {data['error']}")
```

## Available Models

| Model | Speed | Cost | Quality | Use Case |
|-------|-------|------|---------|----------|
| `gemini-1.5-flash` | ⚡⚡⚡ | 💰 | ⭐⭐⭐ | Default, fast, cheap |
| `gemini-1.5-pro` | ⚡⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | Best quality |
| `gemini-1.0-pro` | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ | Stable, proven |

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "data": null,
  "error": "Error message here",
  "error_code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_URL` | URL format is invalid | Check URL format |
| `NOT_FOUND` | Page not found (404) | Verify URL exists |
| `FORBIDDEN` | Access forbidden (403) | URL may block bots |
| `TIMEOUT` | Request timeout | Try again or increase timeout |
| `INSUFFICIENT_CONTENT` | Not enough text | Page may be too short |
| `AI_TIMEOUT` | AI request timeout | Try again |
| `AI_API_ERROR` | Gemini API error | Check API key/quota |

## CORS Configuration

The API has CORS enabled by default to allow browser access from any origin.

**For production**, update the CORS settings in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Deployment

### Development

```bash
python3 api.py
```

### Production with Uvicorn

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GEMINI_API_KEY=""

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t web-summarizer-api .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key web-summarizer-api
```

## Rate Limiting

The API currently has no rate limiting. For production, consider adding:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/summarize")
@limiter.limit("10/minute")
async def summarize_url(request: Request, ...):
    ...
```

## Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Test Summarize Endpoint

```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://blog.google/technology/ai/"}'
```

### Load Testing with Apache Bench

```bash
ab -n 100 -c 10 -p request.json -T application/json http://localhost:8000/summarize
```

## Monitoring

### Prometheus Metrics

Add prometheus metrics:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Access metrics at: `http://localhost:8000/metrics`

## Security Best Practices

1. **API Key Protection**
   - Never commit `.env` file
   - Use environment variables
   - Rotate keys regularly

2. **Input Validation**
   - All inputs validated by Pydantic
   - URL format checked
   - Rate limiting recommended

3. **CORS**
   - Restrict origins in production
   - Don't use `allow_origins=["*"]`

4. **HTTPS**
   - Always use HTTPS in production
   - Use reverse proxy (nginx/caddy)

## Troubleshooting

### API won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use different port
uvicorn api:app --port 8080
```

### "GEMINI_API_KEY must be set"

```bash
# Check .env file exists
cat .env | grep GEMINI_API_KEY

# Or set manually
export GEMINI_API_KEY=your_key_here
python3 api.py
```

### CORS errors in browser

Check browser console. If you see CORS errors, the API CORS is configured to allow all origins. The issue may be:
- API not running
- Wrong URL
- Browser extension blocking

## Support

- **Interactive Docs:** http://localhost:8000/docs
- **API Documentation:** This file
- **GitHub Issues:** For bug reports

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start API | `python3 api.py` |
| View Docs | Open http://localhost:8000/docs |
| Test UI | Open http://localhost:8000 |
| Health Check | `curl http://localhost:8000/health` |
| Stop Server | `Ctrl+C` |

**Ready to summarize!** 🚀
