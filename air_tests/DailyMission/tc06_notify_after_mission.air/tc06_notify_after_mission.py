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
from air_tests.DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app, execute_mission_action, open_app_with_fake_ads

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
        open_app_with_fake_ads(cheat, home_page, ads)
        wrapper.log_info("=== TC06: Notify after completing mission but not claiming ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        daily.open_daily_mission_popup()
        execute_mission_action(game, cheat, "complete_levels", 3)
        sleep(2)
        home_page.go_home(force=True)
        if not daily.is_notify_visible():
            raise AssertionError("Notify not visible after completing mission")
        wrapper.log_info("PASS: Notify visible")
        daily.open_daily_mission_popup()
        daily.claim_mission(0)
        sleep(1)
        home_page.go_home(force=True)
        if daily.is_notify_visible():
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