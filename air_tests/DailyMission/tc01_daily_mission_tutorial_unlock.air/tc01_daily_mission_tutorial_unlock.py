# tc01_daily_mission_tutorial_unlock.py
# TC01: fresh install → autoplay to lv10 → win level → Daily Mission popup appears → complete tutorial

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
from air_tests.DailyMission.conftest_daily import setup_fresh_install, teardown_app

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page: HomePage = HomePage()
cheat: CheatPage = CheatPage()
game: GamePage = GamePage()
daily: DailyMissionPage = DailyMissionPage()
ads: RemoveAds = RemoveAds()
setting: SettingPage = SettingPage()


def main():
    try:
        setup_fresh_install(home_page, cheat, game, ads, setting, level_timeout=260)

        wrapper.log_info("Begin check daily mission")
        cheat.open_cheat()
        cheat.win_level()
        cheat.close_cheat()
        wrapper.log_info("Waiting for win animation...")
        sleep(5)

        # complete tutorial (the method now uses force=False and corrected templates)
        daily.complete_daily_mission_tutorial()

        wrapper.log_info("=====Script done=====")

    except Exception as e:
        wrapper.log_error(f"Test failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="error_screen.png")
    finally:
        teardown_app()


if __name__ == "__main__":
    main()

