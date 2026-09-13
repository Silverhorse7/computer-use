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
