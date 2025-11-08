"""
Topic-based content aggregation and social media post generation
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
import concurrent.futures
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SocialMediaPost:
    """Social media post data"""
    platform: str
    content: str
    hashtags: List[str]
    character_count: int


class TopicAggregator:
    """Aggregates summaries from multiple sources for a specific topic"""

    def __init__(self, agent):
        """
        Initialize topic aggregator

        Args:
            agent: WebSummarizerAgent instance
        """
        self.agent = agent

    def aggregate_topic(
        self,
        topic: str,
        urls: List[str],
        platforms: Optional[List[str]] = None,
        max_workers: int = 5,
    ) -> Dict:
        """
        Aggregate summaries from multiple URLs for a specific topic

        Args:
            topic: The topic to focus on
            urls: List of URLs to summarize
            platforms: Social media platforms to generate posts for
            max_workers: Maximum concurrent workers

        Returns:
            Dictionary with aggregated data and social media posts
        """
        if platforms is None:
            platforms = ["twitter", "linkedin", "facebook"]

        logger.info(f"Aggregating content for topic: {topic} from {len(urls)} sources")

        # Summarize all URLs concurrently
        summaries = self._fetch_summaries(urls, max_workers)

        # Generate social media posts for each summary
        rows = []
        for i, summary_response in enumerate(summaries):
            if not summary_response.success:
                logger.warning(f"Failed to summarize URL {i+1}: {summary_response.error}")
                continue

            data = summary_response.data

            # Generate posts for each platform
            social_posts = self._generate_social_posts(
                topic=topic,
                summary=data.summary,
                key_points=data.key_points,
                url=data.url,
                title=data.title,
                platforms=platforms,
            )

            row = {
                "source_url": data.url,
                "title": data.title,
                "category": data.category,
                "summary": data.summary,
                "key_points": "; ".join(data.key_points),
                "word_count": len(data.summary.split()),
                "tokens_used": data.metadata.tokens_used,
                "processing_time_ms": data.metadata.processing_time_ms,
                "timestamp": data.metadata.timestamp,
            }

            # Add social media posts
            for platform, post in social_posts.items():
                row[f"{platform}_post"] = post.content
                row[f"{platform}_hashtags"] = " ".join(post.hashtags)
                row[f"{platform}_chars"] = post.character_count

            rows.append(row)

        # Generate master summary from all successful summaries
        master_summary = self._generate_master_summary(summaries, topic)

        # Generate consolidated social media posts
        all_summaries_text = "\n\n".join([
            s.data.summary for s in summaries if s.success
        ])
        all_key_points = []
        for s in summaries:
            if s.success:
                all_key_points.extend(s.data.key_points)

        # Get first successful URL for reference
        first_url = next((s.data.url for s in summaries if s.success), "")
        first_title = f"{topic} - Research Summary"

        consolidated_posts = self._generate_social_posts(
            topic=topic,
            summary=master_summary,
            key_points=all_key_points[:5],  # Top 5 key points
            url=first_url,
            title=first_title,
            platforms=platforms,
        )

        # Convert posts to simple dict
        social_media_posts = {
            platform: post.content
            for platform, post in consolidated_posts.items()
        }

        result = {
            "topic": topic,
            "total_sources": len(urls),
            "successful_summaries": len(rows),
            "failed_summaries": len(urls) - len(rows),
            "platforms": platforms,
            "generated_at": datetime.now().isoformat(),
            "master_summary": master_summary,
            "social_media_posts": social_media_posts,
            "summaries": [
                {
                    "url": s.data.url if s.success else "",
                    "success": s.success,
                    "data": {
                        "title": s.data.title if s.success else "",
                        "summary": s.data.summary if s.success else "",
                        "key_points": s.data.key_points if s.success else [],
                    } if s.success else {},
                    "error": s.error if not s.success else None,
                }
                for s in summaries
            ],
            "data": rows,
        }

        logger.info(f"Successfully aggregated {len(rows)}/{len(urls)} sources")

        return result

    def _fetch_summaries(self, urls: List[str], max_workers: int) -> List:
        """Fetch summaries concurrently"""
        summaries = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.agent.summarize_url, url): url
                for url in urls
            }

            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    summary = future.result(timeout=60)
                    summaries.append(summary)
                except Exception as e:
                    url = future_to_url[future]
                    logger.error(f"Failed to fetch summary for {url}: {e}")
                    # Create a failed response
                    from web_summarizer.models import SummaryResponse
                    summaries.append(
                        SummaryResponse(
                            success=False,
                            error=str(e),
                            error_code="FETCH_FAILED",
                        )
                    )

        return summaries

    def _generate_social_posts(
        self,
        topic: str,
        summary: str,
        key_points: List[str],
        url: str,
        title: str,
        platforms: List[str],
    ) -> Dict[str, SocialMediaPost]:
        """Generate social media posts for different platforms"""
        posts = {}

        # Generate hashtags from topic
        hashtags = self._generate_hashtags(topic, key_points)

        for platform in platforms:
            if platform.lower() == "twitter":
                posts["twitter"] = self._generate_twitter_post(
                    summary, key_points, url, hashtags
                )
            elif platform.lower() == "linkedin":
                posts["linkedin"] = self._generate_linkedin_post(
                    topic, title, summary, key_points, url, hashtags
                )
            elif platform.lower() == "facebook":
                posts["facebook"] = self._generate_facebook_post(
                    topic, title, summary, key_points, url, hashtags
                )
            elif platform.lower() == "instagram":
                posts["instagram"] = self._generate_instagram_post(
                    summary, key_points, hashtags
                )

        return posts

    def _generate_twitter_post(
        self,
        summary: str,
        key_points: List[str],
        url: str,
        hashtags: List[str],
    ) -> SocialMediaPost:
        """Generate Twitter/X post (280 character limit)"""
        # Twitter limit: 280 characters
        max_length = 280

        # Reserve space for URL (23 chars for t.co) and hashtags
        url_length = 23
        hashtag_text = " ".join(hashtags[:3])  # Max 3 hashtags
        reserved = url_length + len(hashtag_text) + 4  # spaces and newlines

        # Create concise content
        if len(key_points) > 0:
            content = f"{key_points[0]}"
        else:
            content = summary[:100]

        # Ensure we fit in the limit
        available = max_length - reserved
        if len(content) > available:
            content = content[:available-3] + "..."

        post_text = f"{content}\n\n{url}\n\n{hashtag_text}"

        return SocialMediaPost(
            platform="twitter",
            content=post_text,
            hashtags=hashtags[:3],
            character_count=len(post_text),
        )

    def _generate_linkedin_post(
        self,
        topic: str,
        title: str,
        summary: str,
        key_points: List[str],
        url: str,
        hashtags: List[str],
    ) -> SocialMediaPost:
        """Generate LinkedIn post (3000 character limit)"""
        # LinkedIn: More professional, can be longer

        post_parts = [
            f"📊 {topic}: {title}",
            "",
            summary,
            "",
            "Key Insights:",
        ]

        for i, point in enumerate(key_points[:5], 1):
            post_parts.append(f"{i}. {point}")

        post_parts.extend([
            "",
            f"Read more: {url}",
            "",
            " ".join(hashtags[:5]),
        ])

        post_text = "\n".join(post_parts)

        # Ensure within limit
        if len(post_text) > 3000:
            post_text = post_text[:2997] + "..."

        return SocialMediaPost(
            platform="linkedin",
            content=post_text,
            hashtags=hashtags[:5],
            character_count=len(post_text),
        )

    def _generate_facebook_post(
        self,
        topic: str,
        title: str,
        summary: str,
        key_points: List[str],
        url: str,
        hashtags: List[str],
    ) -> SocialMediaPost:
        """Generate Facebook post (63,206 character limit, but aim for ~500)"""
        # Facebook: Casual, engaging, aim for 500 chars for better engagement

        post_parts = [
            f"💡 {title}",
            "",
            summary,
            "",
            "✨ Highlights:",
        ]

        for point in key_points[:3]:
            post_parts.append(f"• {point}")

        post_parts.extend([
            "",
            f"🔗 {url}",
            "",
            " ".join(hashtags[:3]),
        ])

        post_text = "\n".join(post_parts)

        return SocialMediaPost(
            platform="facebook",
            content=post_text,
            hashtags=hashtags[:3],
            character_count=len(post_text),
        )

    def _generate_instagram_post(
        self,
        summary: str,
        key_points: List[str],
        hashtags: List[str],
    ) -> SocialMediaPost:
        """Generate Instagram caption (2,200 character limit)"""
        # Instagram: Visual-first, use emojis, max 30 hashtags

        post_parts = [
            summary,
            "",
            "✨ Key takeaways:",
        ]

        emojis = ["📌", "💡", "🎯", "⚡", "🔥"]
        for i, point in enumerate(key_points[:5]):
            emoji = emojis[i % len(emojis)]
            post_parts.append(f"{emoji} {point}")

        post_parts.extend([
            "",
            " ".join(hashtags[:30]),  # Instagram allows up to 30
        ])

        post_text = "\n".join(post_parts)

        # Ensure within limit
        if len(post_text) > 2200:
            post_text = post_text[:2197] + "..."

        return SocialMediaPost(
            platform="instagram",
            content=post_text,
            hashtags=hashtags[:30],
            character_count=len(post_text),
        )

    def _generate_master_summary(self, summaries: List, topic: str) -> str:
        """Generate a master summary from multiple article summaries using AI"""
        successful_summaries = [s for s in summaries if s.success]

        if not successful_summaries:
            return f"No articles were successfully summarized for the topic: {topic}"

        if len(successful_summaries) == 1:
            return successful_summaries[0].data.summary

        # Combine all summaries
        combined_text = "\n\n---\n\n".join([
            f"Source: {s.data.title}\n{s.data.summary}"
            for s in successful_summaries
        ])

        # Use Gemini to generate a master summary
        try:
            prompt = f"""Based on the following summaries about "{topic}", create a comprehensive master summary that:
1. Synthesizes the key insights from all sources
2. Highlights common themes and patterns
3. Notes any contrasting viewpoints
4. Is concise yet informative (3-5 sentences)

Summaries:
{combined_text}

Master Summary:"""

            response = self.agent.summarizer.client.generate_content(prompt)
            master_summary = response.text.strip()

            return master_summary

        except Exception as e:
            logger.error(f"Failed to generate master summary: {e}")
            # Fallback: return first summary
            return successful_summaries[0].data.summary

    def _generate_hashtags(self, topic: str, key_points: List[str]) -> List[str]:
        """Generate relevant hashtags from topic and key points"""
        hashtags = set()

        # Add topic-based hashtags
        topic_words = topic.replace("-", " ").replace("_", " ").split()
        for word in topic_words:
            if len(word) > 3:  # Skip short words
                hashtags.add(f"#{word.capitalize()}")

        # Generic useful hashtags
        hashtags.add("#TechNews")
        hashtags.add("#Innovation")
        hashtags.add("#DigitalTransformation")

        return list(hashtags)[:10]  # Return max 10 hashtags
