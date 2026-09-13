"""
Tests for Core ComputerUseController initialization and structure.
"""

from computer_use import ComputerUseController, Win32Driver, DOMDriver, BatchVisionEngine

def test_controller_initialization():
    cu = ComputerUseController()
    assert isinstance(cu.win32, Win32Driver)
    assert isinstance(cu.dom, DOMDriver)
    assert isinstance(cu.vision, BatchVisionEngine)
    assert cu.batch is not None
