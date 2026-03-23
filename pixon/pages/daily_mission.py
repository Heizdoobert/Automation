# pages/daily_mission.py
from pixon.common.base_page import BasePage
from .home_page import get_template, HomePage
from airtest.core.api import sleep
from airtest.aircv import crop_image
import pixon.pixonwrapper as wrapper
import re


class DailyMissionPage(BasePage):
    btn_daily_mission        = get_template("home_page/btn_daily_mission.png",         (-0.397, -0.542))
    tap_to_continue          = get_template("tap_to_continue.png",                     (-0.004,  0.55 ))
    btn_close                = get_template("system_function/btn_close.png",           ( 0.365, -0.858))
    btn_daily_mission_notify = get_template("home_page/btn_daily_mission_notify.png", (-0.396, -0.543))
    btn_play_daily           = get_template("daily_mission/btn_play_daily.png",        ( 0.261, -0.233))
    btn_collect              = get_template("daily_mission/btn_collect.png",           (0.261, 0.113))
    exp_milestone_boxes = [
        get_template("daily_mission/box_30.png",  (-0.128, -0.469)),
        get_template("daily_mission/box_70.png",  ( 0.122, -0.474)),
        get_template("daily_mission/box_100.png", ( 0.317, -0.478)),
    ]
    icon_reward_claim = get_template("daily_mission/icon_reward_claimed.png", (0.268, 0.454))

    MISSION_LIST_AREA = (100, 300, 600, 800)
    EXP_VALUE_AREA    = (300, 500, 400, 550)

    def check_daily_mission_appear(self) -> bool:
        HomePage().go_home(force=True)
        self.handle_popup(self.btn_close, timeout=1)
        sleep(1)
        return bool(self.wait_for_element(self.btn_daily_mission, timeout=2))

    def is_notify_visible(self) -> bool:
        return bool(self.wait_for_element(self.btn_daily_mission_notify, timeout=2))

    def open_daily_mission_popup(self) -> bool:
        if not self.wait_for_element(self.btn_daily_mission, timeout=5):
            wrapper.log_error("Daily Mission icon not found on home screen")
            return False
        self.tap(self.btn_daily_mission)
        sleep(2)
        if self.wait_for_element(self.tap_to_continue, timeout=10):
            self.tap(self.tap_to_continue)
        return True

    def verify_daily_mission_icon_on_home(self) -> bool:
        home = HomePage()
        home.go_home(force=True)
        sleep(2)
        return bool(self.wait_for_element(self.btn_daily_mission, timeout=5))

    def complete_tutorial_from_popup(self) -> None:
        if self.wait_for_element(self.tap_to_continue, timeout=10):
            self.tap(self.tap_to_continue)
            sleep(3)
            if not self.wait_for_element(self.btn_collect, timeout=5):
                wrapper.log_warning("complete_tutorial_from_popup: btn_collect not visible after tap_to_continue")
            else:
                wrapper.log_info("Mission list visible after tap_to_continue")
        else:
            wrapper.log_info("tap_to_continue not found — tutorial may have auto-dismissed")
        if self.wait_for_element(self.btn_close, timeout=5):
            self.tap(self.btn_close)
            sleep(2)
        else:
            wrapper.log_warning("complete_tutorial_from_popup: btn_close not found")

    def complete_daily_mission_tutorial(self) -> None:
        home = HomePage()
        if not home.go_home(force=False):
            home.go_home(force=True)
        if self.wait_for_element(home.btn_next, timeout=5):
            self.tap(home.btn_next)
        else:
            wrapper.log_info("btn_next not found — tutorial may already be triggered")
        if not self.wait_for_element(home.main_home_btn, timeout=10):
            raise AssertionError("complete_daily_mission_tutorial: home did not load after btn_next")
        if not self.wait_for_element(self.btn_daily_mission, timeout=5):
            raise AssertionError("complete_daily_mission_tutorial: btn_daily_mission not visible on home")
        self.tap(self.btn_daily_mission)
        sleep(6)
        if self.wait_for_element(self.tap_to_continue, timeout=10):
            self.tap(self.tap_to_continue)
            sleep(3)
            if not self.wait_for_element(self.btn_collect, timeout=5):
                wrapper.log_warning("complete_daily_mission_tutorial: btn_collect not visible after tap_to_continue")
            else:
                wrapper.log_info("Mission list visible after tap_to_continue")
        else:
            wrapper.log_info("tap_to_continue not found — may have auto-dismissed")
        if self.wait_for_element(self.btn_close, timeout=5):
            self.tap(self.btn_close)
            sleep(2)
        if not self.verify_daily_mission_icon_on_home():
            raise AssertionError("complete_daily_mission_tutorial: Daily Mission icon not visible after tutorial")

    def get_mission_count(self) -> int:
        return len(self._find_all_elements(self.btn_play_daily))

    def get_collect_mission_count(self) -> int:
        return len(self._find_all_elements(self.btn_collect))
    
    def get_icon_claim_reward(self) -> int:
        return len(self._find_all_elements(self.icon_reward_claim))

    def claim_mission(self, index: int) -> bool:
        positions = self._find_all_elements(self.btn_collect)
        if index < len(positions):
            pos = positions[index]
            if isinstance(pos, dict):
                pos = pos['result']
            self.tap(pos)
            sleep(1)
            wrapper.log_info(f"Claimed mission {index + 1}")
            return True
        wrapper.log_warning(f"Mission index {index} out of range (total {len(positions)})")
        return False
    
    def take_mission(self):
        play_missions = self._find_all_elements(self.btn_play_daily)
        if len(play_missions) != 0:
            self.tap(self.btn_play_daily)

    def get_exp_progress(self) -> int:
        @wrapper.retry(times=3, delay=1, exceptions=(Exception,))
        def _attempt():
            screen = wrapper.get_screen()
            w, h = self.get_screen_size()
            x1, y1, x2, y2 = self.EXP_VALUE_AREA
            scaled = (
                int(x1 * w / 720), int(y1 * h / 1280),
                int(x2 * w / 720), int(y2 * h / 1280),
            )
            cropped = crop_image(screen, scaled)
            for t in wrapper.find_all_text(cropped):
                m = re.search(r'\d+', t)
                if m:
                    return int(m.group())
            return 0
        return _attempt()

    def claim_exp_reward(self, milestone: int) -> bool:
        index = {30: 0, 70: 1, 100: 2}.get(milestone, -1)
        if index == -1:
            wrapper.log_warning(f"claim_exp_reward: unknown milestone {milestone}")
            return False
        if self.wait_for_element(self.exp_milestone_boxes[index], timeout=3):
            self.tap(self.exp_milestone_boxes[index])
            sleep(1)
            wrapper.log_info(f"Claimed {milestone} EXP reward")
            return True
        return False

    def _find_all_elements(self, template, timeout=1) -> list:
        screen = wrapper.get_screen()
        pos = template.match_all_in(screen)
        return pos if pos else []