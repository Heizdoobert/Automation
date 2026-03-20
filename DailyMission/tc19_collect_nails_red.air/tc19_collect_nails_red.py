import sys
import traceback
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from airtest.core.api import *
import pixon.pixonwrapper as wrapper
from pixon.pages.home_page import HomePage
from pixon.pages.cheat_page import CheatPage
from pixon.pages.game_page import GamePage
from pixon.pages.daily_mission import DailyMissionPage
from pixon.pages.remove_ads import RemoveAds
from pixon.pages.setting_page import SettingPage
from DailyMission.conftest_daily import setup_unlocked_daily_mission, execute_mission_action, teardown_app

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
        wrapper.log_info("=== TC19: Collect 50 red nails ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        execute_mission_action(game, cheat, "collect_nails_red", 50)
        daily.open_daily_mission_popup()
        wrapper.log_info("PASS: Collected red nails")
        wrapper.log_info("=== TC19 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC19 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc19_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()