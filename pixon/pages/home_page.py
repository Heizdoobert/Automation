# pages/home_page.py
from pixon.common.base_page import BasePage
from pathlib import Path
from airtest.core.api import Template, sleep
import pixon.pixonwrapper as wrapper

IMAGE_DIR = Path(__file__).resolve().parent / "images"

def get_template(relative_path, record_pos, resolution=(720, 1280)):
    return Template(str(IMAGE_DIR / relative_path), record_pos=record_pos, resolution=resolution)


class HomePage(BasePage):

    splash_screen_icon = get_template("splash_screen_icon.png",  ( 0.051, -0.164))
    splash_home_icon   = get_template("label_main_home.png",     (-0.006,  0.792))
    main_home_btn      = get_template("home_page/btn_main_home.png", ( 0.001,  0.794))
    main_play_btn      = get_template("home_page/btn_play.png",      ( 0.003,  0.497))
    btn_lucky_spin     = get_template("home_page/btn_lucky_spin.png",     (-0.401, -0.364))
    btn_setting        = get_template("system_function/btn_setting.png",  ( 0.425, -0.811))
    btn_home           = get_template("system_function/btn_home.png",     (-0.01,   0.357))
    btn_close          = get_template("system_function/btn_close.png",    ( 0.347, -0.294))
    btn_tutorial       = get_template("system_function/btn_tutorial.png", (-0.415, -0.799))
    btn_next           = get_template("system_function/btn_next.png",     (-0.01,   0.256))
    btn_delete         = get_template("system_function/btn_delete.png",   (-0.001,  0.201))
    label_setting      = get_template("settings_page/label_setting.png",  ( 0.003, -0.594))

    def is_at_home(self) -> bool:
        result = self.wait_for_element(self.splash_home_icon, timeout=2)
        self.log_step(f"Check splash_home_icon: {result is not None}")
        return bool(result)

    def _is_screen_dark(self) -> bool:
        import pixon.pixonwrapper as _w
        import numpy as np
        screen = _w.get_screen()
        mean_brightness = float(np.mean(screen))
        is_dark = mean_brightness < 30
        if is_dark:
            wrapper.log_warning(f"_is_screen_dark: brightness={mean_brightness:.1f} — screen too dark to navigate")
        return is_dark

    def go_home(self, force: bool = False, retries: int = 3) -> bool:
        for attempt in range(retries):
            if not force and self.is_at_home():
                wrapper.log_info("go_home: already at home — skip navigation")
                return True
            if self._is_screen_dark():
                wrapper.log_warning(f"go_home attempt {attempt+1}: screen dark — waiting 2s before retry")
                sleep(2)
                continue

            self.tap(self.btn_setting)
            sleep(1)
            if not self.wait_for_element(self.label_setting, timeout=5):
                wrapper.log_warning(f"go_home attempt {attempt+1}: settings panel did not open — retrying")
                sleep(2)
                continue

            if not self.wait_for_element(self.btn_home, timeout=5):
                wrapper.log_warning(f"go_home attempt {attempt+1}: btn_home not found — closing settings and retrying")
                self.tap(self.btn_close)
                sleep(2)
                continue

            self.tap(self.btn_home)
            sleep(1)
            if self.wait_for_element(self.splash_home_icon, timeout=5):
                return True

            sleep(1)
            self.tap(self.btn_home)
            if self.wait_for_element(self.splash_home_icon, timeout=8):
                return True

            wrapper.log_warning(f"go_home attempt {attempt+1}: splash_home_icon not found after two taps")
            sleep(2)

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
