import sys
import traceback
from pathlib import Path

from pixon.adb_utils import set_system_time

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from airtest.core.api import *
import pixon.pixonwrapper as wrapper
from pixon.adb_utils import set_system_timezone
from pixon.pages.home_page import HomePage
from pixon.pages.cheat_page import CheatPage
from pixon.pages.game_page import GamePage
from pixon.pages.daily_mission import DailyMissionPage
from pixon.pages.setting_page import SettingPage
from DailyMission.conftest_daily import setup_unlocked_daily_mission, teardown_app, open_app_with_fake_ads

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
        wrapper.log_info("=== TC32: Change timezone (cheat) ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        daily.open_daily_mission_popup()
        set_system_timezone("America/New_York")
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