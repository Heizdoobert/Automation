# pages/home_page.py
from pixon.common.base_page import BasePage
from pathlib import Path
from airtest.core.api import Template, sleep, touch, keyevent, G, start_app, exists
import pixon.pixonwrapper as wrapper
import time

IMAGE_DIR = Path(__file__).resolve().parent / "images"
PACKAGE_NAME = "com.woodpuzzle.pin3d"

def get_template(relative_path, record_pos, resolution=None):
    if resolution is None:
        try:
            w = G.DEVICE.display_info['width']
            h = G.DEVICE.display_info['height']
            resolution = (w, h)
        except Exception:
            resolution = (720, 1280)
    return Template(str(IMAGE_DIR / relative_path), record_pos=record_pos, resolution=resolution)  


class HomePage(BasePage):

    splash_screen_icon = get_template("splash_screen_icon.png",  ( 0.051, -0.164))
    splash_home_icon   = get_template("label_main_home.png",     (-0.006,  0.792))
    splash_home_icon.threshold = 0.5
    main_home_btn      = get_template("home_page/btn_main_home.png", ( 0.001,  0.794))
    main_play_btn      = get_template("home_page/btn_play.png",      ( 0.003,  0.497))
    btn_lucky_spin     = get_template("home_page/btn_lucky_spin.png",     (-0.401, -0.364))
    btn_setting        = get_template("system_function/btn_setting.png",  ( 0.425, -0.811))
    btn_setting.threshold = 0.5
    btn_home           = get_template("system_function/btn_home.png",     (-0.01,   0.357))
    btn_close          = get_template("system_function/btn_close.png",    ( 0.365, -0.861))
    btn_tutorial       = get_template("system_function/btn_tutorial.png", (-0.415, -0.799))
    btn_next           = get_template("system_function/btn_next.png",     (-0.01,   0.256))
    btn_delete         = get_template("system_function/btn_delete.png",   (-0.001,  0.201))
    label_setting      = get_template("settings_page/label_setting.png",  ( 0.003, -0.594))

    def is_at_home(self) -> bool:
        end_time = time.time() + 10
        while time.time() < end_time:
            if (exists(self.splash_home_icon) or
                exists(self.main_home_btn) or
                exists(self.main_play_btn)):
                self.log_step("At home detected")
                return True
            sleep(0.5)
        self.log_step("Not at home after 10 seconds")
        return False

    def _is_screen_dark(self) -> bool:
        import pixon.pixonwrapper as _w
        import numpy as np
        screen = _w.get_screen()
        mean_brightness = float(np.mean(screen))
        is_dark = mean_brightness < 30
        if is_dark:
            wrapper.log_warning(f"_is_screen_dark: brightness={mean_brightness:.1f} — screen too dark to navigate")
        return is_dark

    def go_home(self, force: bool = False) -> bool:
        if not force and self.is_at_home():
            wrapper.log_info("go_home: already at home — skip navigation")
            return True
        if self._is_screen_dark():
            wrapper.log_warning(f"go_home: screen dark — waiting 2s before retry")
            sleep(2)
            if self.is_at_home():
                return True
        wrapper.log_info("go_home: trying home button approach")
        for i in range(10):
            self.tap(self.btn_setting)
            self.tap(self.btn_home)
            sleep(1)
            self.tap(self.btn_home)
            sleep(1)
            if self.is_at_home():
                wrapper.log_info(f"go_home: home button approach worked after {i+1} presses")
                return True
        wrapper.log_warning("go_home: home button approach failed after 10 presses")
        wrapper.log_warning("go_home: all approaches failed")
        return False

    def click_play(self) -> None:
        self.tap(self.main_play_btn)
        sleep(5)

    def close_popup(self) -> None:
        if wrapper.wait_exists(self.btn_close, timeout=2):
            self.tap(self.btn_close)

    def click_btn_next(self) -> None:
        self.tap(self.btn_next)
        sleep(2)
