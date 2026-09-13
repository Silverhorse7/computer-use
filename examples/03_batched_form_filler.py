"""
Example 03: In-Memory Fast Batched Form Filling.

Demonstrates scanning an entire multi-field form in ~150ms and filling
all dropdowns in rapid succession without LLM vision delays.
"""

from computer_use import ComputerUseController

def main():
    cu = ComputerUseController()

    # 1. Capture the form
    capture_path = "form_page.png"
    cu.capture(capture_path)

    # 2. In-memory detection (100-150ms)
    boxes = cu.vision.detect_dropdown_boxes(capture_path)
    print(f"Found {len(boxes)} form fields!")

    # 3. Strategy callback: choose option based on field index
    def choose_option(index: int, total: int, box):
        # Example: select default tier (+42px) for general parameters,
        # or custom secondary tier (+84px) for the final policy setting
        if index == total - 1:
            return 84
        return 42

    # 4. Batch fill in ~8 seconds
    cu.batch.batch_fill_dropdowns(
        image_path=capture_path,
        options_strategy=choose_option,
        field_click_delay_ms=180
    )

    # 5. Check and recover any unfilled red boxes
    cu.batch.recover_unfilled_fields("form_check.png")

    # 6. Click Continue CTA
    btn = cu.vision.detect_primary_button(capture_path, color_type="orange")
    if btn:
        print(f"Clicking Continue at ({btn.center_x}, {btn.center_y})")
        cu.click(btn.center_x, btn.center_y)

if __name__ == "__main__":
    main()
