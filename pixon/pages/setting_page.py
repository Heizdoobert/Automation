# pages/setting_page.py
from pixon.common.base_page import BasePage
from .home_page import get_template, HomePage
from airtest.core.api import sleep
import pixon.pixonwrapper as wrapper


class SettingPage(BasePage):
    btn_setting          = get_template("system_function/btn_setting.png",          ( 0.425, -0.811))
    btn_music            = None
    btn_sound            = None
    btn_vibrate          = None
    btn_redeem_code_blue = get_template("settings_page/btn_redeem_code_blue.png",   (-0.014, -0.061))
    btn_save_progress    = get_template("settings_page/btn_save_progress.png",      (-0.003,  0.097))
    btn_delete_progress  = get_template("settings_page/btn_delete_progress.png",   ( 0.003,  0.042))
    blank_confirm        = get_template("settings_page/blank_confirm.png",          ( 0.003,  0.064))
    label_setting        = get_template("settings_page/label_setting.png",          ( 0.003, -0.594))

    def open_setting(self, retry: int = 5) -> bool:
        for attempt in range(retry):
            self.tap(self.btn_setting)
            sleep(2)
            if self.wait_for_element(self.label_setting, timeout=15):
                return True
            wrapper.log_warning(f"open_setting attempt {attempt+1} failed")
        wrapper.log_error("open_setting: settings panel did not open")
        return False

    def music(self) -> None:
        if self.btn_music:
            self.tap(self.btn_music)

    def sound(self) -> None:
        if self.btn_sound:
            self.tap(self.btn_sound)

    def vibrate(self) -> None:
        if self.btn_vibrate:
            self.tap(self.btn_vibrate)

    def redeem_code(self) -> None:
        self.tap(self.btn_redeem_code_blue)

    def save_progress(self) -> None:
        self.tap(self.btn_save_progress)

    def delete_progress(self, word: str = "confirm", assume_at_home: bool = False) -> None:
        home = HomePage()
        # Even if we assume we are at home, let's check and try to go home if not.
        if not home.is_at_home():
            wrapper.log_info("delete_progress: not at home — trying to go home")
            if not home.go_home(force=True):
                raise AssertionError("delete_progress: failed to navigate to home screen")

        if not self.open_setting():
            raise AssertionError("delete_progress: cannot open settings panel")
        self.save_progress()
        sleep(1)
        if not self.wait_for_element(self.btn_delete_progress, timeout=5):
            raise AssertionError("delete_progress: btn_delete_progress not found")
        self.tap(self.btn_delete_progress)
        sleep(2)
        if not self.wait_for_element(self.blank_confirm, timeout=10):
            self.take_screenshot("blank_confirm_error.png")
            wrapper.log_error("delete_progress: blank_confirm input not found")
            raise AssertionError("delete_progress: blank_confirm input not found")
        self.tap(self.blank_confirm)
        self.input_text(str(word), confirm=True)
        sleep(1)
        if not self.wait_for_element(home.btn_delete, timeout=5):
            raise AssertionError("delete_progress: btn_delete not found")
        self.tap(home.btn_delete)
        wrapper.log_info("delete_progress: confirmed — game will restart")
