# air_tests/unit/test_pixonwrapper.py
import sys
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

import pixon.pixonwrapper as pw


def make_template(**kwargs):
    from air_tests.unit.conftest import FakeTemplate  # noqa: PLC0415
    t = FakeTemplate()
    for k, v in kwargs.items():
        setattr(t, k, v)
    return t


def make_rgb_screen(h=100, w=100) -> np.ndarray:
    return np.zeros((h, w, 3), dtype=np.uint8)


# ===========================================================================
# 1. default_img_setup
# ===========================================================================

class TestDefaultImgSetup:

    def test_sets_rgb_true(self):
        t = make_template(rgb=False)
        pw.default_img_setup(t)
        assert t.rgb is True

    def test_sets_threshold_to_0_6(self):
        t = make_template(threshold=0.9)
        pw.default_img_setup(t)
        assert t.threshold == 0.6

    def test_sets_record_pos_empty_tuple_when_none(self):
        t = make_template(record_pos=None)
        pw.default_img_setup(t)
        assert t.record_pos == ()

    def test_does_not_override_existing_record_pos(self):
        t = make_template(record_pos=(0.1, 0.2))
        pw.default_img_setup(t)
        assert t.record_pos == (0.1, 0.2)

    def test_sets_default_resolution_720x1280(self):
        t = make_template(resolution=None)
        pw.default_img_setup(t)
        assert t.resolution == (720, 1280)

    def test_does_not_override_existing_resolution(self):
        t = make_template(resolution=(1080, 1920))
        pw.default_img_setup(t)
        assert t.resolution == (1080, 1920)

    def test_returns_same_object(self):
        t = make_template()
        result = pw.default_img_setup(t)
        assert result is t

    def test_non_template_returned_as_is(self):
        coord = (100, 200)
        result = pw.default_img_setup(coord)
        assert result == coord


# ===========================================================================
# 2. find_all_text
# ===========================================================================

class TestFindAllText:

    def _make_ocr_result(self, items):
        """Build a fake PaddleOCR result: list of [[bbox], (text, conf)]"""
        return [[None, item] for item in items]

    def test_returns_texts_above_confidence_threshold(self):
        fake_result = self._make_ocr_result([("123", 0.9), ("456", 0.7), ("789", 0.5)])
        mock_ocr = MagicMock()
        mock_ocr.ocr.return_value = [fake_result]
        with patch.object(pw, "_ocr", mock_ocr):
            result = pw.find_all_text(make_rgb_screen())
        assert result == ["123", "456"]

    def test_filters_low_confidence(self):
        fake_result = self._make_ocr_result([("low", 0.4), ("high", 0.8)])
        mock_ocr = MagicMock()
        mock_ocr.ocr.return_value = [fake_result]
        with patch.object(pw, "_ocr", mock_ocr):
            result = pw.find_all_text(make_rgb_screen())
        assert result == ["high"]

    def test_returns_empty_list_when_no_results(self):
        mock_ocr = MagicMock()
        mock_ocr.ocr.return_value = [None]
        with patch.object(pw, "_ocr", mock_ocr):
            result = pw.find_all_text(make_rgb_screen())
        assert result == []

    def test_returns_empty_list_on_exception(self):
        mock_ocr = MagicMock()
        mock_ocr.ocr.side_effect = Exception("OCR crash")
        with patch.object(pw, "_ocr", mock_ocr):
            result = pw.find_all_text(make_rgb_screen())
        assert result == []

    def test_handles_bgra_input(self):
        bgra_img = np.zeros((50, 50, 4), dtype=np.uint8)
        mock_ocr = MagicMock()
        mock_ocr.ocr.return_value = [[]]
        with patch.object(pw, "_ocr", mock_ocr):
            result = pw.find_all_text(bgra_img)
        assert result == []


# ===========================================================================
# 3. is_text_present
# ===========================================================================

class TestIsTextPresent:

    def test_true_when_text_found(self):
        with patch.object(pw, "find_all_text", return_value=["100", "200"]):
            pw.G.DEVICE.snapshot.return_value = make_rgb_screen()
            assert pw.is_text_present("100") is True

    def test_false_when_text_not_found(self):
        with patch.object(pw, "find_all_text", return_value=["100"]):
            pw.G.DEVICE.snapshot.return_value = make_rgb_screen()
            assert pw.is_text_present("999") is False

    def test_crops_when_area_provided(self):
        # BUG-10 FIX: is_text_present calls crop_image (module-level import from airtest.aircv).
        # Patch pw.crop_image — not pw.aircv.crop_image.
        screen = make_rgb_screen()
        pw.G.DEVICE.snapshot.return_value = screen
        with patch.object(pw, "find_all_text", return_value=["42"]):
            with patch.object(pw, "crop_image", return_value=screen) as mock_crop:
                area = (0, 0, 50, 50)
                pw.is_text_present("42", area=area)
                mock_crop.assert_called_with(screen, area)

    def test_no_crop_without_area(self):
        pw.G.DEVICE.snapshot.return_value = make_rgb_screen()
        with patch.object(pw, "find_all_text", return_value=[]) as mock_fat:
            pw.is_text_present("x")
            mock_fat.assert_called_once()


# ===========================================================================
# 4. partial_search
# ===========================================================================

class TestPartialSearch:

    def test_returns_match_on_full_screen(self):
        t = make_template()
        t.match_in = MagicMock(return_value=(100, 200))
        pw.G.DEVICE.snapshot.return_value = make_rgb_screen()
        assert pw.partial_search(t) == (100, 200)

    def test_returns_none_when_no_match(self):
        t = make_template()
        t.match_in = MagicMock(return_value=None)
        pw.G.DEVICE.snapshot.return_value = make_rgb_screen()
        assert pw.partial_search(t) is None

    def test_crops_when_area_given(self):
        # BUG-10 FIX: partial_search calls crop_image (module-level import), not pw.aircv.crop_image.
        screen = make_rgb_screen()
        cropped = make_rgb_screen(50, 50)
        t = make_template()
        t.match_in = MagicMock(return_value=(10, 10))
        pw.G.DEVICE.snapshot.return_value = screen
        area = (0, 0, 50, 50)
        with patch.object(pw, "crop_image", return_value=cropped) as mock_crop:
            pw.partial_search(t, area=area)
            mock_crop.assert_called_with(screen, area)


# ===========================================================================
# 5. wait_exists
# ===========================================================================

class TestWaitExists:

    def test_returns_immediately_when_found_first_try(self):
        t = make_template()
        pw.sleep.reset_mock()
        with patch.object(pw, "partial_search", return_value=(50, 50)):
            result = pw.wait_exists(t, timeout=5)
        assert result == (50, 50)
        pw.sleep.assert_not_called()

    def test_retries_until_found(self):
        t = make_template()
        responses = [None, None, (80, 90)]
        with patch.object(pw, "partial_search", side_effect=responses):
            result = pw.wait_exists(t, timeout=10, interval=0.01)
        assert result == (80, 90)

    def test_returns_false_on_timeout(self):
        t = make_template()
        with patch.object(pw, "partial_search", return_value=None):
            with patch("pixon.pixonwrapper.time") as mock_time:
                mock_time.time.side_effect = [0, 999]
                result = pw.wait_exists(t, timeout=1, interval=0.01)
        assert result is False


# ===========================================================================
# 6. wait_not_exists
# ===========================================================================

class TestWaitNotExists:

    def test_returns_true_when_already_absent(self):
        t = make_template()
        pw.sleep.reset_mock()
        with patch.object(pw, "partial_search", return_value=None):
            result = pw.wait_not_exists(t, timeout=5)
        assert result is True
        pw.sleep.assert_not_called()

    def test_waits_until_element_disappears(self):
        t = make_template()
        responses = [(10, 10), (10, 10), None]
        with patch.object(pw, "partial_search", side_effect=responses):
            result = pw.wait_not_exists(t, timeout=10, interval=0.01)
        assert result is True

    def test_returns_false_on_timeout(self):
        t = make_template()
        with patch.object(pw, "partial_search", return_value=(1, 1)):
            with patch("pixon.pixonwrapper.time") as mock_time:
                mock_time.time.side_effect = [0, 999]
                result = pw.wait_not_exists(t, timeout=1)
        assert result is False


# ===========================================================================
# 7. try_touch
# ===========================================================================

class TestTryTouch:

    def test_touches_template_when_found(self):
        t = make_template()
        pw.touch.reset_mock()
        with patch.object(pw, "partial_search", return_value=(100, 200)):
            result = pw.try_touch(t)
        assert result is True
        pw.touch.assert_called_once_with((100, 200))

    def test_returns_false_and_logs_when_not_found(self):
        t = make_template()
        with patch.object(pw, "partial_search", return_value=None):
            with patch.object(pw, "log_error") as mock_log:
                result = pw.try_touch(t)
        assert result is False
        mock_log.assert_called_once()

    def test_accepts_coordinate_directly(self):
        pw.touch.reset_mock()
        result = pw.try_touch((300, 400))
        assert result is True
        pw.touch.assert_called_once_with((300, 400))


# ===========================================================================
# 8. try_touch_and_wait
# ===========================================================================

class TestTryTouchAndWait:

    def test_returns_true_and_sleeps(self):
        t = make_template()
        pw.touch.reset_mock()
        pw.sleep.reset_mock()
        with patch.object(pw, "wait_exists", return_value=(50, 60)):
            result = pw.try_touch_and_wait(t, wait_time=2)
        assert result is True
        pw.touch.assert_called_once_with((50, 60))
        pw.sleep.assert_called_once_with(2)

    def test_returns_false_when_not_found(self):
        t = make_template()
        with patch.object(pw, "wait_exists", return_value=False):
            with patch.object(pw, "log_error") as mock_log:
                result = pw.try_touch_and_wait(t)
        assert result is False
        mock_log.assert_called_once()

    def test_coordinate_touches_directly(self):
        pw.touch.reset_mock()
        result = pw.try_touch_and_wait((100, 200), wait_time=1)
        assert result is True
        pw.touch.assert_called_once_with((100, 200))


# ===========================================================================
# 9. try_touch_and_hold
# ===========================================================================

class TestTryTouchAndHold:

    def test_holds_for_given_duration(self):
        t = make_template()
        pw.touch.reset_mock()
        with patch.object(pw, "wait_exists", return_value=(70, 80)):
            result = pw.try_touch_and_hold(t, hold_time=3)
        assert result is True
        pw.touch.assert_called_once_with((70, 80), duration=3)

    def test_returns_false_when_not_found(self):
        t = make_template()
        with patch.object(pw, "wait_exists", return_value=False):
            with patch.object(pw, "log_error") as mock_log:
                result = pw.try_touch_and_hold(t)
        assert result is False
        mock_log.assert_called_once()


# ===========================================================================
# 10. teststep decorator
# ===========================================================================

class TestTeststepDecorator:

    def test_wrapped_function_is_called(self):
        mock_fn = MagicMock(return_value="ok")
        mock_fn.__name__ = "my_step"
        decorated = pw.teststep(mock_fn)
        with patch.object(pw, "log_info"):
            result = decorated("arg1", key="val")
        mock_fn.assert_called_once_with("arg1", key="val")
        assert result == "ok"

    def test_preserves_function_name(self):
        @pw.teststep
        def my_named_step():
            pass
        assert my_named_step.__name__ == "my_named_step"

    def test_logs_begin_and_end(self):
        @pw.teststep
        def dummy():
            return 42

        with patch.object(pw, "log_info") as mock_log:
            dummy()
        messages = [c[0][0] for c in mock_log.call_args_list]
        assert any("Begin" in m and "dummy" in m for m in messages)
        assert any("End" in m and "dummy" in m for m in messages)

    def test_passes_args_and_kwargs(self):
        received = {}

        @pw.teststep
        def capture(a, b=None):
            received["a"] = a
            received["b"] = b

        with patch.object(pw, "log_info"):
            capture(1, b=2)
        assert received == {"a": 1, "b": 2}

    def test_exception_propagates(self):
        @pw.teststep
        def failing():
            raise ValueError("boom")

        with patch.object(pw, "log_info"):
            with pytest.raises(ValueError, match="boom"):
                failing()


# ===========================================================================
# 11. preprocess_image
# ===========================================================================

@pytest.fixture
def real_cv2():
    stub = sys.modules.pop("cv2", None)
    import cv2 as real
    yield real
    sys.modules["cv2"] = stub or MagicMock()


class TestPreprocessImage:

    def test_returns_2d_array(self, real_cv2):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = pw.preprocess_image(img)
        assert result.ndim == 2

    def test_output_shape_matches_input_hw(self, real_cv2):
        img = np.zeros((80, 60, 3), dtype=np.uint8)
        result = pw.preprocess_image(img)
        assert result.shape == (80, 60)

    def test_only_binary_values(self, real_cv2):
        img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        result = pw.preprocess_image(img)
        assert set(np.unique(result)).issubset({0, 255})

    def test_dtype_is_uint8(self, real_cv2):
        img = np.zeros((30, 30, 3), dtype=np.uint8)
        assert pw.preprocess_image(img).dtype == np.uint8

    def test_all_black_input(self, real_cv2):
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        result = pw.preprocess_image(img)
        assert result.ndim == 2

    def test_all_white_input(self, real_cv2):
        img = np.full((50, 50, 3), 255, dtype=np.uint8)
        result = pw.preprocess_image(img)
        assert result.ndim == 2


# ===========================================================================
# 12. log_info / log_error
# ===========================================================================

class TestLoggingHelpers:

    def test_log_info_calls_log(self):
        with patch.object(pw, "log") as mock_log:
            pw.log_info("hello")
        mock_log.assert_called_once_with("hello", snapshot=True)

    def test_log_error_wraps_in_runtime_error(self):
        with patch.object(pw, "log") as mock_log:
            pw.log_error("something broke")
        args, _ = mock_log.call_args
        assert isinstance(args[0], RuntimeError)
        assert "something broke" in str(args[0])

    def test_log_info_snapshot_false(self):
        with patch.object(pw, "log") as mock_log:
            pw.log_info("msg", snapshot=False)
        mock_log.assert_called_once_with("msg", snapshot=False)
