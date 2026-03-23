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
from DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app, open_app_with_fake_ads

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
        open_app_with_fake_ads(cheat, home_page, ads)
        wrapper.log_info("=== TC07: Check random 5 missions per day ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        daily.open_daily_mission_popup()
        count_a = daily.get_mission_count()
        count_b = daily.get_collect_mission_count()
        if count_a != 5:
            for i in range(count_b):
                daily.claim_mission(i)
            # Close and reopen popup to refresh UI state after claiming
            daily.tap(daily.btn_close)
            sleep(2)
            daily.open_daily_mission_popup()
            count_a = daily.get_mission_count()
            if count_a != 5:
                raise AssertionError(f"Expected 5 missions, got {count_a}")
        wrapper.log_info(f"PASS: {count_a} missions displayed")
        wrapper.log_info("=== TC07 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC07 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc07_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()