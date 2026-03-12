# pages/daily_mission.py
from common.base_page import BasePage
from .home_page import get_template, HomePage
from airtest.core.api import sleep
from airtest.aircv import crop_image 
import pixon.pixonwrapper as wrapper
import re


class DailyMissionPage(BasePage):
    btn_daily_mission = get_template("home_page/btn_daily_mission.png", (-0.397, -0.542))

    tap_to_continue = get_template("tap_to_continue.png",          (-0.004, 0.55))
    btn_close        = get_template("system_function/btn_close.png",  ( 0.365, -0.858))

    btn_daily_mission_notify = get_template("home_page/icon_daily_mission_notify.png", (-0.396, -0.543))
    btn_play_daily = get_template("daily_mission/btn_play_daily.png",  (0.261, -0.233))
    btn_collect       = get_template("daily_mission/btn_collect.png",      ( 0.2,   0.1  ))
    exp_milestone_boxes = [
        get_template("daily_mission/box_30.png",  (-0.128, -0.469)),
        get_template("daily_mission/box_70.png",  ( 0.122, -0.474)),
        get_template("daily_mission/box_100.png", ( 0.317, -0.478)),
    ]

    MISSION_LIST_AREA = (100, 300, 600, 800)
    EXP_VALUE_AREA    = (300, 500, 400, 550)

    # ------------------------------------------------------------------

    def check_daily_mission_appear(self) -> bool:
        HomePage().go_home(force=True)
        self.handle_popup(self.btn_close, timeout=1)
        sleep(1)
        return bool(self.wait_for_element(self.btn_daily_mission, timeout=2))

    def complete_daily_mission_tutorial(self) -> None:
        home = HomePage()
        home.go_home(force=True)

        if self.wait_for_element(home.btn_next, timeout=5):
            self.tap(home.btn_next)

        if not self.wait_for_element(home.main_home_btn, timeout=10):
            raise AssertionError("Home screen not loaded after btn_next")

        if not self.wait_for_element(self.btn_daily_mission, timeout=5):
            raise AssertionError("Daily mission icon not found")
        self.tap(self.btn_daily_mission)
        sleep(6)

        if self.wait_for_element(self.tap_to_continue, timeout=10):
            self.tap(self.tap_to_continue)
            sleep(3)

        self.tap(self.btn_close)
        sleep(1)

        if not self.verify_daily_mission_icon_on_home():
            raise AssertionError("Icon missing after tutorial")

    def verify_daily_mission_icon_on_home(self) -> bool:
        HomePage().go_home(force=True)
        sleep(2)
        return bool(self.wait_for_element(self.btn_daily_mission, timeout=5))

    def is_notify_visible(self) -> bool:
        return bool(self.wait_for_element(self.btn_daily_mission_notify, timeout=2))

    def open_daily_mission_popup(self) -> bool:
        if not self.wait_for_element(self.btn_daily_mission, timeout=5):
            wrapper.log_error("Daily mission icon not found")
            return False
        self.tap(self.btn_daily_mission)
        sleep(2)
        return True

    def get_mission_count(self) -> int:
        return len(self._find_all_elements(self.btn_collect))

    def claim_mission(self, index: int) -> bool:
        positions = self._find_all_elements(self.btn_collect)
        if index < len(positions):
            self.tap(positions[index])
            sleep(1)
            return True
        return False

    def get_exp_progress(self) -> int:
        @wrapper.retry(times=3, delay=1)
        def _attempt():
            screen = wrapper.get_screen()
            w, h = self.get_screen_size()
            x1, y1, x2, y2 = self.EXP_VALUE_AREA
            scaled = (int(x1 * w / 720), int(y1 * h / 1280),
                      int(x2 * w / 720), int(y2 * h / 1280))
            cropped = crop_image(screen, scaled)
            for text in wrapper.find_all_text(cropped):
                match = re.search(r'\d+', text)
                if match:
                    return int(match.group())
            return 0
        return _attempt()

    def claim_exp_reward(self, milestone: int) -> bool:
        index = {30: 0, 70: 1, 100: 2}.get(milestone, -1)
        if index == -1:
            return False
        if self.wait_for_element(self.exp_milestone_boxes[index], timeout=3):
            self.tap(self.exp_milestone_boxes[index])
            sleep(1)
            return True
        return False

    def _find_all_elements(self, template, timeout=1) -> list:
        pos = template.match_in(wrapper.get_screen())
        return [pos] if pos else []
