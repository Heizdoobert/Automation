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
from air_tests.DailyMission.conftest_daily import unlock_daily_mission_fresh, teardown_app

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
        
        wrapper.log_info("=== TC03: New user – popup tutorial after unlock ===")

        unlock_daily_mission_fresh(home_page, cheat, game, ads, setting, target_level=11)

        daily.complete_tutorial_from_popup()

        if not daily.verify_daily_mission_icon_on_home():
            raise AssertionError("Icon Daily Mission doesn't appear after tutorial")

        wrapper.log_info("=== TC03 PASSED ===")

    except Exception as e:
        wrapper.log_error(f"TC03 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc03_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()


