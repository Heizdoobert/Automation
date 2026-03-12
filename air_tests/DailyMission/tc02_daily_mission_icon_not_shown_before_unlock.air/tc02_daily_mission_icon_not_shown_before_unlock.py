# tc01_daily_mission_icon_not_shown_before_unlock.air/tc01_daily_mission_icon_not_shown_before_unlock.py
import sys
import traceback
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from airtest.core.api import *
import pixon.pixonwrapper as wrapper
from pages.home_page import HomePage
from pages.cheat_page import CheatPage
from pages.game_page import GamePage
from pages.daily_mission import DailyMissionPage
from pages.remove_ads import RemoveAds
from pages.setting_page import SettingPage
from air_tests.DailyMission.conftest_daily import reset_progress, teardown_app, setup_with_level

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page = HomePage()
cheat = CheatPage()
game = GamePage()
daily = DailyMissionPage()
ads = RemoveAds()
setting = SettingPage()

def main():
    try:
        wrapper.log_info("=== TC01: Check Daily Mission icon before and after unlock ===")
        reset_progress(home_page, setting, cheat, game, target_level=7, wait=150)

        wrapper.log_info("Checking at level 7...")
        home_page.go_home(force=True)
        if daily.wait_for_element(daily.btn_daily_mission, timeout=3):
            raise AssertionError("Daily Mission icon appeared at level 7!")
        wrapper.log_info("PASS: No icon at level 7")

        wrapper.log_info("Setting level to 9...")
        cheat.open_cheat()
        cheat.set_level(10)
        cheat.close_cheat()
        sleep(2)
        home_page.click_play()
        sleep(3)
        home_page.go_home(force=True)

        if daily.wait_for_element(daily.btn_daily_mission, timeout=3):
            raise AssertionError("Daily Mission icon appeared at level 10!")
        wrapper.log_info("PASS: No icon at level 10")

        wrapper.log_info("Setting level to 11...")
        cheat.open_cheat()
        cheat.set_level(11)
        cheat.close_cheat()
        sleep(2)
        cheat.open_cheat()
        cheat.win_level()
        cheat.close_cheat()
        sleep(3)
        home_page.go_home(force=True)

        if not daily.wait_for_element(daily.btn_daily_mission, timeout=5):
            raise AssertionError("Daily Mission icon did NOT appear after level 10!")
        wrapper.log_info("PASS: Icon appears after level 10")

        wrapper.log_info("=== TC01 PASSED ===")

    except Exception as e:
        wrapper.log_error(f"TC01 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc01_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()