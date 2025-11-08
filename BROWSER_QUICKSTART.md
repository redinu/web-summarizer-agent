# 🌐 Browser Quick Start Guide

## Test the API in Your Browser - 3 Steps!

### Step 1: Set Your Gemini API Key

```bash
# Create .env file if it doesn't exist
cp .env.example .env

# Edit .env and add your Gemini API key
# Get one free at: https://aistudio.google.com/app/apikey
```

Your `.env` file should look like:
```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXX
```

### Step 2: Start the API Server

```bash
python3 api.py
```

You should see:
```
🚀 Starting Web Summarizer API...
📖 Open http://localhost:8000 in your browser
📚 API docs: http://localhost:8000/docs
```

### Step 3: Open in Browser

Open your web browser and go to:

**http://localhost:8000**

You'll see a beautiful web interface where you can:
1. Enter any URL
2. Choose AI model (Flash, Pro, or 1.0)
3. Customize options
4. Click "Summarize"
5. See results instantly!

---

## What You Can Do

### 1. Interactive Web Interface
- **URL:** http://localhost:8000
- Paste any URL
- Select model and options
- Get instant summaries
- See metadata (tokens, time, cost)

### 2. Swagger API Documentation
- **URL:** http://localhost:8000/docs
- Interactive API testing
- Try all endpoints
- See request/response examples
- Generate code snippets

### 3. ReDoc Documentation
- **URL:** http://localhost:8000/redoc
- Beautiful, searchable docs
- Complete API reference
- Download OpenAPI spec

---

## Example Usage

### Try These URLs:

```
https://blog.google/technology/ai/google-gemini-ai/
https://deepmind.google/technologies/gemini/
https://blog.google/technology/ai/
https://techcrunch.com/latest/
https://www.nytimes.com/section/technology
```

### Test with cURL:

```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://blog.google/technology/ai/",
    "model": "gemini-1.5-flash"
  }'
```

### Test in Browser Console:

Open browser console (F12) and paste:

```javascript
fetch('http://localhost:8000/summarize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    url: 'https://blog.google/technology/ai/',
    model: 'gemini-1.5-flash'
  })
})
.then(r => r.json())
.then(data => console.log(data.data.summary))
```

---

## Troubleshooting

### "Connection refused"
- Check if API is running: `curl http://localhost:8000/health`
- Restart the server: `python3 api.py`

### "GEMINI_API_KEY must be set"
- Check `.env` file exists: `cat .env`
- Make sure key is set: `echo $GEMINI_API_KEY`
- Get free key: https://aistudio.google.com/app/apikey

### CORS errors
- API has CORS enabled for all origins
- Try incognito mode
- Check browser console for details

### Slow responses
- Gemini Flash is fastest (~2s)
- Large pages take longer
- Check your internet connection

---

## Features Demo

### Web Interface Features:
✅ URL input with validation
✅ Model selection dropdown
✅ Adjustable summary length
✅ Key points customization
✅ Optional citations
✅ Real-time loading indicator
✅ Beautiful result display
✅ Error handling
✅ Metadata tracking

### API Features:
✅ RESTful endpoints
✅ JSON request/response
✅ OpenAPI documentation
✅ CORS enabled
✅ Health check
✅ Error codes
✅ Token tracking

---

## Screenshot

When you open http://localhost:8000, you'll see:

```
┌─────────────────────────────────────────┐
│   🤖 Web Summarizer API                 │
│   AI-powered web content summarization  │
│                                         │
│   URL to Summarize:                     │
│   [https://blog.google/...]            │
│                                         │
│   AI Model: [Gemini 1.5 Flash ▼]       │
│                                         │
│   Max Summary Sentences: [4]            │
│   Number of Key Points: [5]             │
│   ☐ Include Citations                   │
│                                         │
│   [Summarize]                           │
└─────────────────────────────────────────┘
```

After clicking "Summarize":

```
┌─────────────────────────────────────────┐
│   📝 Summary                            │
│   Google Gemini is a new AI model...   │
│                                         │
│   🔑 Key Points                         │
│   • First key point                     │
│   • Second key point                    │
│   • Third key point                     │
│                                         │
│   Metadata:                             │
│   Processing Time: 2500ms               │
│   Tokens Used: 1500                     │
│   Model: gemini-1.5-flash              │
└─────────────────────────────────────────┘
```

---

## Next Steps

1. ✅ **Try the web interface** - http://localhost:8000
2. ✅ **Explore API docs** - http://localhost:8000/docs
3. ✅ **Test with your URLs** - Any public webpage
4. ✅ **Try different models** - Compare Flash vs Pro
5. ✅ **Build your app** - Use the API in your projects

---

## Stop the Server

Press `Ctrl+C` in the terminal where the API is running.

---

## Questions?

- **API Documentation:** [API_README.md](API_README.md)
- **Migration Guide:** [GEMINI_MIGRATION.md](GEMINI_MIGRATION.md)
- **Full Docs:** [README.md](README.md)

**Happy Summarizing!** 🎉
