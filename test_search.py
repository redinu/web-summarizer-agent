#!/usr/bin/env python3
"""Quick test of the search-based aggregation feature"""

import sys
import os
sys.path.insert(0, 'src')

from web_summarizer.web_searcher import WebSearcher

# Test search
searcher = WebSearcher(search_engine="duckduckgo")

print("🔍 Testing web search...")
results = searcher.search("python programming", num_results=3)

print(f"\n✅ Found {len(results)} results:\n")
for i, result in enumerate(results, 1):
    print(f"{i}. {result['title']}")
    print(f"   {result['url']}")
    print(f"   {result['snippet'][:100]}...")
    print()

print("\n✨ Search feature working!")
