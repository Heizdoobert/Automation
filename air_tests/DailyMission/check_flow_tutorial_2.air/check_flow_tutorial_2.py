# check_flow_tutorial_2.py
# Standalone smoke test: launch → fake ads → click Play → autoplay đến lv10

import sys
import time
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

# use home_page to avoid shadowing Airtest's built-in `home` function
home_page: HomePage = HomePage()
daily: DailyMissionPage = DailyMissionPage()
game: GamePage = GamePage()
ads: RemoveAds = RemoveAds()
cheat: CheatPage = CheatPage()
setting: SettingPage = SettingPage()


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

        # Vào game để đọc level
        home_page.click_play()
        sleep(3)

        current_lv = game.get_current_level()
        wrapper.log_info(f"Current level: {current_lv}")

        if current_lv < 10:
            wrapper.log_info("level < 10: Cheat is active...")
            cheat.open_cheat()
            cheat.auto_play_on()
            cheat.close_cheat()

            timeout = 150
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                current_lv = game.get_current_level()
                wrapper.log_info(f"Checking level... Current: {current_lv}")
                if current_lv >= 10:
                    wrapper.log_info(f"Goal to lv target: Level {current_lv}")
                    cheat.open_cheat()
                    cheat.auto_play_off()
                    cheat.close_cheat()
                    break
                sleep(10)
            else:
                raise AssertionError(f"TIMEOUT: level 10 not reached in {timeout}s")
        else:
            wrapper.log_info("Reached level 10+, skip Cheat.")

        wrapper.log_info("=====Script done=====")

    except Exception as e:
        wrapper.log_error(f"Test failed: {str(e)}")
        snapshot(filename="error_screen.png")
    finally:
        stop_app(package_name)


if __name__ == "__main__":
    main()
