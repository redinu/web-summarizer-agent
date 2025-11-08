# Quick Start Guide

Get up and running with Web Summarizer Agent in 5 minutes!

## Step 1: Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements-dev.txt
```

## Step 2: Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get your API key from: https://console.anthropic.com/
```

Your `.env` file should look like:
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

## Step 3: Test Installation

Create a file `test_agent.py`:

```python
from web_summarizer import WebSummarizerAgent
import os
from dotenv import load_dotenv

load_dotenv()

agent = WebSummarizerAgent()
response = agent.summarize_url("https://www.anthropic.com")

if response.success:
    print("✅ Agent working!")
    print(f"Title: {response.data.title}")
    print(f"Summary: {response.data.summary}")
else:
    print(f"❌ Error: {response.error}")
```

Run it:
```bash
python test_agent.py
```

## Step 4: Run Examples

```bash
# Basic usage
python examples/basic_usage.py

# Advanced configuration
python examples/advanced_usage.py

# Batch processing
python examples/batch_processing.py
```

## Step 5: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=web_summarizer

# Run specific test
pytest tests/test_models.py -v
```

## Common Issues

### Issue: "ANTHROPIC_API_KEY not set"
**Solution:** Make sure you've created a `.env` file with your API key.

### Issue: "Module not found: web_summarizer"
**Solution:** Install in development mode:
```bash
pip install -e .
```

### Issue: "Insufficient content extracted"
**Solution:** Some websites may have paywalls or JavaScript-heavy content. Try a different URL.

## Next Steps

1. Read the full [README.md](README.md) for detailed API documentation
2. Check out [USER_STORIES.md](USER_STORIES.md) for feature roadmap
3. Explore the code in `src/web_summarizer/`
4. Build your own integration!

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review the examples in `examples/`
- Look at test cases in `tests/` for usage patterns

---

Happy summarizing! 🚀
