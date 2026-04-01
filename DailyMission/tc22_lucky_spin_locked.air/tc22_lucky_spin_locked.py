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
from pixon.pages.setting_page import SettingPage
from pixon.pages.lucky_spin import LuckySpinPage
from DailyMission.conftest_daily import teardown_app, open_app_with_fake_ads, setup_fresh_install

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page = HomePage()
cheat = CheatPage()
game = GamePage()
daily = DailyMissionPage()
lucky = LuckySpinPage()
setting = SettingPage()
lucky = LuckySpinPage()

def main():
    try:
        open_app_with_fake_ads(home_page)
        wrapper.log_info("=== TC22: Lucky spin not unlocked but mission exists ===")
        setup_fresh_install(home_page, game, setting)
        if not wrapper.wait_not_exists(lucky.label_lucky_spin):
            return AssertionError("Lucky Spin showing too late")
        wrapper.log_info("PASS: Mission displayed (manual check required)")
        wrapper.log_info("=== TC22 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC22 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc22_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()