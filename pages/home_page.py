# pages/home_page.py
from common.base_page import BasePage
from pathlib import Path
from airtest.core.api import Template, sleep
import pixon.pixonwrapper as wrapper

IMAGE_DIR = Path(__file__).resolve().parent / "images"

def get_template(relative_path, record_pos, resolution=(720, 1280)):
    return Template(str(IMAGE_DIR / relative_path), record_pos=record_pos, resolution=resolution)


class HomePage(BasePage):

    # Loading screen locators
    splash_screen_icon = get_template("splash_screen_icon.png",  ( 0.051, -0.164))
    splash_home_icon   = get_template("label_main_home.png",    (-0.006, 0.792))

    # Main home locators
    main_home_btn = get_template("home_page/btn_main_home.png",  (0.001, 0.794))
    main_play_btn = get_template("home_page/btn_play.png",  (0.003, 0.497))

    # System function locators
    btn_setting  = get_template("system_function/btn_setting.png",  (0.425, -0.811))
    btn_home     = get_template("system_function/btn_home.png",     (-0.01, 0.357))
    btn_close    = get_template("system_function/btn_close.png",    (0.347, -0.294))
    btn_tutorial = get_template("system_function/btn_tutorial.png", (-0.415, -0.799))
    btn_next     = get_template("system_function/btn_next.png",     (-0.01, 0.256))
    btn_delete   = get_template("system_function/btn_delete.png",   (-0.001,  0.201))

    def is_at_home(self) -> bool:
        result = self.wait_for_element(self.splash_home_icon, timeout=2)
        self.log_step(f"Check splash_home_icon: {result is not None}")
        return bool(result)

    def go_home(self, force: bool = False) -> bool:
        if force or not self.is_at_home():
            self.tap(self.btn_setting)
            if not self.wait_for_element(self.btn_home, timeout=5):
                return False
            self.tap(self.btn_home)
            if not self.wait_for_element(self.splash_home_icon, timeout=5):
                return False
        return True

    def click_play(self) -> None:
        self.tap(self.main_play_btn)
        sleep(5)

    def close_popup(self) -> None:
        if wrapper.wait_exists(self.btn_close, timeout=2):
            self.tap(self.btn_close)
