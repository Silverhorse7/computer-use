"""
Master ComputerUseController orchestrating hybrid automation.
"""

import os
import time
from typing import Optional, Dict, Any, List, Tuple
from .engine_win32 import Win32Driver
from .engine_dom import DOMDriver
from .engine_vision import BatchVisionEngine, BoundingBox
from .engine_batch import FormBatchFiller
from .feed_summarizer import FeedSummarizer


class ComputerUseController:
    """
    Unified High-Performance Computer Use Controller.
    
    Provides seamless access to:
    - Tier 1: DevTools DOM Injection (<20ms)
    - Tier 2: In-Memory Fast Batched Vision (~150ms)
    - Tier 3: Native Win32 STA Primitives
    """

    def __init__(self, script_path: Optional[str] = None):
        self.win32 = Win32Driver(script_path=script_path)
        self.dom = DOMDriver(win32=self.win32)
        self.vision = BatchVisionEngine()
        self.batch = FormBatchFiller(win32=self.win32, vision=self.vision)
        self.summarizer = FeedSummarizer()


    # --- OS / Desktop Primitives ---

    def capture(self, output_path: str = "capture.png") -> str:
        """Capture screenshot of the active window or desktop."""
        return self.win32.capture(output_path)

    def click(self, x: int, y: int) -> str:
        """Native Win32 click at coordinates."""
        return self.win32.click(x, y)

    def type_text(self, text: str) -> str:
        """Type string directly into focused element."""
        return self.win32.send_keys(text)

    def press_key(self, keys: str) -> str:
        """Send special key combos (e.g. '^l', '{ENTER}', '{PGDN}')."""
        return self.win32.send_keys(keys)

    def scroll(self, amount: int = -500) -> str:
        """Scroll vertical wheel."""
        return self.win32.scroll(amount)

    def navigate(self, url: str) -> str:
        """Focus browser URL bar and navigate."""
        return self.win32.navigate(url)

    def maximize(self) -> str:
        """Maximize target window."""
        return self.win32.maximize()

    # --- Hybrid Actions ---

    def click_button_hybrid(self, button_text: str, fallback_capture_path: str = "temp_btn.png") -> bool:
        """
        Attempts ultra-fast DOM injection click first.
        If unavailable or in desktop app, falls back to in-memory color segmentation click.
        """
        t0 = time.perf_counter()
        try:
            res = self.dom.click_button(button_text)
            print(f"=== [HYBRID] DOM click attempted: {res} ===")
            return True
        except Exception as e:
            print(f"=== [HYBRID] DOM failed ({e}), falling back to vision ===")

        # Vision Fallback
        self.capture(fallback_capture_path)
        btn = self.vision.detect_primary_button(fallback_capture_path)
        if btn:
            self.click(btn.center_x, btn.center_y)
            t1 = time.perf_counter()
            print(f"=== [HYBRID] Vision fallback clicked button at ({btn.center_x}, {btn.center_y}) in {(t1-t0):.2f}s ===")
            return True

        return False

    # --- Feed & Social Intelligence Primitives ---

    def extract_twitter_posts(self, count: int = 20, auto_scroll: bool = True) -> List[Dict[str, Any]]:
        """
        Extract up to `count` posts from the active Twitter/X feed via Tier 1 DOM injection.
        """
        return self.dom.extract_twitter_posts(count=count, auto_scroll=auto_scroll)

    def interact_twitter_post(self, query: str, action: str = "like") -> Dict[str, Any]:
        """
        Find tweet matching `query` and trigger action ('like', 'bookmark', 'retweet', 'reply').
        """
        return self.dom.interact_twitter_post(query=query, action=action)

    def summarize_feed(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize analytics, trending hashtags, top topics, and markdown digest from posts.
        """
        return self.summarizer.summarize(posts)

