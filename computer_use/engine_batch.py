"""
Fast Batched Multi-Field Form Filler & Pipeline Runner.
"""

import time
from typing import List, Optional, Callable, Dict, Any
from .engine_win32 import Win32Driver
from .engine_vision import BatchVisionEngine, BoundingBox


class FormBatchFiller:
    """
    Executes batched UI interactions sequentially without per-action LLM perception loops.
    
    Transforms what would be 2-3 minutes of repetitive visual prompts into
    a single sub-10 second synchronized execution pipeline.
    """

    def __init__(self, win32: Optional[Win32Driver] = None, vision: Optional[BatchVisionEngine] = None):
        self.win32 = win32 or Win32Driver()
        self.vision = vision or BatchVisionEngine()

    def batch_fill_dropdowns(
        self,
        image_path: str,
        options_strategy: Optional[Callable[[int, int, BoundingBox], int]] = None,
        field_click_delay_ms: int = 180,
        option_offset_y: int = 42,
    ) -> int:
        """
        Detects all dropdown boxes in image_path and clicks them sequentially.
        
        :param options_strategy: Function (index, total_count, box) -> offset_y
                                 Defaults to selecting option 1 (+42px) or option 2 (+84px).
        :return: Count of fields filled.
        """
        boxes = self.vision.detect_dropdown_boxes(image_path)
        if not boxes:
            print("=== [BATCH] No dropdown boxes detected ===")
            return 0

        t0 = time.perf_counter()
        print(f"=== [BATCH] Executing batch fill across {len(boxes)} fields ===")

        for idx, box in enumerate(boxes):
            cy = box.center_y
            cx = box.center_x

            # 1. Click dropdown to open
            self.win32.click(cx, cy)
            time.sleep(field_click_delay_ms / 1000.0)

            # 2. Determine option vertical offset
            if options_strategy:
                offset = options_strategy(idx, len(boxes), box)
            else:
                # Default: Option 1 (+42px)
                offset = option_offset_y

            # 3. Click option
            self.win32.click(cx, cy + offset)
            time.sleep(field_click_delay_ms / 1000.0)

        t1 = time.perf_counter()
        print(f"=== [BATCH] Completed {len(boxes)} fields in {(t1-t0):.2f} seconds ===")
        return len(boxes)

    def recover_unfilled_fields(
        self,
        temp_capture_path: str,
        default_choice_offset: int = 42,
    ) -> int:
        """
        Captures screen, scans for red-bordered unfilled boxes, and fills them.
        """
        self.win32.capture(temp_capture_path)
        red_boxes = self.vision.detect_unfilled_red_boxes(temp_capture_path)
        if not red_boxes:
            return 0

        print(f"=== [RECOVERY] Recovering {len(red_boxes)} unfilled fields ===")
        for box in red_boxes:
            self.win32.click(box.center_x, box.center_y)
            time.sleep(0.2)
            self.win32.click(box.center_x, box.center_y + default_choice_offset)
            time.sleep(0.2)

        return len(red_boxes)
