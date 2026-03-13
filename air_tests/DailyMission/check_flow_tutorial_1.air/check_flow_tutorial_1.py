# air_tests/DailyMission/check_flow_tutorial_1.air/check_flow_tutorial_1.py
# Standalone smoke test:
#   launch → check if daily mission shown too early → delete + jump to lv10 + complete tutorial

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from airtest.core.api import *  # type: ignore[reportWildcardImportFromLibrary]
import pixon.pixonwrapper as wrapper
from pages.home_page import HomePage
from pages.daily_mission import DailyMissionPage
from pages.game_page import GamePage
from pages.remove_ads import RemoveAds
from pages.cheat_page import CheatPage
from pages.setting_page import SettingPage

auto_setup(__file__)

package_name = "com.woodpuzzle.pin3d"

home_page: HomePage     = HomePage()
daily: DailyMissionPage = DailyMissionPage()
game: GamePage          = GamePage()
ads: RemoveAds          = RemoveAds()
cheat: CheatPage        = CheatPage()
setting: SettingPage    = SettingPage()


def main():
    try:
        wrapper.launch_app_wait_load_done(package_name, home_page.splash_screen_icon)

        for _ in range(3):
            if exists(home_page.btn_close):
                home_page.close_popup()

        cheat.open_cheat()
        ads.fake_ads_on()
        sleep(2)
        cheat.close_cheat()
        wrapper.log_info("Remove Ads On")

        for _ in range(3):
            if exists(home_page.btn_close):
                home_page.close_popup()

        wrapper.log_info("Begin check daily mission")
        current_lv = game.get_current_level()
        wrapper.log_info(f"Level current check: {current_lv}")

        # If level >= 10 AND daily mission already shows → bug (shown too early)
        if current_lv >= 10 and daily.check_daily_mission_appear():
            wrapper.log_error("Daily mission displayed too soon — must investigate")
        else:
            wrapper.log_info("System fine — proceeding to set level 10 and complete tutorial")
            setting.delete_progress()
            sleep(20)

            # BUG-09 FIX: after delete_progress game restarts to home/lv1,
            # must open_cheat() before set_level() — cannot call cheat while at home without entering game
            cheat.open_cheat()
            cheat.set_level(10)
            cheat.win_level()
            cheat.close_cheat()
            daily.complete_daily_mission_tutorial()

        wrapper.log_info("=====Script done=====")

    except Exception as e:
        wrapper.log_error(f"Test failed: {str(e)}")
        snapshot(filename="error_screen.png")
    finally:
        stop_app(package_name)


if __name__ == "__main__":
    main()
