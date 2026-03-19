# air_tests/DailyMission/tc03_tutorial_fresh_install.air/tc03_tutorial_fresh_install.py
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
from air_tests.DailyMission.conftest_daily import (
    setup_fresh_install, teardown_app, _enter_game_and_get_level, open_app_with_fake_ads
)

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
        wrapper.log_info("=== TC03: Fresh install — popup tutorial after unlock ===")

        setup_fresh_install(home_page, cheat, game, setting, level_timeout=260)

        _enter_game_and_get_level(home_page, game)

        cheat.open_cheat()
        cheat.win_level_and_continue()
        sleep(3)

        daily.complete_daily_mission_tutorial()

        assert daily.verify_daily_mission_icon_on_home(), \
            "TC03 FAIL: Daily Mission icon not visible after tutorial"
        wrapper.log_info("Daily Mission icon visible on Main")

        wrapper.log_info("=== TC03 PASSED ===")

    except AssertionError as e:
        wrapper.log_error(f"TC03 ASSERTION FAILED: {e}")
        snapshot(filename="tc03_assertion_error.png")
    except Exception as e:
        wrapper.log_error(f"TC03 UNEXPECTED ERROR: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc03_error.png")
    finally:
        teardown_app()


if __name__ == "__main__":
    main()
