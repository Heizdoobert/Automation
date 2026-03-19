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
from air_tests.DailyMission.conftest_daily import setup_unlocked_daily_mission, execute_mission_action, teardown_app

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
        wrapper.launch_app_wait_load_done(package_name, home_page.splash_screen_icon)
        wrapper.log_info("=== TC13: Complete 3,5,10 levels mission ===")
        setup_unlocked_daily_mission(home_page, cheat, game, ads, setting, target_level=11)
        execute_mission_action(game, cheat, "complete_levels", 3)
        daily.open_daily_mission_popup()
        if not daily.wait_for_element(daily.btn_collect, timeout=5):
            raise AssertionError("Mission not marked as complete")
        wrapper.log_info("PASS: 3 levels completed mission")
        wrapper.log_info("=== TC13 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC13 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc13_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()