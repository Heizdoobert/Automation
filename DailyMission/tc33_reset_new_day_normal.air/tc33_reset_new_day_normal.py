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
from DailyMission.conftest_daily import setup_unlocked_daily_mission, wait_for_next_day, teardown_app, open_app_with_fake_ads

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
        wrapper.log_info("=== TC33: Reset when day changes (normal) ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        daily.open_daily_mission_popup()
        missions_before = daily.get_mission_count()
        exp_before = daily.get_exp_progress()
        wait_for_next_day(2)
        daily.open_daily_mission_popup()
        missions_after = daily.get_mission_count()
        exp_after = daily.get_exp_progress()
        if missions_after == missions_before and exp_after == exp_before:
            raise AssertionError("Data not reset after new day")
        wrapper.log_info("PASS: Data reset after new day")
        wrapper.log_info("=== TC33 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC33 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc33_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()