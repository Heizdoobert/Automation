# air_tests/DailyMission/tc02_daily_mission_icon_not_shown_before_unlock.air/tc02_daily_mission_icon_not_shown_before_unlock.py
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
from DailyMission.conftest_daily import (
    reset_progress, teardown_app, open_app_with_fake_ads,
    _set_level_and_win, go_home_clean
)

auto_setup(__file__)

# Add device connection check
from airtest.core.api import connect_device
from airtest.core.error import NoDeviceError

# Try to connect to any available device
G.DEVICE.connect()
if not G.device:
    raise RuntimeError("No devices available. Please connect your Android device or check ADB connection.")

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
        wrapper.log_info("=== TC02: Check Daily Mission icon before and after unlock ===")

        reset_progress(home_page, setting, cheat, game, target_level=7, wait=15)

        go_home_clean(home_page)
        if daily.wait_for_element(daily.btn_daily_mission, timeout=3):
            raise AssertionError("Daily Mission icon appeared at level 7!")
        wrapper.log_info("PASS: No icon at level 7")

        wrapper.log_info("Setting level to 10 via ADB and winning...")
        _set_level_and_win(cheat, home_page, 10)
        go_home_clean(home_page)

        if daily.wait_for_element(daily.btn_daily_mission, timeout=3):
            raise AssertionError("Daily Mission icon appeared after winning level 10!")
        wrapper.log_info("PASS: No icon after winning level 10")

        wrapper.log_info("Setting level to 11 via ADB and winning...")
        _set_level_and_win(cheat, home_page, 11)
        go_home_clean(home_page)

        if not daily.wait_for_element(daily.btn_daily_mission, timeout=5):
            raise AssertionError("Daily Mission icon did NOT appear after winning level 11!")
        wrapper.log_info("PASS: Icon appears after winning level 11")

        wrapper.log_info("=== TC02 PASSED ===")

    except Exception as e:
        wrapper.log_error(f"TC02 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc02_error.png")
    finally:
        teardown_app()


if __name__ == "__main__":
    main()