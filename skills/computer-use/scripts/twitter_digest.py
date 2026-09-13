#!/usr/bin/env python3
"""
Helper Script: Twitter / X Feed Digest & Interaction Runner.
Executes the Twitter automation pipeline and prints the executive markdown digest.
"""

import sys
import io

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from computer_use import ComputerUseController
from computer_use.feed_summarizer import FeedSummarizer


def main():
    live = "--live" in sys.argv
    cu = ComputerUseController()
    
    print(f"[*] Starting Twitter Feed Digest (live_mode={live})...")
    if live:
        cu.navigate("https://x.com/home")
        posts = cu.extract_twitter_posts(count=20, auto_scroll=True)
    else:
        # Sample realistic posts for verification
        posts = [
            {"author": "Yosef Madboly", "handle": "@Silverhorse7", "text": "Open-sourcing computer-use: 3-tier hybrid engine <20ms DOM! #AI #Python", "metrics": {"likes": "1.4K", "reposts": "320"}},
            {"author": "Andrej Karpathy", "handle": "@karpathy", "text": "Fastest computer use agent avoids visual LLM inference when DOM exists.", "metrics": {"likes": "8.9K", "reposts": "1.2K"}},
            {"author": "OpenAI Devs", "handle": "@OpenAIDevs", "text": "Real-time streaming and lower latency tool calling for agents. #AI #Developers", "metrics": {"likes": "3.5K", "reposts": "620"}},
        ]
        
    summarizer = FeedSummarizer()
    summary = summarizer.summarize(posts)
    print("\n" + summary["markdown_digest"])


if __name__ == "__main__":
    main()
