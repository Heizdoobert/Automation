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
    """Setup app with fake ads on.

    Args:
        cheat (CheatPage): Open cheat mode
        home (HomePage): Checking home
        ads (RemoveAds): Setup fake ads
    """
    cold_start_with_combined(fakeads=True, heart=5, level=3, booster={"drill": 20, "hammer": 20, "magnet": 20}, coin=5000)
    sleep(20)
    close_all_popups(home)

def close_all_popups(home: HomePage, repeat: int = 5) -> None:
    """Close popups displayed on screen.

    Args:
        home (HomePage): HomePage instance to check for popups
        repeat (int, optional): Number of times to repeat checking for popups. Defaults to 5.
    """
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
    """Navigate to and confirm home screen.

    Args:
        home (HomePage): HomePage instance for navigation and state checking
        retries (int, optional): Number of retry attempts to reach home. Defaults to 3.
    """
    wrapper.log_info("=== go_home_clean started ===")
    close_all_popups(home)
    wrapper.log_info("After close_all_popups")
    at_home = home.is_at_home()
    wrapper.log_info(f"is_at_home() returned: {at_home}")
    if at_home:
        wrapper.log_info("Already at home")
        close_all_popups(home)
        wrapper.log_info("After second close_all_popups")
        return
    for attempt in range(retries):
        wrapper.log_info(f"go_home_clean attempt {attempt+1} started")
        close_all_popups(home)
        wrapper.log_info("After close_all_popups in loop")
        if home.go_home(force=False):
            wrapper.log_info("go_home returned True")
            sleep(1)
            close_all_popups(home)
            wrapper.log_info("After close_all_popups post-go_home")
            at_home = home.is_at_home()
            wrapper.log_info(f"is_at_home() returned: {at_home}")
            if at_home:
                wrapper.log_info("Home screen confirmed")
                return
            else:
                wrapper.log_info("is_at_home was False after go_home")
        else:
            wrapper.log_info("go_home returned False")
        wrapper.log_warning(f"go_home_clean attempt {attempt+1} failed")
    assert False, "Not at home after navigation"


# ==================== GAME & LEVEL HELPERS ====================
def _enter_game_and_get_level(home: HomePage, game: GamePage) -> int:
    """Enter the game and return the current level.

    Args:
        home (HomePage): HomePage instance to check home state and start game
        game (GamePage): GamePage instance to get the current level

    Returns:
        int: The current level in the game
    """
    if home.is_at_home():
        home.click_play()
        sleep(3)
    return game.get_current_level()

def _wait_for_splash_and_enter_game(home: HomePage, game: GamePage) -> int:
    """Wait for splash screen to disappear then enter game and return current level.

    Args:
        home (HomePage): HomePage instance to check splash screen and close popups
        game (GamePage): GamePage instance to get the current level

    Returns:
        int: The current level in the game
    """
    if not wrapper.wait_not_exists(home.splash_screen_icon, timeout=60, interval=1):
        wrapper.log_info("Splash still showing after 60s")
    close_all_popups(home)
    return _enter_game_and_get_level(home, game)

def _autoplay_to_level(game: GamePage, target_level: int, timeout: int = LEVEL_WAIT_TIMEOUT) -> None:
    """Run autoplay until the target level is reached.

    Args:
        game (GamePage): GamePage instance to get the current level
        target_level (int): The target level to reach
        timeout (int, optional): Maximum time in seconds to wait for the target level. Defaults to LEVEL_WAIT_TIMEOUT.

    Raises:
        AssertionError: If the target level is not reached within the timeout.
    """
    set_combined(autoplay=True, playspeed=2)
    start = time.time()
    while time.time() - start < timeout:
        current_lv = game.get_current_level()
        if current_lv >= target_level:
            set_combined(autoplay=False)
            wrapper.log_info(f"Autoplay reached level {target_level}")
            return
        sleep(5)
    raise AssertionError(f"Autoplay failed to reach level {target_level} in {timeout}s")

def _advance_levels(cheat: CheatPage, game: GamePage, home_page: HomePage, daily: DailyMissionPage, target_level: int) -> None:
    """Advance the game level by level until the target level is reached.

    Args:
        cheat (CheatPage): CheatPage instance to control cheating actions
        game (GamePage): GamePage instance to get the current level
        target_level (int): The target level to reach
    """
    home_page.click_play()
    current_lv = game.get_current_level()
    if current_lv >= target_level:
        return
    for lv in range(current_lv, target_level):
        set_level(lv + 1)
        sleep(1)
        cheat.open_cheat()
        cheat.win_level_and_continue()
        sleep(2)
        close_all_popups(home_page)
        daily.click_tap_to_continued()
        home_page.click_play()
    wrapper.log_info(f"Advanced from level {current_lv} to {target_level}")

def _set_level_and_win(cheat: CheatPage, home: HomePage, level: int) -> None:
    """Set the level and win it to return to home.

    Args:
        cheat (CheatPage): CheatPage instance to open cheat and win the level
        home (HomePage): HomePage instance to start the game
        level (int): The level to set and win
    """
    home.click_play()
    set_level(level)
    sleep(1)
    cheat.open_cheat()
    cheat.win_level_and_continue()
    sleep(3)


# ==================== SETUP / TEARDOWN ====================
import subprocess

def setup_fresh_install(
    home: HomePage,
    game: GamePage,
    setting: SettingPage,
) -> None:
    """Set up a fresh install of the game.

    Args:
        home (HomePage): HomePage instance for navigation
        cheat (CheatPage): CheatPage instance for cheating
        game (GamePage): GamePage instance for game actions
        setting (SettingPage): SettingPage instance for settings
    """
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
) -> None:
    """Reset game progress and set up to a target level.

    Args:
        home (HomePage): HomePage instance for navigation
        setting (SettingPage): SettingPage instance for settings
        cheat (CheatPage): CheatPage instance for cheating
        game (GamePage): GamePage instance for game actions
        target_level (int, optional): The target level to set after reset. Defaults to DEFAULT_TARGET_LEVEL.
        wait (int, optional): Time in seconds to wait after deleting progress. Defaults to 15.
    """
    go_home_clean(home)
    wrapper.log_info("Clearing app data via ADB")
    subprocess.run(["adb", "shell", "pm", "clear", package_name], check=True)
    wrapper.log_info("Starting app via ADB")
    try:
        subprocess.run(["adb", "shell", "am", "start", "-n", f"{package_name}/com.pixon.studio.CustomUnityActivity"], check=True)
    except Exception as e:
        wrapper.log_warning(f"Failed to start main activity: {e}")
        subprocess.run(["adb", "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"], check=True)
    wrapper.log_info("Waiting for app to start...")
    sleep(30)
    wrapper.log_info("Checking if app reached home screen...")
    for i in range(18):
        if home.is_at_home():
            wrapper.log_info(f"App reached home screen after {(i+1)*5} seconds")
            break
        wrapper.log_info(f"Waiting for home screen... (attempt {i+1}/18)")
        sleep(5)
    else:
        wrapper.log_error("App did not reach home screen after 90 seconds")
        try:
            home.take_screenshot("app_start_debug.png")
            wrapper.log_info("Took screenshot for debugging: app_start_debug.png")
        except Exception as e:
            wrapper.log_warning(f"Failed to take screenshot: {e}")
        raise AssertionError("App did not start or did not reach home screen after clearing data")
    _set_level_and_win(cheat, home, 3)
    set_level(target_level)
    go_home_clean(home)

def cold_start_unlock_daily_mission(
    home: HomePage,
    setting: SettingPage,
    game: GamePage,
) -> None:
    """Unlock the daily mission by starting from a cold start at the target level.

    Args:
        home (HomePage): HomePage instance for navigation
        setting (SettingPage): SettingPage instance for settings
        game (GamePage): GamePage instance for game actions
    """
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
    """Step to unlock the daily mission by setting the level if needed.

    Args:
        home (HomePage): HomePage instance for navigation
        cheat (CheatPage): CheatPage instance for cheating
        game (GamePage): GamePage instance for game actions
        target_level (int, optional): The target level to reach. Defaults to DEFAULT_TARGET_LEVEL.
    """
    current_lv = _enter_game_and_get_level(home, game)
    if current_lv < target_level:
        _set_level_and_win(cheat, home, target_level)
        home.click_btn_next()
    go_home_clean(home)

def teardown_app() -> None:
    """Stop the app.

    """
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
    """Execute a daily mission action based on the mission type.

    Args:
        game (GamePage): GamePage instance for game actions
        cheat (CheatPage): CheatPage instance for cheating
        daily (DailyMissionPage): DailyMissionPage instance to take the mission
        home_page (HomePage): HomePage instance for navigation
        ads (RemoveAds): RemoveAds instance for ads-related actions
        lucky_spin (LuckySpinPage): LuckySpinPage instance for lucky spin
        mission_type (str): The type of mission to execute
        value (int): The value associated with the mission (e.g., number of levels, coins, etc.)
    """
    daily.take_mission()
    if mission_type == "complete_levels":
        target_level = game.get_current_level() + value
        _advance_levels(cheat, game, home_page, daily, target_level)
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
        _autoplay_to_level(game, game.get_current_level() + (value // 10))
        go_home_clean(home_page)
    elif mission_type == "collect_nails_blue":
        set_level(game.get_current_level() + (value // 10))
        _autoplay_to_level(game, game.get_current_level() + (value // 10))
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
        teardown_app()
        open_app_with_fake_ads(home_page)
    else:
        wrapper.log_warning(f"Unknown mission type: {mission_type}")


# ==================== VALIDATION HELPERS ====================
def check_lucky(lucky: LuckySpinPage) -> bool:
    """Check if the lucky spin is not present (i.e., the lucky spin has been used or is not available).

    Args:
        lucky (LuckySpinPage): LuckySpinPage instance to check the lucky spin label

    Returns:
        bool: True if the lucky spin label does not exist (meaning the spin is done or not available), False otherwise
    """
    if wrapper.wait_not_exists(lucky.label_lucky_spin, timeout=5, interval=1):
        return True
    return False

def wait_for_next_day(time: int) -> None:
    set_system_time("24*3600*{int}")
