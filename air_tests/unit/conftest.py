# air_tests/unit/conftest.py
import sys
import pytest
import numpy as np
from unittest.mock import MagicMock


class FakeTemplate:
    """Stand-in for airtest.core.api.Template used in unit tests."""
    def __init__(self, filename="img.png"):
        self.filename = filename
        self.rgb = False
        self.threshold = 0.7
        self.record_pos = None
        self.resolution = None

    def match_in(self, screen):
        return None


def _passthrough_decorator(f):
    """Stand-in for @logwrap — returns the original function unchanged."""
    return f


def make_template(**kwargs) -> FakeTemplate:
    t = FakeTemplate()
    for k, v in kwargs.items():
        setattr(t, k, v)
    return t


def make_rgb_screen(h=100, w=100) -> np.ndarray:
    return np.zeros((h, w, 3), dtype=np.uint8)


@pytest.fixture(scope="session", autouse=True)
def airtest_stubs():
    # Stub out ALL heavy/native packages BEFORE pixonwrapper import
    for _mod in [
        "paddlepaddle", "paddle", "paddleocr",
        "pytesseract", "PIL", "PIL.Image", "cv2", "requests",
        "airtest", "airtest.core", "airtest.core.api",
        "airtest.aircv", "airtest.report", "airtest.report.report",
    ]:
        sys.modules.setdefault(_mod, MagicMock())

    # airtest.core.api: logwrap must be passthrough, Template must be FakeTemplate
    _api_stub = MagicMock()
    _api_stub.Template = FakeTemplate
    _api_stub.logwrap  = _passthrough_decorator
    sys.modules["airtest.core.api"] = _api_stub

    # Import pixonwrapper only after stubs are in place
    import pixon.pixonwrapper as pw

    # Inject all names the module expects at module level
    pw.Template = FakeTemplate
    pw.G        = MagicMock()
    pw.touch    = MagicMock()
    pw.sleep    = MagicMock()
    pw.log      = MagicMock()
    pw.wait     = MagicMock()

    # BUG-10 FIX: pixonwrapper imports crop_image directly from airtest.aircv
    # (not via pw.aircv.crop_image). Inject mock at module level so partial_search()
    # and is_text_present() use the mock when tested.
    _mock_crop = MagicMock(return_value=make_rgb_screen())
    pw.crop_image = _mock_crop

    # Keep pw.aircv as MagicMock for any legacy references;
    # point its crop_image at the same mock for symmetry
    pw.aircv = MagicMock()
    pw.aircv.crop_image = _mock_crop

    # Inject _ocr stub so TestFindAllText patch.object works correctly
    pw._ocr = MagicMock()

    yield pw
