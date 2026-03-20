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
from pixon.pages.lucky_spin import LuckySpinPage
from pixon.pages.remove_ads import RemoveAds
from pixon.pages.setting_page import SettingPage
from DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page = HomePage()
cheat = CheatPage()
game = GamePage()
daily = DailyMissionPage()
lucky = LuckySpinPage()
ads = RemoveAds()
setting = SettingPage()

def main():
    try:
        wrapper.launch_app_wait_load_done(package_name, home_page.splash_screen_icon)
        wrapper.log_info("=== TC21: Lucky spin (already unlocked) ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        lucky.open_spin()
        lucky.spin()
        sleep(2)
        wrapper.log_info("PASS: Lucky spin completed")
        wrapper.log_info("=== TC21 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC21 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc21_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()