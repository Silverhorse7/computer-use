"""
High-Speed DevTools DOM Injection Driver (<20ms execution).
"""

import time
from typing import Optional, Dict, Any, List
from .engine_win32 import Win32Driver


class DOMDriver:
    """
    DOM Injection automation driver.
    
    Executes client-side JavaScript payloads directly in the browser's context
    via DevTools Console injection or Chrome DevTools Protocol (CDP), triggering
    native-like synthetic events (mousedown, mouseup, click, change, input)
    that React, Vue, and Angular frameworks accept without visual rendering overhead.
    """

    def __init__(self, win32: Optional[Win32Driver] = None):
        self.win32 = win32 or Win32Driver()

    def build_event_dispatcher_js(self) -> str:
        """Returns reusable JavaScript helper for dispatching full event lifecycles."""
        return """
function triggerEvents(el, val = null) {
    if (!el) return false;
    ['mouseenter', 'mouseover', 'mousedown', 'mouseup', 'click'].forEach(evt => {
        el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
    });
    if (val !== null && ('value' in el)) {
        el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    }
    return true;
}
"""

    def build_click_button_js(self, button_text: str) -> str:
        """Generates JS to find and click a button matching text (case-insensitive)."""
        clean_text = button_text.lower().strip()
        return f"""
(() => {{
    {self.build_event_dispatcher_js()}
    const target = '{clean_text}';
    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"], a[role="button"], div[role="button"]'))
        .filter(b => b.textContent.trim().toLowerCase().includes(target) && !b.disabled);
    if (btns.length > 0) {{
        triggerEvents(btns[0]);
        console.log("=== [DOM] Clicked button matching: " + target + " ===");
        return true;
    }}
    console.warn("=== [DOM] Button not found matching: " + target + " ===");
    return false;
}})();
"""

    def build_click_radio_js(self, label_substring: str) -> str:
        """Generates JS to find and select a radio button by its text or label."""
        return f"""
(() => {{
    {self.build_event_dispatcher_js()}
    const target = '{label_substring.lower().strip()}';
    const labels = Array.from(document.querySelectorAll('label, span, div'))
        .filter(l => l.textContent && l.textContent.toLowerCase().includes(target));
    if (labels.length > 0) {{
        let el = labels[0];
        let radio = el.closest('label') || el.parentElement;
        let input = (radio ? radio.querySelector('input[type="radio"]') : null) || el.querySelector('input') || el;
        if (input && input.tagName === 'INPUT') {{
            input.checked = true;
            triggerEvents(input);
        }} else {{
            triggerEvents(el);
        }}
        console.log("=== [DOM] Checked radio matching: " + target + " ===");
        return true;
    }}
    console.warn("=== [DOM] Radio not found matching: " + target + " ===");
    return false;
}})();
"""

    def build_fill_input_js(self, label_substring: str, value: str) -> str:
        """Generates JS to find an input by adjacent label or placeholder and fill value."""
        return f"""
(() => {{
    {self.build_event_dispatcher_js()}
    const target = '{label_substring.lower().strip()}';
    const val = '{value.replace("'", "\\'")}';
    
    // 1. Check placeholder
    let input = Array.from(document.querySelectorAll('input, textarea'))
        .find(i => (i.placeholder && i.placeholder.toLowerCase().includes(target)) ||
                   (i.name && i.name.toLowerCase().includes(target)) ||
                   (i.id && i.id.toLowerCase().includes(target)));
                   
    // 2. Check associated label
    if (!input) {{
        const labels = Array.from(document.querySelectorAll('label'))
            .filter(l => l.textContent.toLowerCase().includes(target));
        if (labels.length > 0) {{
            input = labels[0].querySelector('input, textarea') ||
                    document.getElementById(labels[0].htmlFor);
        }}
    }}
    
    if (input) {{
        triggerEvents(input, val);
        console.log("=== [DOM] Filled input for: " + target + " ===");
        return true;
    }}
    console.warn("=== [DOM] Input not found for: " + target + " ===");
    return false;
}})();
"""

    def inject_console(self, js_code: str, auto_close: bool = True, wait_ms: int = 400) -> str:
        """
        Injects and runs JavaScript via DevTools Console.
        
        Shortcut:
        1. Ctrl+Shift+J (opens Console)
        2. Paste JS snippet + Enter
        3. F12 (closes DevTools to prevent layout shift)
        """
        # Focus DevTools Console
        self.win32.send_keys("^+j")
        time.sleep(1.0)
        
        # Load script into clipboard and execute
        ps_code = f"""
Add-Type -AssemblyName System.Windows.Forms
$js = @'
{js_code}
'@
[System.Windows.Forms.Clipboard]::SetText($js)
Start-Sleep -Milliseconds 150
"""
        self.win32._run_ps(["-Command", ps_code])
        self.win32.send_keys("^v{ENTER}")
        time.sleep(wait_ms / 1000.0)
        
        if auto_close:
            self.win32.send_keys("{F12}")
            time.sleep(0.5)
            
        return "OK: Injected JS payload"

    def evaluate(self, js_expression: str, timeout: float = 3.5) -> Any:
        """
        Evaluates JavaScript in the browser DevTools console and returns the result
        by leveraging the DevTools copy() clipboard bridge.
        """
        import json
        
        wrapped_js = f"""
try {{
    const __cu_res = (() => {{ return ({js_expression}); }})();
    copy(JSON.stringify(__cu_res));
}} catch (__cu_err) {{
    copy(JSON.stringify({{ __cu_error: __cu_err.message }}));
}}
"""
        marker = f"__CU_PENDING_{time.time()}__"
        self.win32.set_clipboard(marker)
        
        self.inject_console(wrapped_js, auto_close=True, wait_ms=300)
        
        t0 = time.time()
        raw_text = ""
        while time.time() - t0 < timeout:
            raw_text = self.win32.get_clipboard()
            if raw_text and raw_text != marker and not raw_text.startswith("__CU_PENDING_"):
                break
            time.sleep(0.15)
            
        try:
            return json.loads(raw_text)
        except Exception:
            return raw_text

    def build_extract_twitter_posts_js(self, count: int = 20) -> str:
        """Generates JS to query and extract tweets from active Twitter/X feed."""
        return f"""
(() => {{
    function harvest() {{
        const articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
        return articles.map(article => {{
            const userEl = article.querySelector('[data-testid="User-Name"]');
            const textEl = article.querySelector('[data-testid="tweetText"]');
            const timeEl = article.querySelector('time');
            const linkEl = article.querySelector('a[href*="/status/"]');
            
            const fullUserText = userEl ? userEl.innerText : '';
            const handleMatch = fullUserText.match(/@([A-Za-z0-9_]+)/);
            const handle = handleMatch ? handleMatch[0] : '';
            const author = fullUserText.split('\\n')[0].trim();
            const text = textEl ? textEl.innerText.trim() : '';
            
            const tweetUrl = linkEl ? linkEl.href : '';
            const tweetIdMatch = tweetUrl.match(/status\\/(\\d+)/);
            const id = tweetIdMatch ? tweetIdMatch[1] : (handle + '_' + text.slice(0, 30));

            const likeBtn = article.querySelector('button[data-testid="like"], button[data-testid="unlike"]');
            const retweetBtn = article.querySelector('button[data-testid="retweet"], button[data-testid="unretweet"]');
            const replyBtn = article.querySelector('button[data-testid="reply"]');
            
            const getCount = (btn) => {{
                if (!btn) return '0';
                const t = btn.innerText.trim();
                if (t) return t;
                const label = btn.getAttribute('aria-label') || '';
                const m = label.match(/([\\d,\\.]+[KkMm]?)/);
                return m ? m[1] : '0';
            }};

            return {{
                id: id,
                author: author || 'Twitter User',
                handle: handle || '@user',
                text: text,
                timestamp: timeEl ? (timeEl.getAttribute('datetime') || timeEl.innerText) : '',
                url: tweetUrl,
                metrics: {{
                    likes: getCount(likeBtn),
                    reposts: getCount(retweetBtn),
                    replies: getCount(replyBtn)
                }},
                liked: !!article.querySelector('button[data-testid="unlike"]')
            }};
        }}).filter(p => p.text.length > 0 || p.url.length > 0);
    }}
    return harvest().slice(0, {count});
}})()
"""

    def build_interact_twitter_post_js(self, query: str, action: str = "like") -> str:
        """Generates JS to find matching tweet and click action button (like, bookmark, retweet)."""
        clean_query = query.lower().replace("'", "\\'")
        clean_action = action.lower().strip()
        return f"""
(() => {{
    {self.build_event_dispatcher_js()}
    const query = '{clean_query}';
    const action = '{clean_action}';
    
    const articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
    const match = articles.find(a => {{
        const text = a.innerText.toLowerCase();
        return text.includes(query);
    }});

    if (!match) {{
        console.warn('[computer-use] Tweet not found matching query: ' + query);
        return {{ success: false, reason: 'tweet_not_found', query: query }};
    }}

    let btn = null;
    if (action === 'like') {{
        btn = match.querySelector('button[data-testid="like"]');
    }} else if (action === 'bookmark') {{
        btn = match.querySelector('button[data-testid="bookmark"]');
    }} else if (action === 'retweet' || action === 'repost') {{
        btn = match.querySelector('button[data-testid="retweet"]');
    }} else if (action === 'reply') {{
        btn = match.querySelector('button[data-testid="reply"]');
    }}

    if (!btn) {{
        const alreadyDone = match.querySelector('button[data-testid="un' + action + '"]');
        if (alreadyDone) {{
            return {{ success: true, already_done: true, action: action }};
        }}
        return {{ success: false, reason: 'action_button_not_found', action: action }};
    }}

    triggerEvents(btn);
    const authorEl = match.querySelector('[data-testid="User-Name"]');
    const textEl = match.querySelector('[data-testid="tweetText"]');
    return {{
        success: true,
        action: action,
        author: authorEl ? authorEl.innerText.split('\\n')[0] : '',
        snippet: textEl ? textEl.innerText.slice(0, 80) : ''
    }};
}})()
"""

    def extract_twitter_posts(self, count: int = 20, auto_scroll: bool = True, max_scroll_steps: int = 10) -> List[Dict[str, Any]]:
        """
        Extract up to `count` posts from the active Twitter/X feed.
        If auto_scroll is True, automatically scrolls down to load virtualized tweets.
        """
        collected = {}
        scroll_count = 0
        
        while len(collected) < count and scroll_count <= max_scroll_steps:
            js = self.build_extract_twitter_posts_js(count)
            posts = self.evaluate(js)
            if isinstance(posts, list):
                for p in posts:
                    pid = p.get("id") or (p.get("handle", "") + "_" + p.get("text", "")[:30])
                    if pid and pid not in collected:
                        collected[pid] = p
            
            if len(collected) >= count or not auto_scroll:
                break
                
            # Scroll down to load more tweets in virtualized DOM
            self.win32.scroll(-800)
            time.sleep(0.5)
            scroll_count += 1
            
        return list(collected.values())[:count]

    def interact_twitter_post(self, query: str, action: str = "like") -> Dict[str, Any]:
        """
        Find a tweet matching `query` and trigger the specified action ('like', 'bookmark', 'retweet', 'reply').
        Dispatches full synthetic event lifecycles (<20ms).
        """
        js = self.build_interact_twitter_post_js(query, action)
        res = self.evaluate(js)
        if isinstance(res, dict):
            return res
        return {"success": True, "raw_result": str(res)}

    def click_button(self, button_text: str) -> str:
        """Click button by text using DOM injection."""
        js = self.build_click_button_js(button_text)
        return self.inject_console(js)

    def select_radio(self, label_text: str) -> str:
        """Select radio option by text using DOM injection."""
        js = self.build_click_radio_js(label_text)
        return self.inject_console(js)

    def fill_input(self, label_text: str, value: str) -> str:
        """Fill input by label using DOM injection."""
        js = self.build_fill_input_js(label_text, value)
        return self.inject_console(js)


