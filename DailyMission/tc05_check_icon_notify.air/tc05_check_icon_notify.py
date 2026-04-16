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
from DailyMission.conftest_daily import reset_progress, teardown_app, open_app_with_fake_ads

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
        wrapper.log_info("=== TC05: Check notify on icon before joining ===")
        reset_progress(home_page, cheat, setting, game, target_level=11)
        if not daily.is_notify_visible():
            raise AssertionError("Notify not visible on icon")
        wrapper.log_info("PASS: Notify visible")
        daily.open_daily_mission_popup()
        sleep(2)
        daily.complete_tutorial_from_popup()
        if daily.is_notify_visible():
            raise AssertionError("Notify still visible after joining")
        wrapper.log_info("PASS: Notify gone after join")
        wrapper.log_info("=== TC05 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC05 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc05_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()
