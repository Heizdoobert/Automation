import sys
import traceback
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from airtest.core.api import *
import pixon.pixonwrapper as wrapper
from pixon.common.test_flow import run_step, log_step
from pixon.pages.home_page import HomePage
from pixon.pages.cheat_page import CheatPage
from pixon.pages.game_page import GamePage
from pixon.pages.daily_mission import DailyMissionPage
from pixon.pages.remove_ads import RemoveAds
from pixon.pages.setting_page import SettingPage
from pixon.pages.lucky_spin import LuckySpinPage
from DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app, execute_mission_action, open_app_with_fake_ads, go_home_clean

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page = HomePage()
cheat = CheatPage()
game = GamePage()
daily = DailyMissionPage()
ads = RemoveAds()
setting = SettingPage()
lucky = LuckySpinPage()

def main():
    try:
        run_step("tc06 open app with fake ads", open_app_with_fake_ads, home_page)
        wrapper.log_info("=== TC06: Notify after completing mission but not claiming ===")
        run_step(
            "tc06 setup unlocked daily mission",
            setup_unlocked_daily_mission,
            home_page,
            cheat,
            game,
            11,
        )
        run_step("tc06 open daily mission popup", daily.open_daily_mission_popup)
        run_step(
            "tc06 execute complete_levels mission",
            execute_mission_action,
            game,
            cheat,
            daily,
            home_page,
            lucky,
            "complete_levels",
            3,
        )
        sleep(2)
        run_step("tc06 return home for notify check", go_home_clean, home_page)
        log_step("tc06 verify notify appears after mission completion")
        if not daily.is_notify_visible(timeout=8):
            raise AssertionError("Notify not visible after completing mission")
        wrapper.log_info("PASS: Notify visible")
        run_step("tc06 re-open daily mission popup", daily.open_daily_mission_popup)
        run_step("tc06 claim first mission", daily.claim_mission, 0)
        sleep(1)
        run_step("tc06 return home after claim", home_page.go_home, True)
        log_step("tc06 verify notify disappears after claim")
        if daily.is_notify_visible(timeout=5):
            raise AssertionError("Notify still visible after claiming")
        wrapper.log_info("PASS: Notify gone after claim")
        wrapper.log_info("=== TC06 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC06 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc06_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()