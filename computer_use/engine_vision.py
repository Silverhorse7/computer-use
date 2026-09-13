"""
In-Memory Fast Batched Vision & UI Detection Engine (100–150ms).
"""

import time
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image


class BoundingBox:
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.width = right - left
        self.height = bottom - top
        self.center_x = (left + right) // 2
        self.center_y = (top + bottom) // 2

    def to_dict(self) -> Dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
            "width": self.width,
            "height": self.height,
            "center_x": self.center_x,
            "center_y": self.center_y,
        }

    def __repr__(self) -> str:
        return f"BoundingBox({self.left}, {self.top}, {self.right}, {self.bottom}) Center=({self.center_x}, {self.center_y})"


class BatchVisionEngine:
    """
    High-speed pixel scanning engine.
    
    Operates directly on in-memory bitmaps to identify form fields, dropdowns,
    unfilled red validation error borders, and primary CTA buttons in under 150ms
    without making expensive or slow LLM visual inference calls.
    """

    def __init__(self, default_box_height_range: Tuple[int, int] = (32, 52)):
        self.box_min_h, self.box_max_h = default_box_height_range

    def detect_dropdown_boxes(
        self,
        image_path: str,
        scan_x_range: Tuple[int, int] = (1200, 1600),
        scan_y_range: Optional[Tuple[int, int]] = None,
    ) -> List[BoundingBox]:
        """
        Scans for rectangular input/dropdown borders by detecting horizontal grey edges.
        """
        t0 = time.perf_counter()
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        
        y_min = scan_y_range[0] if scan_y_range else 200
        y_max = scan_y_range[1] if scan_y_range else height - 100
        x_start, x_end = scan_x_range
        
        borders = []
        # Sample every row
        for y in range(y_min, y_max):
            match_count = 0
            # Sample across x span
            for x in range(x_start, x_end, 2):
                r, g, b = img.getpixel((x, y))
                # Neutral grey border detection
                if 100 < r < 215 and abs(r - g) <= 6 and abs(g - b) <= 6:
                    match_count += 1
            if match_count > 120:
                borders.append(y)
                
        # Group pairs of lines into boxes
        boxes: List[BoundingBox] = []
        i = 0
        while i < len(borders):
            top = borders[i]
            matched = False
            for j in range(i + 1, len(borders)):
                bot = borders[j]
                h = bot - top
                if self.box_min_h <= h <= self.box_max_h:
                    boxes.append(BoundingBox(x_start, top, x_end, bot))
                    i = j
                    matched = True
                    break
            i += 1
            
        t1 = time.perf_counter()
        print(f"=== [VISION] Detected {len(boxes)} fields in {(t1-t0)*1000:.2f} ms ===")
        return boxes

    def detect_unfilled_red_boxes(
        self,
        image_path: str,
        scan_x_range: Tuple[int, int] = (1200, 1600),
    ) -> List[BoundingBox]:
        """
        Detects red validation borders for unfilled required fields (R > 170, G < 70, B < 70).
        """
        t0 = time.perf_counter()
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        x_start, x_end = scan_x_range
        
        red_lines = []
        for y in range(250, height - 100):
            match_count = 0
            for x in range(x_start, x_end, 2):
                r, g, b = img.getpixel((x, y))
                if r > 170 and g < 70 and b < 70:
                    match_count += 1
            if match_count > 80:
                red_lines.append(y)
                
        boxes: List[BoundingBox] = []
        i = 0
        while i < len(red_lines):
            top = red_lines[i]
            for j in range(i + 1, len(red_lines)):
                bot = red_lines[j]
                if self.box_min_h <= bot - top <= self.box_max_h:
                    boxes.append(BoundingBox(x_start, top, x_end, bot))
                    i = j
                    break
            i += 1
            
        t1 = time.perf_counter()
        print(f"=== [VISION] Detected {len(boxes)} red unfilled boxes in {(t1-t0)*1000:.2f} ms ===")
        return boxes

    def detect_primary_button(
        self,
        image_path: str,
        color_type: str = "orange",
        search_region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Optional[BoundingBox]:
        """
        Finds primary action buttons by color segmentation (orange, blue, green).
        """
        img = Image.open(image_path).convert("RGB")
        w, h = img.size
        
        min_x, min_y, max_x, max_y = search_region or (0, 0, w, h)
        
        button_pixels = []
        step = 4
        for y in range(min_y, max_y, step):
            for x in range(min_x, max_x, step):
                r, g, b = img.getpixel((x, y))
                match = False
                if color_type == "orange":
                    # Accent orange / warm CTA
                    if r > 215 and 95 < g < 180 and b < 55:
                        match = True
                elif color_type == "blue":
                    # Primary SaaS blue
                    if b > 190 and g > 90 and r < 75:
                        match = True
                elif color_type == "green":
                    # Success green
                    if g > 150 and r < 80 and b < 80:
                        match = True
                        
                if match:
                    button_pixels.append((x, y))
                    
        if not button_pixels:
            return None
            
        xs = [p[0] for p in button_pixels]
        ys = [p[1] for p in button_pixels]
        return BoundingBox(min(xs), min(ys), max(xs), max(ys))
