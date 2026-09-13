#!/usr/bin/env python3
"""
Helper Script: In-Memory UI Contrast Border Scanner.
Scans an image or current display for input fields and dropdown boxes in ~150ms.
"""

import sys
from computer_use import ComputerUseController


def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else "screen.png"
    cu = ComputerUseController()
    
    if len(sys.argv) <= 1:
        print("[*] No image supplied, capturing active screen...")
        cu.capture(image_path)
        
    print(f"[*] Scanning UI boxes in '{image_path}' using in-memory contrast analysis...")
    boxes = cu.vision.detect_dropdown_boxes(image_path)
    print(f"[+] Detected {len(boxes)} UI form fields in image:")
    for i, b in enumerate(boxes, 1):
        print(f"    {i}. Bounds: ({b.x1}, {b.y1}) -> ({b.x2}, {b.y2}) | Center: ({b.center_x}, {b.center_y})")


if __name__ == "__main__":
    main()
