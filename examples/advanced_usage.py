"""
Advanced usage example with custom options
"""

import os
from dotenv import load_dotenv

from web_summarizer import WebSummarizerAgent
from web_summarizer.models import SummaryRequest, SummaryOptions

load_dotenv()


def main():
    # Initialize agent
    agent = WebSummarizerAgent(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
    )

    # Custom options
    options = SummaryOptions(
        max_summary_sentences=6,
        num_key_points=8,
        include_citations=True,
        model="gemini-1.5-pro",  # Use more powerful model
        timeout_seconds=30,
    )

    # Create request
    request = SummaryRequest(
        url="https://blog.google/technology/ai/",
        options=options,
    )

    print("Advanced Summarization with Custom Options")
    print("=" * 80)
    print(f"URL: {request.url}")
    print(f"Model: {options.model}")
    print(f"Max Summary Sentences: {options.max_summary_sentences}")
    print(f"Key Points: {options.num_key_points}")
    print(f"Include Citations: {options.include_citations}")
    print("=" * 80 + "\n")

    # Summarize
    response = agent.summarize(request)

    if response.success:
        print(f"📄 Title: {response.data.title}\n")

        print("📝 Summary:")
        print(response.data.summary)
        print()

        print("🔑 Key Points:")
        for i, point in enumerate(response.data.key_points, 1):
            print(f"   {i}. {point}")
        print()

        if response.data.citations:
            print("💬 Notable Quotes:")
            for i, citation in enumerate(response.data.citations, 1):
                print(f'   {i}. "{citation}"')
            print()

        print(f"🏷️  Category: {response.data.category}\n")

        print("⚡ Performance:")
        print(f"   - Time: {response.data.metadata.processing_time_ms}ms")
        print(f"   - Tokens: {response.data.metadata.tokens_used}")
        print(f"   - Cost: ~${response.data.metadata.tokens_used * 0.000001:.6f}")

    else:
        print(f"❌ Error [{response.error_code}]: {response.error}")


if __name__ == "__main__":
    main()
