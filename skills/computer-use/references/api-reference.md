# API Reference: Computer Use Hybrid Engine

This document provides a comprehensive reference for both the **Python API** and the **PowerShell Module**.

---

## 1. Python API (`computer_use`)

### `ComputerUseController`
The master orchestrator unifying all three execution tiers.

```python
from computer_use import ComputerUseController
cu = ComputerUseController(script_path=None)
```

#### OS Primitives (Tier 3)
- `cu.capture(output_path="capture.png") -> str`: Captures active window or primary display to PNG.
- `cu.click(x: int, y: int) -> str`: Performs native Win32 mouse click at screen coordinates.
- `cu.type_text(text: str) -> str`: Types raw text into the currently focused input.
- `cu.press_key(keys: str) -> str`: Sends special key combinations (e.g., `^l` for address bar, `{ENTER}`, `{PGDN}`, `{F12}`).
- `cu.scroll(amount: int = -500) -> str`: Scrolls vertical wheel (positive = up, negative = down).
- `cu.navigate(url: str) -> str`: Focuses address bar, pastes URL, and navigates.
- `cu.maximize() -> str`: Maximizes target application window.

#### DOM Injection (Tier 1: `cu.dom`)
- `cu.dom.click_button(button_text: str) -> str`: Finds button by visible text (case-insensitive) and dispatches complete synthetic mouse events (`mouseenter` -> `mouseover` -> `mousedown` -> `mouseup` -> `click`).
- `cu.dom.select_radio(label_text: str) -> str`: Finds radio button by adjacent label or container text and selects it.
- `cu.dom.fill_input(label_text: str, value: str) -> str`: Finds input by placeholder, name, id, or associated label and updates value with `input` and `change` events.
- `cu.dom.evaluate(js_expression: str, timeout: float = 3.5) -> Any`: Evaluates JS in browser DevTools console and returns parsed JSON output via OS clipboard bridge.
- `cu.dom.extract_twitter_posts(count: int = 20, auto_scroll: bool = True) -> List[Dict[str, Any]]`: Queries virtualized Twitter feed and returns parsed tweet records.
- `cu.dom.interact_twitter_post(query: str, action: str = "like") -> Dict[str, Any]`: Finds tweet matching query substring and clicks action button (`like`, `bookmark`, `retweet`, `reply`).

#### Batched Vision (Tier 2: `cu.vision` & `cu.batch`)
- `cu.vision.detect_dropdown_boxes(image_path: str) -> List[BoundingBox]`: In-memory contrast border scanner returning bounding boxes in ~150ms.
- `cu.vision.detect_unfilled_red_boxes(image_path: str) -> List[BoundingBox]`: Detects red validation error borders (`R > 170, G < 70, B < 70`).
- `cu.vision.detect_primary_button(image_path: str, color_type: str = "orange") -> Optional[BoundingBox]`: Color segmentation button locator.
- `cu.batch.batch_fill_dropdowns(image_path: str, options_strategy=None, field_click_delay_ms=180)`: Sequentially fills all detected dropdowns in ~8 seconds.
- `cu.batch.recover_unfilled_fields(check_image_path: str)`: Scans for red error boxes and re-clicks them.

#### Feed Intelligence (`cu.summarizer`)
- `cu.summarize_feed(posts: List[Dict[str, Any]]) -> Dict[str, Any]`: Analyzes feed posts to extract hashtags, topics, active voices, top-engagement posts, and formats a markdown digest.

---

## 2. PowerShell Module (`powershell/ComputerUse.psd1`)

Zero external dependencies. Works on standard Windows 10/11 PowerShell 5.1+.

```powershell
Import-Module .\powershell\ComputerUse.psd1
```

### Exported Cmdlets

| Cmdlet | Parameters | Description |
| :--- | :--- | :--- |
| `Invoke-CUCapture` | `-Path <string>` | Captures active display to PNG. |
| `Invoke-CUClick` | `-X <int> -Y <int>` | Native Win32 mouse click. |
| `Invoke-CUSendKeys` | `-Keys <string>` | Sends keystrokes / hotkeys. |
| `Invoke-CUNavigate` | `-Url <string>` | Focuses browser URL bar and navigates. |
| `Invoke-CUScroll` | `-Amount <int>` | Mouse wheel scroll (default -500). |
| `Invoke-CUDOMClick` | `-ButtonText <string>` | Tier 1 synthetic DOM click (<20ms). |
| `Invoke-CUDOMRadio` | `-LabelText <string>` | Tier 1 synthetic radio selection. |
| `Invoke-CUBatchScan` | `-ImagePath <string>` | In-memory border contrast detection. |
| `Invoke-CUTwitterExtract` | `-Count <int>` | Ingests Twitter/X feed posts (default 20). |
| `Invoke-CUTwitterInteract`| `-Query <string> -Action <string>` | Interacts with matching tweet (`like`, `bookmark`). |
