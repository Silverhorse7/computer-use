"""
Tests for DOM injection script generation.
"""

from computer_use.engine_dom import DOMDriver

def test_button_js_generation():
    dom = DOMDriver()
    js = dom.build_click_button_js("Continue")
    assert "target = 'continue'" in js
    assert "triggerEvents" in js
    assert "querySelectorAll" in js

def test_radio_js_generation():
    dom = DOMDriver()
    js = dom.build_click_radio_js("Enterprise Tier")
    assert "enterprise tier" in js
    assert "input.checked = true" in js

def test_input_js_generation():
    dom = DOMDriver()
    js = dom.build_fill_input_js("Phone", "1234567890")
    assert "target = 'phone'" in js
    assert "val = '1234567890'" in js

def test_twitter_extract_js_generation():
    dom = DOMDriver()
    js = dom.build_extract_twitter_posts_js(count=20)
    assert "article[data-testid=\"tweet\"]" in js
    assert "tweetText" in js
    assert "User-Name" in js
    assert ".slice(0, 20)" in js

def test_twitter_interact_js_generation():
    dom = DOMDriver()
    js = dom.build_interact_twitter_post_js("open source", action="like")
    assert "open source" in js
    assert "like" in js
    assert "triggerEvents" in js
    assert "button[data-testid=\"like\"]" in js

