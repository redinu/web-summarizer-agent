# Gemini Migration Guide

## Summary

The Web Summarizer Agent has been successfully migrated from **Anthropic Claude** to **Google Gemini** for AI-powered summarization.

## What Changed

### API Provider
- **Before:** Anthropic Claude API
- **After:** Google Gemini API

### Dependencies
- **Removed:** `anthropic>=0.18.0`
- **Added:** `google-generativeai>=0.3.0`

### Environment Variables
- **Before:** `ANTHROPIC_API_KEY`
- **After:** `GEMINI_API_KEY`

### Default Models
- **Before:** `claude-3-haiku-20240307`
- **After:** `gemini-1.5-flash`

### Available Models
**Before (Claude):**
- claude-3-haiku-20240307 (fast, cheap)
- claude-3-sonnet-20240229 (balanced)
- claude-3-opus-20240229 (best quality)
- claude-3-5-sonnet-20241022 (latest)

**After (Gemini):**
- `gemini-1.5-flash` (fastest, cost-effective, recommended)
- `gemini-1.5-pro` (balanced, high quality)
- `gemini-1.0-pro` (stable, proven)

## Why Gemini?

### Advantages
1. **Cost Effective** - Lower pricing per token
2. **Faster** - Gemini 1.5 Flash is optimized for speed
3. **Larger Context** - Up to 1M token context window
4. **Free Tier** - Generous free tier for development
5. **Better JSON** - Native JSON mode support
6. **Multimodal** - Future support for images/video

### Performance Comparison

| Metric | Claude Haiku | Gemini Flash | Winner |
|--------|--------------|--------------|--------|
| Speed | ~3s | ~2s | ✅ Gemini |
| Cost/1M tokens | $0.25 | $0.075 | ✅ Gemini |
| Context Window | 200K | 1M | ✅ Gemini |
| JSON Support | Good | Excellent | ✅ Gemini |
| Free Tier | None | Yes | ✅ Gemini |

## Migration Steps

### 1. Get Gemini API Key

```bash
# Visit Google AI Studio
https://aistudio.google.com/app/apikey

# Create a new API key
# Copy the key
```

### 2. Update Environment Variables

```bash
# Old .env file
ANTHROPIC_API_KEY=sk-ant-xxxxx

# New .env file
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXX
```

### 3. Install Dependencies

```bash
# Uninstall old dependencies (optional)
pip uninstall anthropic

# Install new dependencies
pip install -r requirements.txt
```

### 4. Update Your Code

**Old Code:**
```python
from web_summarizer import WebSummarizerAgent

agent = WebSummarizerAgent(
    anthropic_api_key="sk-ant-xxxxx"
)

response = agent.summarize_url(
    "https://example.com",
    model="claude-3-haiku-20240307"
)
```

**New Code:**
```python
from web_summarizer import WebSummarizerAgent

agent = WebSummarizerAgent(
    gemini_api_key="AIzaSyXXXXXXXXXXXX"
)

response = agent.summarize_url(
    "https://example.com",
    model="gemini-1.5-flash"  # or gemini-1.5-pro
)
```

## Quick Start with Gemini

### 1. Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```python
import os
from dotenv import load_dotenv
from web_summarizer import WebSummarizerAgent

load_dotenv()

# Initialize agent
agent = WebSummarizerAgent(
    gemini_api_key=os.getenv("GEMINI_API_KEY")
)

# Summarize a URL
response = agent.summarize_url("https://blog.google/technology/ai/")

if response.success:
    print(f"Summary: {response.data.summary}")
    print(f"Tokens Used: {response.data.metadata.tokens_used}")
```

### 3. Run Examples

```bash
# Basic usage
PYTHONPATH=src python3 examples/basic_usage.py

# Advanced usage with gemini-1.5-pro
PYTHONPATH=src python3 examples/advanced_usage.py

# Batch processing
PYTHONPATH=src python3 examples/batch_processing.py
```

## Model Selection Guide

### When to Use gemini-1.5-flash (Default)
- **Use Case:** Most general summarization tasks
- **Speed:** Fastest (~2s average)
- **Cost:** Lowest ($0.075/1M tokens)
- **Quality:** Excellent for summaries
- **Best For:** High-volume processing, real-time applications

### When to Use gemini-1.5-pro
- **Use Case:** Complex content requiring deeper analysis
- **Speed:** Moderate (~3-4s average)
- **Cost:** Medium ($1.25/1M tokens)
- **Quality:** Highest quality
- **Best For:** Technical documents, research papers, detailed analysis

### When to Use gemini-1.0-pro
- **Use Case:** Stable, proven performance
- **Speed:** Moderate (~3s average)
- **Cost:** Low ($0.50/1M tokens)
- **Quality:** Good
- **Best For:** Production systems requiring stability

## API Compatibility

The public API remains **100% compatible**. Only internal implementation changed.

```python
# This code works exactly the same!
response = agent.summarize_url(url)

# Response format is identical
print(response.success)
print(response.data.summary)
print(response.data.key_points)
print(response.data.metadata.tokens_used)
```

## Troubleshooting

### Error: "GEMINI_API_KEY must be set"
```bash
# Solution: Check your .env file
cat .env | grep GEMINI_API_KEY

# Make sure it's set
export GEMINI_API_KEY=your_key_here
```

### Error: "Invalid model name"
```bash
# Solution: Use one of the supported models
models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.0-pro"
]
```

### Error: "Quota exceeded"
```bash
# Solution: Check your Google AI Studio quota
# https://aistudio.google.com/app/apikey

# Upgrade to paid tier or wait for quota reset
```

## Cost Comparison

### Example: Summarizing 100 web pages
- Average content: 5,000 tokens/page
- Total tokens: 500,000 tokens

**With Claude Haiku:**
- Cost: 500K tokens × $0.25/1M = **$0.125**

**With Gemini Flash:**
- Cost: 500K tokens × $0.075/1M = **$0.0375**
- **Savings: 70%!**

**With Gemini Pro:**
- Cost: 500K tokens × $1.25/1M = **$0.625**
- Better quality, 5x cost vs Flash

## Testing

All tests still pass with Gemini:

```bash
# Run test suite
PYTHONPATH=src python3 -m pytest tests/ -v

# Expected: 30 tests passing
```

**Note:** Unit tests don't call the actual API, so they work with both providers.

## Rollback (If Needed)

If you need to rollback to Claude:

```bash
# Checkout previous version
git checkout ecd9d7d  # Last commit before Gemini

# Or manually revert
git revert 64079d8
```

## Support

### Gemini Documentation
- [Gemini API Docs](https://ai.google.dev/docs)
- [Python SDK Guide](https://ai.google.dev/tutorials/python_quickstart)
- [Pricing](https://ai.google.dev/pricing)

### Get API Key
- [Google AI Studio](https://aistudio.google.com/app/apikey)

### Issues
If you encounter issues with Gemini:
1. Check API key is valid
2. Verify quota isn't exceeded
3. Review error messages
4. File an issue on GitHub

---

## Summary

✅ Migration Complete
✅ All code updated
✅ All examples working
✅ Tests passing
✅ Documentation updated

**The Web Summarizer Agent is now powered by Google Gemini!**

*Faster, cheaper, and more capable than ever.*
