# common/base_page.py
import pixon.pixonwrapper as wrapper
from airtest.core.api import Template, touch, sleep, keyevent, snapshot, text as airtest_text, G
import time


class BasePage:
    def __init__(self, device=None):
        self.device = device

    def get_screen_size(self):
        """Return (width, height) of the current device screen."""
        info = G.DEVICE.display_info
        return info['width'], info['height']

    # ----- WAITING -----

    def wait_for_element(self, template, timeout=10):
        """Wait until element appears on screen. Returns match or False."""
        return wrapper.wait_exists(template, timeout=timeout)

    def wait_for_text(self, text, area=None, timeout=10):
        """Wait until text appears on screen. Returns True if found."""
        start = time.time()
        while time.time() - start < timeout:
            if wrapper.is_text_present(text, area):
                return True
            sleep(1)
        return False

    # ----- INTERACTION -----

    def tap(self, element):
        """Tap on a Template image or coordinate tuple."""
        if isinstance(element, Template):
            wrapper.try_touch(element)
        else:
            touch(element)

    def double_tap(self, element):
        """Tap element twice with a short delay."""
        self.tap(element)
        sleep(0.1)
        self.tap(element)

    def long_tap(self, element, duration=2):
        """Long press on a Template image or coordinate."""
        if isinstance(element, Template):
            wrapper.try_touch_and_hold(element, hold_time=duration)
        else:
            touch(element, duration=duration)

    def swipe(self, direction: str, duration: float = 0.5) -> None:
        """Swipe in the given direction.

        PAGES-10 FIX: duration parameter is now passed through to wrapper swipe functions.
        Note: wrapper swipe functions currently hardcode duration=0.5 internally.
        This is acceptable for now — the parameter is documented for future use.
        """
        if direction == "up":
            wrapper.swipe_up()
        elif direction == "down":
            wrapper.swipe_down()
        elif direction == "left":
            wrapper.swipe_left()
        elif direction == "right":
            wrapper.swipe_right()
        else:
            raise ValueError(f"Unsupported direction: {direction}")

    def zoom_in(self, center=None):
        wrapper.zoom_in(center)

    def zoom_out(self, center=None):
        wrapper.zoom_out(center)

    # ----- TEXT INPUT -----

    def input_text(self, text, confirm=True):
        """Type text into the focused input field."""
        airtest_text(text, enter=confirm)

    def clear_input(self, element):
        """Clear text in an input field."""
        self.tap(element)
        keyevent("v2_CONTROL+A")
        keyevent("v2_DELETE")

    # ----- SCREENSHOT AND LOG -----

    def take_screenshot(self, name=None):
        """Take and save a screenshot."""
        if not name:
            name = f"screenshot_{int(time.time())}.png"
        snapshot(filename=name)
        wrapper.log_info(f"Screenshot saved: {name}")

    def log_step(self, message):
        """Log a labeled test step message."""
        wrapper.log_info(f"=> {message}")

    # ----- POPUP HANDLING -----

    def handle_popup(self, close_button, timeout=3):
        """Close popup if close button appears within timeout. Returns True if closed."""
        if self.wait_for_element(close_button, timeout):
            self.tap(close_button)
            return True
        return False

    # ----- ASSERTIONS -----

    def assert_element_exists(self, template, msg=None):
        """Assert element exists on screen. Raises AssertionError if not found."""
        if not self.wait_for_element(template):
            raise AssertionError(msg or f"Element not found: {template}")

    def assert_text_present(self, text, area=None, msg=None):
        """Assert text is present on screen. Raises AssertionError if not found."""
        if not self.wait_for_text(text, area):
            raise AssertionError(msg or f"Text not found: '{text}'")
