# Deployment Guide - Web Summarizer Agent

This guide covers deploying the Web Summarizer Agent to various platforms and integrating it with MeshCore.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [MeshCore Integration](#meshcore-integration)
5. [Production Configuration](#production-configuration)
6. [Monitoring & Logging](#monitoring--logging)

---

## Quick Start

### 1. Get Your API Key

Get a free Gemini API key at https://aistudio.google.com/app/apikey

### 2. Deploy Locally

```bash
# Clone the repository
git clone https://github.com/redietdagnew/web-summarizer-agent.git
cd web-summarizer-agent

# Set up environment
cp .env.example .env
echo "GEMINI_API_KEY=your_key_here" >> .env

# Install dependencies
pip install -r requirements.txt

# Run the server
python3 api.py
```

Access at: http://localhost:8000

---

## Docker Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Option 2: Docker Run

```bash
docker build -t web-summarizer:latest .

docker run -d \
  --name web-summarizer \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key_here \
  --restart unless-stopped \
  web-summarizer:latest
```

### Docker Hub

```bash
# Pull pre-built image
docker pull redietdagnew/web-summarizer:latest

# Run
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key_here \
  redietdagnew/web-summarizer:latest
```

---

## Cloud Deployment

### AWS ECS

1. **Push image to ECR:**

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t web-summarizer .
docker tag web-summarizer:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/web-summarizer:latest

# Push
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/web-summarizer:latest
```

2. **Create ECS Task Definition:**

```json
{
  "family": "web-summarizer",
  "containerDefinitions": [
    {
      "name": "web-summarizer",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/web-summarizer:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GEMINI_API_KEY",
          "value": "your_key_here"
        }
      ]
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy web-summarizer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here \
  --port 8000
```

### Heroku

```bash
# Create app
heroku create web-summarizer-agent

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key_here

# Deploy
git push heroku main

# Scale
heroku ps:scale web=1
```

### Railway

1. Connect your GitHub repository to Railway
2. Add environment variable: `GEMINI_API_KEY`
3. Deploy automatically on push

### Render

1. Create a new Web Service
2. Connect your repository
3. Set environment variables:
   - `GEMINI_API_KEY`
4. Deploy

---

## MeshCore Integration

### 1. Register Agent in MeshCore

```bash
# Using MeshCore CLI
meshcore agent register \
  --manifest meshcore.json \
  --name web-summarizer \
  --endpoint http://your-deployment-url:8000
```

### 2. MeshCore Configuration File

Create `meshcore-config.yaml`:

```yaml
agents:
  - name: web-summarizer
    type: utility
    endpoint: http://localhost:8000
    api_key: ${GEMINI_API_KEY}
    capabilities:
      - web-fetching
      - content-extraction
      - summarization
    inputs:
      - url
      - text
    outputs:
      - summary
      - key_points
      - citations
    timeout: 30s
    retry:
      max_attempts: 3
      backoff: exponential
```

### 3. Multi-Agent Workflow Example

```python
from meshcore import MeshCore

# Initialize MeshCore
mesh = MeshCore()

# Define workflow
workflow = mesh.create_workflow("research-automation")

# Step 1: Summarize articles
summarizer = mesh.get_agent("web-summarizer")
summaries = workflow.add_step(
    agent=summarizer,
    inputs=["https://example.com/article1", "https://example.com/article2"],
    parallel=True
)

# Step 2: Analyze sentiment
sentiment_analyzer = mesh.get_agent("sentiment-analyzer")
sentiments = workflow.add_step(
    agent=sentiment_analyzer,
    inputs=summaries,
    depends_on=[summaries]
)

# Step 3: Generate report
reporter = mesh.get_agent("report-generator")
report = workflow.add_step(
    agent=reporter,
    inputs=[summaries, sentiments],
    depends_on=[summaries, sentiments]
)

# Execute workflow
result = workflow.execute()
```

### 4. Test Integration

```bash
# Health check
curl http://localhost:8000/health

# Test summarization
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## Production Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_production_key

# Optional (recommended for production)
DEFAULT_MODEL=models/gemini-2.5-flash
MAX_TOKENS=2048
TIMEOUT_SECONDS=30
MAX_CONTENT_LENGTH=100000
USER_AGENT=WebSummarizerAgent/1.0.0 (Production)
MAX_REDIRECTS=5
REQUEST_TIMEOUT=15

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/web-summarizer/app.log

# Rate Limiting (if implemented)
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### HTTPS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Monitoring & Logging

### Prometheus Metrics

Add to `requirements.txt`:
```
prometheus-fastapi-instrumentator>=6.0.0
```

Update `api.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

# After creating app
Instrumentator().instrument(app).expose(app)
```

Access metrics at: `http://localhost:8000/metrics`

### Grafana Dashboard

Import dashboard from `monitoring/grafana-dashboard.json`

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check with monitoring
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

### Logging Configuration

Create `logging.conf`:

```ini
[loggers]
keys=root,uvicorn,web_summarizer

[handlers]
keys=console,file

[formatters]
keys=default,json

[logger_root]
level=INFO
handlers=console,file

[logger_uvicorn]
level=INFO
handlers=console,file
qualname=uvicorn
propagate=0

[logger_web_summarizer]
level=INFO
handlers=console,file
qualname=web_summarizer
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=default
args=(sys.stdout,)

[handler_file]
class=handlers.RotatingFileHandler
level=INFO
formatter=json
args=('/var/log/web-summarizer/app.log', 'a', 10485760, 5)

[formatter_default]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_json]
class=pythonjsonlogger.jsonlogger.JsonFormatter
format=%(asctime)s %(name)s %(levelname)s %(message)s
```

### Error Tracking with Sentry

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

---

## Performance Optimization

### 1. Caching

Add Redis caching for frequently accessed URLs:

```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_summary(url: str):
    cached = redis_client.get(f"summary:{url}")
    if cached:
        return json.loads(cached)
    return None

def cache_summary(url: str, summary: dict, ttl: int = 3600):
    redis_client.setex(
        f"summary:{url}",
        ttl,
        json.dumps(summary)
    )
```

### 2. Load Balancing

Use multiple instances behind a load balancer:

```yaml
# docker-compose-scaled.yml
version: '3.8'
services:
  web-summarizer:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    deploy:
      replicas: 3

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web-summarizer
```

### 3. Database for Analytics

Track usage and performance:

```python
# Track summarization requests
db.execute("""
    INSERT INTO summarization_logs
    (url, tokens_used, processing_time_ms, success, timestamp)
    VALUES (?, ?, ?, ?, ?)
""", (url, tokens_used, processing_time, success, datetime.now()))
```

---

## Security Best Practices

1. **API Key Protection**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate keys regularly

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter

   @app.post("/summarize")
   @limiter.limit("10/minute")
   async def summarize_url(request: Request, ...):
       ...
   ```

3. **Input Validation**
   - All inputs validated by Pydantic
   - URL whitelist/blacklist support
   - Content length limits

4. **HTTPS Only**
   - Always use HTTPS in production
   - HSTS headers enabled
   - Secure cookies

---

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
lsof -ti :8000 | xargs kill -9
```

**Docker Build Fails**
```bash
docker system prune -a
docker-compose build --no-cache
```

**API Key Not Working**
```bash
# Test API key
curl -H "x-goog-api-key: YOUR_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

**High Memory Usage**
```bash
# Limit memory in docker-compose.yml
services:
  web-summarizer:
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## Support

- **Documentation**: [README.md](README.md)
- **Issues**: https://github.com/redietdagnew/web-summarizer-agent/issues
- **Email**: support@meshcore.ai
- **Discord**: Join MeshCore Community

---

**Ready for production!** Follow this guide to deploy your Web Summarizer Agent to any platform.
