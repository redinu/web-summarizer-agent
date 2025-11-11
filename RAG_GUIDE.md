# RAG (Retrieval-Augmented Generation) Guide

## 🧠 What is RAG?

RAG enhances your Web Summarizer with memory! Instead of processing each URL in isolation, RAG stores all summaries in a vector database, allowing you to:

- **Search semantically** across all past summaries
- **Ask questions** about your knowledge base
- **Find related content** automatically
- **Build knowledge** over time

## 🚀 Quick Start

### Enable RAG

Set environment variables:

```bash
# Enable RAG
ENABLE_RAG=true

# Choose embedding model (optional)
RAG_EMBEDDING_MODEL=sentence-transformers  # Free, local (default)
# OR
RAG_EMBEDDING_MODEL=gemini  # Uses your Gemini API key
```

### Start the API

```bash
python3 api.py
```

You'll see: `🧠 RAG (Retrieval-Augmented Generation) ENABLED`

## 📖 How It Works

### 1. Automatic Storage

When you summarize a URL with RAG enabled, it's automatically stored:

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/ai-article"}'
```

✅ Summary is generated AND stored in vector database

### 2. Semantic Search

Find similar summaries:

```bash
curl -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What have I learned about artificial intelligence?",
    "n_results": 5
  }'
```

**Response:**
```json
{
  "success": true,
  "query": "What have I learned about artificial intelligence?",
  "results_count": 5,
  "results": [
    {
      "id": "doc_12345",
      "document": "Article Title\n\nSummary text...",
      "metadata": {
        "url": "https://example.com/ai-article",
        "title": "The Future of AI",
        "category": "Technology",
        "timestamp": "2025-11-10T10:30:00"
      },
      "distance": 0.23
    }
  ]
}
```

### 3. Question Answering

Ask questions about your knowledge base:

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main trends in AI according to the articles I've read?",
    "n_context_docs": 3
  }'
```

**Response:**
```json
{
  "success": true,
  "question": "What are the main trends in AI...",
  "answer": "Based on the articles you've read, the main AI trends are...",
  "sources": [
    {
      "title": "AI Trends 2025",
      "url": "https://example.com/ai-trends",
      "relevance_score": 0.89
    }
  ],
  "context_documents_used": 3
}
```

## 🎯 API Endpoints

### POST /rag/search

Search for similar summaries

**Request:**
```json
{
  "query": "machine learning applications",
  "n_results": 5
}
```

### POST /rag/query

Ask questions using RAG

**Request:**
```json
{
  "question": "What are the key challenges in AI development?",
  "n_context_docs": 3
}
```

### GET /rag/stats

Get knowledge base statistics

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_documents": 127,
    "collection_name": "web_summaries",
    "embedding_model": "sentence-transformers",
    "persist_directory": "./chroma_db"
  }
}
```

### DELETE /rag/clear

Clear all documents from knowledge base

**Response:**
```json
{
  "success": true,
  "message": "All documents cleared from RAG knowledge base"
}
```

## 🔧 Configuration

### Embedding Models

**Option 1: Sentence Transformers (Recommended)**
- ✅ 100% Free
- ✅ Runs locally
- ✅ No API key needed
- ✅ Good quality
- Uses: `all-MiniLM-L6-v2` model

```bash
RAG_EMBEDDING_MODEL=sentence-transformers
```

**Option 2: Google Gemini Embeddings**
- Uses your existing Gemini API key
- Excellent quality
- Requires API calls (minimal cost)

```bash
RAG_EMBEDDING_MODEL=gemini
```

### Storage Location

RAG data is stored in `./chroma_db` by default. This directory contains:
- Vector embeddings
- Document metadata
- ChromaDB index

**To change location** (modify in code):
```python
agent = WebSummarizerAgent(
    gemini_api_key=api_key,
    enable_rag=True,
    rag_persist_dir="/path/to/storage"
)
```

## 💡 Use Cases

### 1. Research Assistant

Build a knowledge base of research papers:

```bash
# Summarize multiple papers
for url in paper1.pdf paper2.pdf paper3.pdf; do
  curl -X POST http://localhost:8000/summarize \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$url\"}"
done

# Ask questions about the research
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the common methodologies used?"}'
```

### 2. Competitive Intelligence

Track competitor news:

```bash
# Summarize competitor articles
# They're automatically stored in RAG

# Later, query for insights
curl -X POST http://localhost:8000/rag/query \
  -d '{"question": "What are my competitors focusing on?"}'
```

### 3. Content Aggregation

Build a searchable archive:

```bash
# Use topic aggregation with RAG enabled
curl -X POST http://localhost:8000/search-and-aggregate \
  -d '{"topic": "AI trends", "num_results": 20}'

# All 20 summaries are stored in RAG

# Search your archive
curl -X POST http://localhost:8000/rag/search \
  -d '{"query": "GPT-4 capabilities"}'
```

## 🐍 Python SDK Usage

```python
from web_summarizer import WebSummarizerAgent

# Initialize with RAG
agent = WebSummarizerAgent(
    gemini_api_key="your-key",
    enable_rag=True,
    rag_embedding_model="sentence-transformers"  # or "gemini"
)

# Summarize (automatically stores in RAG)
response = agent.summarize_url("https://example.com/article")

# Search RAG
if agent.rag_engine:
    results = agent.rag_engine.search_similar(
        query="machine learning",
        n_results=5
    )

    for result in results:
        print(f"Title: {result['metadata']['title']}")
        print(f"URL: {result['metadata']['url']}")
        print(f"Relevance: {1 - result['distance']:.2f}")
        print()

# Query with context
import google.generativeai as genai
model = genai.GenerativeModel("models/gemini-2.5-flash")

answer = agent.rag_engine.generate_with_context(
    query="What are the key findings?",
    gemini_model=model,
    n_context_docs=3
)

print(f"Answer: {answer['answer']}")
print(f"Sources: {len(answer['sources'])}")
```

## 📊 Performance

### Storage

- **Per document**: ~1-2 KB (metadata + embedding)
- **1000 documents**: ~1-2 MB
- **10,000 documents**: ~10-20 MB

### Speed

- **Embedding creation**: 10-50ms (Sentence Transformers)
- **Search**: 5-20ms for 1000 docs
- **Query + generation**: 2-5 seconds (depends on Gemini)

## 🔒 Privacy & Security

### Local Storage

- All data stored locally in `./chroma_db`
- No data sent to third parties (except Gemini for generation)
- Delete data anytime with `/rag/clear`

### Embeddings

**Sentence Transformers (default):**
- 100% local processing
- No data leaves your machine
- No API calls for embeddings

**Gemini Embeddings:**
- Text sent to Google for embedding
- Follow Google's privacy policy
- More secure than storing full articles elsewhere

## 🚀 Deployment with RAG

### Render

Add environment variable in Render dashboard:
```
ENABLE_RAG=true
```

### Docker

```bash
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e ENABLE_RAG=true \
  -v $(pwd)/chroma_db:/app/chroma_db \
  web-summarizer:latest
```

**Important**: Use volume mount (`-v`) to persist RAG data!

### Docker Compose

```yaml
services:
  web-summarizer:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENABLE_RAG=true
      - RAG_EMBEDDING_MODEL=sentence-transformers
    volumes:
      - ./chroma_db:/app/chroma_db
```

## 🐛 Troubleshooting

### RAG not enabled

**Error**: `RAG is not enabled`

**Solution**:
```bash
export ENABLE_RAG=true
python3 api.py
```

### Import errors

**Error**: `ModuleNotFoundError: No module named 'chromadb'`

**Solution**:
```bash
pip install chromadb sentence-transformers
```

### Slow embedding creation

**Issue**: First embedding is slow

**Explanation**: Sentence Transformers downloads model on first use (~80MB)

**Solution**: Wait for download, subsequent embeddings are fast

### Storage growing large

**Issue**: `chroma_db` directory is large

**Solution**: Clear old data:
```bash
curl -X DELETE http://localhost:8000/rag/clear
```

Or delete directory:
```bash
rm -rf ./chroma_db
```

## 📈 Roadmap

Future RAG enhancements:

- [ ] Multi-modal embeddings (images + text)
- [ ] Automatic document clustering
- [ ] Temporal queries ("articles from last month")
- [ ] Export/import knowledge base
- [ ] Federated search across multiple databases
- [ ] Fine-tuned embeddings for specific domains

## 🎓 Learn More

**RAG Concepts:**
- [Retrieval-Augmented Generation Paper](https://arxiv.org/abs/2005.11401)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

**Related Tools:**
- LangChain: RAG framework
- LlamaIndex: Data framework for LLMs
- Weaviate: Vector database

---

**Questions?** Open an issue on GitHub!
