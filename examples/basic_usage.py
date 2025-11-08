"""
Basic usage example for Web Summarizer Agent
"""

import json
import os
from dotenv import load_dotenv

from web_summarizer import WebSummarizerAgent

# Load environment variables
load_dotenv()


def main():
    # Initialize the agent
    agent = WebSummarizerAgent(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    # Example URL to summarize
    url = "https://www.anthropic.com/news/claude-3-5-sonnet"

    print(f"Summarizing: {url}\n")

    # Simple usage
    response = agent.summarize_url(url)

    if response.success:
        print("✅ Summary Generated Successfully!\n")
        print(f"Title: {response.data.title}\n")
        print(f"Summary:\n{response.data.summary}\n")
        print("Key Points:")
        for i, point in enumerate(response.data.key_points, 1):
            print(f"  {i}. {point}")
        print(f"\nCategory: {response.data.category}")
        print(f"\nMetadata:")
        print(f"  - Processing Time: {response.data.metadata.processing_time_ms}ms")
        print(f"  - Tokens Used: {response.data.metadata.tokens_used}")
        print(f"  - Model: {response.data.metadata.model_used}")
        print(f"  - Content Length: {response.data.metadata.content_length} chars")
    else:
        print(f"❌ Error: {response.error}")
        print(f"Error Code: {response.error_code}")

    # Get full JSON response
    print("\n" + "=" * 80)
    print("Full JSON Response:")
    print("=" * 80)
    print(json.dumps(response.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    main()
