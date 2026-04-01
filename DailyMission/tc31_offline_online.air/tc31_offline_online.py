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
from pixon.pages.setting_page import SettingPage
from DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app, open_app_with_fake_ads
import subprocess

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page = HomePage()
cheat = CheatPage()
game = GamePage()
daily = DailyMissionPage()
setting = SettingPage()

def main():
    try:
        open_app_with_fake_ads(home_page)
        wrapper.log_info("=== TC31: Offline -> online ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        serial = G.DEVICE.serialno
        subprocess.run(f"adb -s {serial} shell svc wifi disable", shell=True)
        sleep(2)
        daily.open_daily_mission_popup()
        count_before = daily.get_mission_count()
        subprocess.run(f"adb -s {serial} shell svc wifi enable", shell=True)
        sleep(5)
        daily.open_daily_mission_popup()
        count_after = daily.get_mission_count()
        if count_after != count_before:
            raise AssertionError(f"Mission count changed: {count_before} -> {count_after}")
        wrapper.log_info("PASS: Missions unchanged after network toggle")
        wrapper.log_info("=== TC31 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC31 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc31_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()
