"""
Tests for vision bounding box and detection logic.
"""

from computer_use.engine_vision import BoundingBox, BatchVisionEngine
from PIL import Image

def test_bounding_box_properties():
    box = BoundingBox(100, 200, 300, 240)
    assert box.width == 200
    assert box.height == 40
    assert box.center_x == 200
    assert box.center_y == 220
    d = box.to_dict()
    assert d["left"] == 100
    assert d["top"] == 200

def test_vision_engine_button_detection(tmp_path):
    img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    # Draw an orange button
    for y in range(150, 190):
        for x in range(100, 250):
            img.putpixel((x, y), (255, 153, 0))
            
    test_path = str(tmp_path / "test_orange.png")
    img.save(test_path)
    
    engine = BatchVisionEngine()
    btn = engine.detect_primary_button(test_path, color_type="orange")
    assert btn is not None
    assert 95 <= btn.left <= 105
    assert 145 <= btn.top <= 155
