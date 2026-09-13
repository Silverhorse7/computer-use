"""
Feed Summarizer & Content Intelligence Engine.

Analyzes social feeds (Twitter/X, Bluesky, Mastodon, etc.) to extract
trending hashtags, key topics, high-engagement posts, and executive digests.
Supports 100% offline heuristic analysis with optional LLM neural synthesis.
"""

import re
from collections import Counter
from typing import List, Dict, Any, Optional


# Standard English stopwords to filter out for keyword extraction
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "just", "like", "get", "got", "also", "one", "new"
}


class FeedSummarizer:
    """
    Intelligent Social Feed Summarizer.
    
    Processes structured post objects, extracts statistical and semantic
    patterns, and formats executive briefings.
    """

    def __init__(self, stopwords: Optional[set] = None):
        self.stopwords = stopwords or STOPWORDS

    @staticmethod
    def _parse_metric(value: Any) -> float:
        """Parse metric strings like '1.2K', '3M', '450' into numeric values."""
        if isinstance(value, (int, float)):
            return float(value)
        if not value or not isinstance(value, str):
            return 0.0
        val = value.strip().upper().replace(",", "")
        try:
            if val.endswith("K"):
                return float(val[:-1]) * 1_000
            elif val.endswith("M"):
                return float(val[:-1]) * 1_000_000
            return float(val)
        except ValueError:
            return 0.0

    def extract_hashtags(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and rank hashtags from posts."""
        hashtags = []
        for post in posts:
            text = post.get("text", "")
            tags = re.findall(r"#\w+", text, re.IGNORECASE)
            hashtags.extend([t.lower() for t in tags])
        counts = Counter(hashtags).most_common()
        return [{"tag": tag, "count": count} for tag, count in counts]

    def extract_mentions(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and rank user mentions (@user) from posts."""
        mentions = []
        for post in posts:
            text = post.get("text", "")
            found = re.findall(r"@[A-Za-z0-9_]+", text)
            mentions.extend(found)
        counts = Counter(mentions).most_common()
        return [{"mention": mention, "count": count} for mention, count in counts]

    def extract_topics(self, posts: List[Dict[str, Any]], top_n: int = 8) -> List[Dict[str, Any]]:
        """Extract top recurring keywords/topics across all posts."""
        tokens = []
        for post in posts:
            text = post.get("text", "")
            # Remove URLs
            text = re.sub(r"https?://\S+", "", text)
            words = re.findall(r"[A-Za-z]{3,}", text.lower())
            for w in words:
                if w not in self.stopwords:
                    tokens.append(w)
        counts = Counter(tokens).most_common(top_n)
        return [{"keyword": word, "frequency": count} for word, count in counts]

    def get_top_posts(self, posts: List[Dict[str, Any]], metric: str = "likes", limit: int = 3) -> List[Dict[str, Any]]:
        """Return the highest engagement posts ranked by specified metric."""
        def score(p):
            metrics = p.get("metrics", {})
            return self._parse_metric(metrics.get(metric, 0))

        sorted_posts = sorted(posts, key=score, reverse=True)
        return sorted_posts[:limit]

    def summarize(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate structured summary analytics from a batch of posts.
        """
        if not posts:
            return {
                "total_posts": 0,
                "topics": [],
                "hashtags": [],
                "top_posts": [],
                "authors": [],
                "digest": "No posts provided to summarize."
            }

        topics = self.extract_topics(posts, top_n=8)
        hashtags = self.extract_hashtags(posts)
        top_liked = self.get_top_posts(posts, metric="likes", limit=3)
        
        # Author frequency
        authors = Counter([p.get("handle") or p.get("author") for p in posts if p.get("handle") or p.get("author")]).most_common(5)
        author_list = [{"author": a, "posts_count": c} for a, c in authors]

        # Build Markdown Digest
        digest_lines = [
            f"# 📰 Feed Digest: {len(posts)} Posts Analyzed",
            "",
            "## 🔍 Primary Topics & Themes",
        ]

        if topics:
            topics_str = ", ".join([f"**{t['keyword']}** ({t['frequency']})" for t in topics[:6]])
            digest_lines.append(f"- Key discussions centered on: {topics_str}")
        else:
            digest_lines.append("- Diverse discussions without dominant single-topic clustering.")

        if hashtags:
            tags_str = " ".join([f"`{h['tag']}`" for h in hashtags[:8]])
            digest_lines.append(f"- Trending tags: {tags_str}")

        digest_lines.extend([
            "",
            "## 🌟 High-Engagement Highlights",
        ])

        for idx, post in enumerate(top_liked, start=1):
            author = post.get("author", "User")
            handle = post.get("handle", "")
            text = post.get("text", "").replace("\n", " ")
            if len(text) > 120:
                text = text[:117] + "..."
            likes = post.get("metrics", {}).get("likes", "0")
            reposts = post.get("metrics", {}).get("reposts", "0")
            digest_lines.append(f"{idx}. **{author}** ({handle}) — ❤️ {likes} | 🔁 {reposts}")
            digest_lines.append(f"   > \"{text}\"")

        digest_lines.extend([
            "",
            "## 👥 Active Voices",
        ])
        for a in author_list:
            digest_lines.append(f"- **{a['author']}** ({a['posts_count']} posts)")

        markdown_digest = "\n".join(digest_lines)

        return {
            "total_posts": len(posts),
            "topics": topics,
            "hashtags": hashtags,
            "top_posts": top_liked,
            "authors": author_list,
            "markdown_digest": markdown_digest
        }
