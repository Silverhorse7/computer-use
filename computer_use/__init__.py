"""
Computer Use: High-Performance Hybrid Automation Engine.

Combines DevTools DOM injection (<20ms), in-memory fast batched vision (150ms),
and resilient native Win32 STA OS primitives.
"""

from .core import ComputerUseController
from .engine_win32 import Win32Driver
from .engine_dom import DOMDriver
from .engine_vision import BatchVisionEngine
from .engine_batch import FormBatchFiller

__version__ = "0.1.0"
__author__ = "Yosef Madboly"
__all__ = [
    "ComputerUseController",
    "Win32Driver",
    "DOMDriver",
    "BatchVisionEngine",
    "FormBatchFiller",
]
