# pages/cheat_page.py
from pixon.common.base_page import BasePage
from .home_page import get_template, HomePage
from airtest.core.api import touch, sleep, keyevent, text
import pixon.pixonwrapper as wrapper


class CheatPage(BasePage):
    cheat_menu       = get_template("cheat/menu_cheat.png",           (-0.422, -0.822))
    close_cheat_menu = get_template("cheat/btn_close_cheat_mode.png", ( 0.432, -0.821))

    list_cheat_menu = [
        get_template("cheat/btn_system_check.png", (-0.092, -0.611)),
        get_template("cheat/btn_console.png",      (-0.075, -0.326)),
        get_template("cheat/btn_options.png",      (-0.069, -0.036)),
        get_template("cheat/btn_profiler.png",     (-0.071,  0.233)),
    ]

    level_label     = get_template("cheat/console/level/jump_to_number.png", (-0.19,   0.004))
    go_to_level_btn = get_template("cheat/console/level/btn_go_to_lv.png",   (-0.265, -0.482))
    winlevel_btn    = get_template("cheat/console/level/btn_winlv.png",       (-0.287, -0.325))
    btn_break_all_piecein_wave = get_template("cheat/console/level/btn_break_all_piecein_wave.png", (-0.124, -0.167))

    speed_button = [
        get_template("cheat/console/auto_play_func/btn_speed_x1.png", (-0.383,  0.057)),
        get_template("cheat/console/auto_play_func/btn_speed_x2.png", (-0.2,    0.057)),
        get_template("cheat/console/auto_play_func/btn_speed_x4.png", ( 0.006,  0.068)),
        get_template("cheat/console/auto_play_func/btn_speed_x6.png", ( 0.206,  0.068)),
    ]
    check_box = [
        get_template("cheat/console/auto_play_func/btn_auto_play_off.png", (-0.376, -0.015)),
        get_template("cheat/console/auto_play_func/btn_auto_play_on.png",  (-0.381, -0.018)),
    ]

    def open_cheat(self) -> None:
        width, height = self.get_screen_size()
        hidden_x = int(50 * width / 720)
        hidden_y = int(640 * height / 1280)
        hidden_button = (hidden_x, hidden_y)
        for _ in range(3):
            touch(hidden_button)
        if not self.wait_for_element(self.cheat_menu, timeout=10):
            raise Exception("Cannot open cheat menu")
        self.tap(self.cheat_menu)
        sleep(2)
        if not self.wait_for_element(self.list_cheat_menu[2], timeout=5):
            raise Exception("Cannot find cheat Options tab")
        self.tap(self.list_cheat_menu[2])
        sleep(1)

    def close_cheat(self) -> None:
        sleep(2)
        self.tap(self.close_cheat_menu)

    def set_level(self, level: int) -> None:
        for _ in range(2):
            self.swipe("down")
        self.tap(self.level_label)
        keyevent("v2_CONTROL+A")
        keyevent("v2_DELETE")
        text(str(level), True)
        sleep(2)
        self.tap(self.go_to_level_btn)
        sleep(3)

    def auto_play_on(self) -> None:
        for _ in range(2):
            self.swipe("down")
        sleep(2)
        self.swipe("up")
        sleep(2)
        self.tap(self.speed_button[1])
        self.tap(self.check_box[0])

    def auto_play_off(self) -> None:
        for _ in range(2):
            self.swipe("down")
        sleep(2)
        self.swipe("up")
        sleep(2)
        self.tap(self.speed_button[0])
        self.tap(self.check_box[1])

    def win_level(self) -> None:
        for _ in range(2):
            self.swipe("down")
        self.tap(self.winlevel_btn)

    def break_all_piecein_wave(self) -> None:
        self.tap(self.btn_break_all_piecein_wave)

    def win_level_and_continue(self) -> bool:
        home = HomePage()
        self.win_level()
        self.close_cheat()
        sleep(2)
        if home.wait_for_element(home.btn_next, timeout=8):
            home.tap(home.btn_next)
            sleep(2)
            wrapper.log_info("win_level_and_continue: tapped btn_next")
            return True
        if home.wait_for_element(home.splash_home_icon, timeout=5):
            wrapper.log_info("win_level_and_continue: game went to home (milestone flow)")
            return False
        wrapper.log_info("win_level_and_continue: neither btn_next nor home found — proceeding")
        return False
