"""
Unit tests for FeedSummarizer.
"""

from computer_use.feed_summarizer import FeedSummarizer

SAMPLE_POSTS = [
    {
        "id": "1",
        "author": "Alice Dev",
        "handle": "@alice",
        "text": "Excited about #AI and #Python automation with computer-use!",
        "metrics": {"likes": "150", "reposts": "30"}
    },
    {
        "id": "2",
        "author": "Bob Engineer",
        "handle": "@bob",
        "text": "High performance computing in #Python is game changing for #AI models.",
        "metrics": {"likes": "1.2K", "reposts": "240"}
    },
    {
        "id": "3",
        "author": "Carol Scientist",
        "handle": "@carol",
        "text": "Check out @bob's latest benchmarks on local inference latency! #OpenSource",
        "metrics": {"likes": "85", "reposts": "12"}
    }
]

def test_extract_hashtags():
    summarizer = FeedSummarizer()
    hashtags = summarizer.extract_hashtags(SAMPLE_POSTS)
    tag_names = [h["tag"] for h in hashtags]
    assert "#ai" in tag_names
    assert "#python" in tag_names
    assert "#opensource" in tag_names
    # #ai and #python appeared twice
    ai_tag = next(h for h in hashtags if h["tag"] == "#ai")
    assert ai_tag["count"] == 2

def test_extract_mentions():
    summarizer = FeedSummarizer()
    mentions = summarizer.extract_mentions(SAMPLE_POSTS)
    assert len(mentions) == 1
    assert mentions[0]["mention"] == "@bob"

def test_extract_topics():
    summarizer = FeedSummarizer()
    topics = summarizer.extract_topics(SAMPLE_POSTS, top_n=5)
    keywords = [t["keyword"] for t in topics]
    assert "automation" in keywords or "benchmarks" in keywords or "models" in keywords

def test_top_posts_ranking():
    summarizer = FeedSummarizer()
    top = summarizer.get_top_posts(SAMPLE_POSTS, metric="likes", limit=1)
    assert len(top) == 1
    assert top[0]["id"] == "2" # 1.2K likes is the highest

def test_full_summary_generation():
    summarizer = FeedSummarizer()
    summary = summarizer.summarize(SAMPLE_POSTS)
    assert summary["total_posts"] == 3
    assert len(summary["top_posts"]) == 3
    assert "# 📰 Feed Digest: 3 Posts Analyzed" in summary["markdown_digest"]
    assert "High-Engagement Highlights" in summary["markdown_digest"]
