# conftest_daily.py
import time
import random
from airtest.core.api import exists, sleep, stop_app
import pixon.pixonwrapper as wrapper
from pixon.pages.home_page import HomePage
from pixon.pages.cheat_page import CheatPage
from pixon.pages.setting_page import SettingPage
from pixon.pages.game_page import GamePage
from pixon.pages.daily_mission import DailyMissionPage
from pixon.pages.lucky_spin import LuckySpinPage
from pixon.adb_utils import (cold_start_with_combined, cold_start_with_level, set_combined,
                       set_level, set_coin, set_booster, set_system_time)

package_name = "com.woodpuzzle.pin3d"
DEFAULT_TARGET_LEVEL = 11
DEFAULT_PRE_LEVEL_MIN = 7
DEFAULT_PRE_LEVEL_MAX = 8
LEVEL_CHECK_INTERVAL = 10
LEVEL_WAIT_TIMEOUT = 300


# ==================== UI HELPERS ====================
def open_app_with_fake_ads(home: HomePage) -> None:
    cold_start_with_combined(fakeads=True)
    close_all_popups(home)

def close_all_popups(home: HomePage, repeat: int = 5) -> None:
    closed = 0
    for _ in range(repeat):
        if exists(home.btn_close):
            home.close_popup()
            sleep(1)
            closed += 1
        else:
            break
    if closed:
        wrapper.log_info(f"Closed {closed} popup(s)")

def go_home_clean(home: HomePage, retries: int = 3) -> None:
    close_all_popups(home)
    if home.is_at_home():
        wrapper.log_info("Already at home")
        close_all_popups(home)
        return
    for attempt in range(retries):
        close_all_popups(home)
        if home.go_home(force=False, retries=2):
            sleep(1)
            close_all_popups(home)
            if home.is_at_home():
                wrapper.log_info("Home screen confirmed")
                return
        wrapper.log_warning(f"go_home_clean attempt {attempt+1} failed")
    assert False, "Not at home after navigation"


# ==================== GAME & LEVEL HELPERS ====================
def _enter_game_and_get_level(home: HomePage, game: GamePage) -> int:
    if home.is_at_home():
        home.click_play()
        sleep(3)
    return game.get_current_level()

def _wait_for_splash_and_enter_game(home: HomePage, game: GamePage) -> int:
    if not wrapper.wait_not_exists(home.splash_screen_icon, timeout=60, interval=1):
        wrapper.log_info("Splash still showing after 60s")
    close_all_popups(home)
    return _enter_game_and_get_level(home, game)

def _autoplay_to_level(game: GamePage, target_level: int, timeout: int = LEVEL_WAIT_TIMEOUT) -> None:
    set_combined(level=1, fakeads=True, autoplay=True)
    start = time.time()
    while time.time() - start < timeout:
        current_lv = game.get_current_level()
        if current_lv >= target_level:
            set_combined(autoplay=False)
            wrapper.log_info(f"Autoplay reached level {target_level}")
            return
        sleep(5)
    raise AssertionError(f"Autoplay failed to reach level {target_level} in {timeout}s")

def _advance_levels(cheat: CheatPage, game: GamePage, target_level: int) -> None:
    current_lv = game.get_current_level()
    if current_lv >= target_level:
        return
    for lv in range(current_lv, target_level):
        set_level(lv + 1)
        sleep(1)
        cheat.open_cheat()
        cheat.win_level_and_continue()
        sleep(2)
    wrapper.log_info(f"Advanced from level {current_lv} to {target_level}")

def _set_level_and_win(cheat: CheatPage, home:HomePage, level: int) -> None:
    home.click_play()
    set_level(level)
    sleep(1)
    cheat.open_cheat()
    cheat.win_level_and_continue()
    sleep(3)


# ==================== SETUP / TEARDOWN ====================
def setup_fresh_install(
    home: HomePage,
    game: GamePage,
    setting: SettingPage,
) -> None:
    go_home_clean(home)
    setting.delete_progress(assume_at_home=True)
    _wait_for_splash_and_enter_game(home, game)
    _autoplay_to_level(game, 3)
    sleep(1)
    set_level(DEFAULT_TARGET_LEVEL)
    sleep(2)
    game.activate_boosters()
    go_home_clean(home)

def reset_progress(
    home: HomePage,
    setting: SettingPage,
    game: GamePage,
    target_level: int = DEFAULT_TARGET_LEVEL,
    wait: int = 15,
) -> None:
    go_home_clean(home)
    setting.delete_progress(assume_at_home=True)
    sleep(wait)
    _wait_for_splash_and_enter_game(home, game)
    _autoplay_to_level(game, 3)
    sleep(1)
    set_level(target_level)
    sleep(2)
    go_home_clean(home)

def cold_start_unlock_daily_mission(
    home: HomePage,
    setting: SettingPage,
    game: GamePage,
) -> None:
    go_home_clean(home)
    setting.delete_progress(assume_at_home=True)
    _wait_for_splash_and_enter_game(home, game)
    cold_start_with_level(DEFAULT_TARGET_LEVEL)

def setup_unlocked_daily_mission(
    home: HomePage,
    cheat: CheatPage,
    game: GamePage,
    target_level: int = DEFAULT_TARGET_LEVEL,
) -> None:
    current_lv = _enter_game_and_get_level(home, game)
    if current_lv < target_level:
        _set_level_and_win(cheat, home, target_level)
        home.click_btn_next()
    go_home_clean(home)

def teardown_app() -> None:
    stop_app(package_name)


# ==================== MISSION ACTIONS ====================
def execute_mission_action(
    game: GamePage,
    cheat: CheatPage,
    daily: DailyMissionPage,
    home_page: HomePage,
    lucky_spin: LuckySpinPage,
    mission_type: str,
    value: int,
) -> None:
    daily.take_mission()
    if mission_type == "complete_levels":
        target_level = game.get_current_level() + value
        _advance_levels(cheat, game, target_level)
        go_home_clean(home_page)
    elif mission_type in ("use_booster", "use_booster_drill", "use_booster_hammer", "use_booster_magnet"):
        booster_name = mission_type.replace("use_booster_", "")
        if booster_name == "use_booster":
            booster_name = random.choice(["drill", "hammer", "magnet"])
        set_booster({booster_name: value + 10})
        sleep(1)
        game.use_booster(booster_name, value)
        go_home_clean(home_page)
    elif mission_type == "spend_coins":
        set_coin(value + 1000)
        sleep(1)
        game.spend_coins(value)
    elif mission_type == "collect_nails_red":
        set_level(game.get_current_level() + (value // 10))
        game.collect_nails("red", value)
        go_home_clean(home_page)
    elif mission_type == "collect_nails_blue":
        set_level(game.get_current_level() + (value // 10))
        game.collect_nails("blue", value)
        go_home_clean(home_page)
    elif mission_type == "lucky_spin":
        lucky_spin.roll_out()
    elif mission_type == "watch_ads":
        pass
    elif mission_type == "play_minutes":
        pass
    elif mission_type == "complete_levels_kill":
        target_level = game.get_current_level() + value
        _autoplay_to_level(game, target_level)
        open_app_with_fake_ads(home_page)
    else:
        wrapper.log_warning(f"Unknown mission type: {mission_type}")


# ==================== VALIDATION HELPERS ====================
def check_lucky(lucky: LuckySpinPage) -> bool:
    if wrapper.wait_not_exists(lucky.label_lucky_spin, timeout=5, interval=1):
        return True
    return False

def wait_for_next_day(time: int) -> None:
    set_system_time("24*3600*{int}")