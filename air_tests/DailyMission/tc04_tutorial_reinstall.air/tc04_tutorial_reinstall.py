# air_tests/DailyMission/tc04_tutorial_reinstall.air/tc04_tutorial_reinstall.py
# exception:: must be run after because need reinstall app to check it
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
from air_tests.DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app, open_app_with_fake_ads

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page = HomePage()
cheat     = CheatPage()
game      = GamePage()
daily     = DailyMissionPage()
ads       = RemoveAds()
setting   = SettingPage()


def main():
    try:
        open_app_with_fake_ads(cheat, home_page, ads)
        wrapper.log_info("=== TC04: Reinstall user (passed level 10) — notify + tutorial ===")

        setup_unlocked_daily_mission(home_page, cheat, game)

        assert daily.is_notify_visible(), \
            "TC04 FAIL Step 1: notify not visible on Daily Mission icon"
        wrapper.log_info("Step 1 PASSED: notify visible")

        assert daily.open_daily_mission_popup(), \
            "TC04 FAIL Step 2: cannot open Daily Mission popup"
        wrapper.log_info("Step 2 PASSED: popup opened")

        daily.complete_tutorial_from_popup()
        wrapper.log_info("Step 3 PASSED: tutorial completed")

        assert daily.verify_daily_mission_icon_on_home(), \
            "TC04 FAIL Step 4: Daily Mission icon not visible after tutorial"
        wrapper.log_info("Step 4 PASSED: icon visible on Main")

        wrapper.log_info("=== TC04 PASSED ===")

    except AssertionError as e:
        wrapper.log_error(f"TC04 ASSERTION FAILED: {e}")
        snapshot(filename="tc04_assertion_error.png")
    except Exception as e:
        wrapper.log_error(f"TC04 UNEXPECTED ERROR: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc04_error.png")
    finally:
        teardown_app()


if __name__ == "__main__":
    main()
