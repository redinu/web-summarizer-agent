#!/usr/bin/env python3
"""
Example: Topic Aggregation for Social Media Content

This example shows how to aggregate summaries from multiple sources
for a specific topic and generate social media posts.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from web_summarizer import WebSummarizerAgent
from web_summarizer.topic_aggregator import TopicAggregator
from web_summarizer.spreadsheet_generator import SpreadsheetGenerator

# Load environment variables
load_dotenv()


def main():
    # Initialize the agent
    agent = WebSummarizerAgent(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
    )

    # Initialize aggregator and spreadsheet generator
    aggregator = TopicAggregator(agent)
    spreadsheet_gen = SpreadsheetGenerator()

    # Define topic and URLs to aggregate
    topic = "AI-Advancements-2025"

    urls = [
        "https://blog.google/technology/ai/google-gemini-ai/",
        "https://openai.com/index/hello-gpt-4o/",
        "https://www.anthropic.com/news/claude-3-family",
        # Add more URLs here
    ]

    platforms = ["twitter", "linkedin", "facebook", "instagram"]

    print(f"🤖 Aggregating content for topic: {topic}")
    print(f"📊 Processing {len(urls)} sources...")
    print(f"📱 Generating posts for: {', '.join(platforms)}\n")

    # Aggregate summaries
    result = aggregator.aggregate_topic(
        topic=topic,
        urls=urls,
        platforms=platforms,
        max_workers=3,  # Process 3 URLs concurrently
    )

    # Display results
    print("=" * 80)
    print("AGGREGATION RESULTS")
    print("=" * 80)
    print(f"Topic: {result['topic']}")
    print(f"Total Sources: {result['total_sources']}")
    print(f"Successful: {result['successful_summaries']}")
    print(f"Failed: {result['failed_summaries']}")
    print(f"Generated At: {result['generated_at']}")
    print("=" * 80)

    # Display first summary with social media posts
    if result['data']:
        first_result = result['data'][0]
        print(f"\n📄 Sample: {first_result['title']}")
        print(f"URL: {first_result['source_url']}")
        print(f"\nSummary:\n{first_result['summary']}")
        print(f"\nKey Points:")
        for point in first_result['key_points'].split('; '):
            print(f"  • {point}")

        print("\n" + "=" * 80)
        print("SOCIAL MEDIA POSTS")
        print("=" * 80)

        for platform in platforms:
            post_key = f"{platform}_post"
            hashtag_key = f"{platform}_hashtags"
            chars_key = f"{platform}_chars"

            if post_key in first_result:
                print(f"\n🐦 {platform.upper()} ({first_result[chars_key]} characters):")
                print("-" * 80)
                print(first_result[post_key])
                print(f"\nHashtags: {first_result[hashtag_key]}")

    # Export to CSV
    print("\n" + "=" * 80)
    print("EXPORTING TO SPREADSHEETS")
    print("=" * 80)

    csv_path = f"output/{topic}_social_media.csv"
    csv_file = spreadsheet_gen.generate_csv(
        result,
        output_path=csv_path,
        include_metadata=True,
    )
    print(f"✅ CSV exported to: {csv_file}")

    # Export to Excel
    excel_path = f"output/{topic}_social_media.xlsx"
    excel_file = spreadsheet_gen.generate_excel(
        result,
        output_path=excel_path,
        include_metadata=True,
    )
    print(f"✅ Excel exported to: {excel_file}")

    # Display preview
    print("\n" + "=" * 80)
    print("CSV PREVIEW")
    print("=" * 80)
    preview = spreadsheet_gen.preview_csv(result, max_rows=2)
    print(preview)

    print("\n✨ Done! Open the Excel file to see all social media posts organized by platform.")
    print(f"   You can now use the content from the '{topic}_social_media.xlsx' file")
    print("   to schedule posts on your social media platforms!")


if __name__ == "__main__":
    main()
