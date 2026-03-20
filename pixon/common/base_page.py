# common/base_page.py
import pixon.pixonwrapper as wrapper
from airtest.core.api import Template, touch, sleep, keyevent, snapshot, text as airtest_text, G
import time


class BasePage:
    def __init__(self, device=None):
        self.device = device

    def get_screen_size(self):
        info = G.DEVICE.display_info
        return info['width'], info['height']

    def wait_for_element(self, template, timeout=10):
        return wrapper.wait_exists(template, timeout=timeout)

    def wait_for_text(self, text, area=None, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            if wrapper.is_text_present(text, area):
                return True
            sleep(1)
        return False

    def tap(self, element):
        if isinstance(element, Template):
            wrapper.try_touch(element)
        else:
            touch(element)

    def double_tap(self, element):
        self.tap(element)
        sleep(0.1)
        self.tap(element)

    def long_tap(self, element, duration=2):
        if isinstance(element, Template):
            wrapper.try_touch_and_hold(element, hold_time=duration)
        else:
            touch(element, duration=duration)

    def swipe(self, direction: str, duration: float = 0.5) -> None:
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

    def input_text(self, text, confirm=True):
        airtest_text(text, enter=confirm)

    def clear_input(self, element):
        self.tap(element)
        keyevent("v2_CONTROL+A")
        keyevent("v2_DELETE")

    def take_screenshot(self, name=None):
        if not name:
            name = f"screenshot_{int(time.time())}.png"
        snapshot(filename=name)
        wrapper.log_info(f"Screenshot saved: {name}")

    def log_step(self, message):
        wrapper.log_info(f"=> {message}")

    def handle_popup(self, close_button, timeout=3):
        if self.wait_for_element(close_button, timeout):
            self.tap(close_button)
            return True
        return False

    def assert_element_exists(self, template, msg=None):
        if not self.wait_for_element(template):
            raise AssertionError(msg or f"Element not found: {template}")

    def assert_text_present(self, text, area=None, msg=None):
        if not self.wait_for_text(text, area):
            raise AssertionError(msg or f"Text not found: '{text}'")
