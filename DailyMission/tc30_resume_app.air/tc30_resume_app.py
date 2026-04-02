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
from DailyMission.conftest_daily import setup_unlocked_daily_mission, execute_mission_action, teardown_app, open_app_with_fake_ads

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
        open_app_with_fake_ads(cheat, home_page, ads)
        wrapper.log_info("=== TC30: Resume app after multitasking ===")
        setup_unlocked_daily_mission(home_page, cheat, game, target_level=11)
        execute_mission_action(game, cheat, daily, home_page, ads, lucky, "complete_levels", 3)
        exp_before = daily.get_exp_progress()
        keyevent("HOME")
        sleep(2)
        start_app(package_name)
        sleep(3)
        home_page.go_home(force=True)
        exp_after = daily.get_exp_progress()
        if exp_after != exp_before:
            raise AssertionError(f"EXP changed after resume: {exp_before} -> {exp_after}")
        wrapper.log_info("PASS: Data preserved after resume")
        wrapper.log_info("=== TC30 PASSED ===")
    except Exception as e:
        wrapper.log_error(f"TC30 failed: {str(e)}\n{traceback.format_exc()}")
        snapshot(filename="tc30_error.png")
    finally:
        teardown_app()

if __name__ == "__main__":
    main()
