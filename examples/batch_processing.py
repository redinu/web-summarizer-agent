"""
Batch processing example - summarize multiple URLs
"""

import os
from dotenv import load_dotenv

from web_summarizer import WebSummarizerAgent

load_dotenv()


def main():
    # Initialize agent
    agent = WebSummarizerAgent(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    # URLs to summarize
    urls = [
        "https://www.anthropic.com/news/claude-3-5-sonnet",
        "https://www.anthropic.com/news/claude-3-family",
        "https://blog.anthropic.com/constitutional-ai-harmlessness-from-ai-feedback",
    ]

    print("Batch Processing Example")
    print("=" * 80)
    print(f"Processing {len(urls)} URLs...\n")

    results = []
    total_tokens = 0
    total_time = 0

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")

        response = agent.summarize_url(url, num_key_points=3)

        if response.success:
            print(f"  ✅ Success - {response.data.metadata.processing_time_ms}ms")
            results.append(response)
            total_tokens += response.data.metadata.tokens_used
            total_time += response.data.metadata.processing_time_ms
        else:
            print(f"  ❌ Failed: {response.error}")

        print()

    # Summary report
    print("=" * 80)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Total URLs: {len(urls)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(urls) - len(results)}")
    print(f"Total Tokens: {total_tokens}")
    print(f"Total Time: {total_time}ms")
    print(f"Average Time: {total_time / len(results) if results else 0:.0f}ms")
    print()

    # Display summaries
    print("=" * 80)
    print("SUMMARIES")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.data.title}")
        print(f"   URL: {result.data.url}")
        print(f"   Category: {result.data.category}")
        print(f"\n   Summary: {result.data.summary}")
        print(f"\n   Key Points:")
        for point in result.data.key_points:
            print(f"   - {point}")
        print()


if __name__ == "__main__":
    main()
