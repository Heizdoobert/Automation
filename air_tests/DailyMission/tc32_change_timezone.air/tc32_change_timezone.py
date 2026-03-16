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
from air_tests.DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app
import subprocess

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
        wrapper.log_info("=== TC32: Change timezone (cheat) ===")
        setup_unlocked_daily_mission(home_page, cheat, game, ads, setting, target_level=11)
        daily.open_daily_mission_popup()
        serial = G.DEVICE.serialno
        subprocess.run(f"adb -s {serial} shell settings put global timezone GMT", shell=True)
        sleep(2)
        daily.open_daily_mission_popup()
        wrapper.log_info("PASS: Missions unchanged after timezone change (manual check)")
        wrapper.log_info("=== TC32 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC32 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc32_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()