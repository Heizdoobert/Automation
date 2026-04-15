# conftest_daily.py
import time
import random
from datetime import datetime, timedelta
from airtest.core.api import exists, sleep, stop_app
import pixon.pixonwrapper as wrapper
from pixon.pages.home_page import HomePage
from pixon.pages.cheat_page import CheatPage
from pixon.pages.setting_page import SettingPage
from pixon.pages.game_page import GamePage
from pixon.pages.daily_mission import DailyMissionPage
from pixon.pages.lucky_spin import LuckySpinPage
from pixon.adb_utils import (
    cold_start_with_combined,
    set_autoplay,
    set_param,
    cold_start_with_json,
    cold_start_with_param,
    set_system_time,
)

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
        home (HomePage): Checking home
    """
    cold_start_with_combined(
        fakeads=True,
        heart=5,
        level=3,
        booster={"drill": 20, "hammer": 20, "magnet": 20},
        coin=5000,
    )
    wrapper.log_info("Started app with fake ads, level 3, 5 hearts, boosters and coins")
    sleep(30)
    wrapper.log_info("Closing popups after starting app")
    close_all_popups(home)
    wrapper.log_info("Finished setup with fake ads")


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
    close_all_popups(home)
    if home.is_at_home():
        close_all_popups(home)
        return
    for attempt in range(retries):
        if home.go_home(force=False):
            sleep(1)
            close_all_popups(home)
            if home.is_at_home():
                return
        wrapper.log_warning(f"go_home_clean attempt {attempt + 1} failed")
    raise AssertionError("Not at home after navigation")


# ==================== GAME & LEVEL HELPERS ====================
def _enter_game_and_get_level(home: HomePage, game: GamePage) -> int:
    """Enter the game and return the current level.

    Args:
        home (HomePage): HomePage instance to check home state and start game
        game (GamePage): GamePage instance to get the current level

    Returns:
        int: The current level in the game
    """
    wrapper.log_info("Entering game to get current level")
    if home.is_at_home():
        wrapper.log_info("At home, clicking play to enter game")
        home.click_play()
        wrapper.log_info("Clicked play, waiting for game to load")
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
    wrapper.log_info("Entering game after splash")
    return _enter_game_and_get_level(home, game)


def _autoplay_to_level(
    game: GamePage, target_level: int, timeout: int = LEVEL_WAIT_TIMEOUT
) -> None:
    """Run autoplay until the target level is reached.

    Args:
        game (GamePage): GamePage instance to get the current level
        target_level (int): The target level to reach
        timeout (int, optional): Maximum time in seconds to wait for the target level. Defaults to LEVEL_WAIT_TIMEOUT.

    Raises:
        AssertionError: If the target level is not reached within the timeout.
    """
    set_autoplay(True, 2)
    wrapper.log_info(
        f"Started autoplay to reach level {target_level} with timeout of {timeout}s"
    )
    start = time.time()
    while time.time() - start < timeout:
        current_lv = game.get_current_level()
        wrapper.log_info(f"Current level: {current_lv}, Target level: {target_level}")
        if current_lv >= target_level:
            set_autoplay(False, 1)
            wrapper.log_info(f"Autoplay reached level {target_level}")
            return
        sleep(5)
    raise AssertionError(f"Autoplay failed to reach level {target_level} in {timeout}s")


def _advance_levels(
    cheat: CheatPage,
    game: GamePage,
    home_page: HomePage,
    daily: DailyMissionPage,
    target_level: int,
) -> None:
    """Advance the game level by level until the target level is reached.

    Args:
        cheat (CheatPage): CheatPage instance to control cheating actions
        game (GamePage): GamePage instance to get the current level
        target_level (int): The target level to reach
    """
    home_page.click_play()
    wrapper.log_info(f"Advancing levels to reach level {target_level}")
    current_lv = game.get_current_level()
    wrapper.log_info(f"Starting level: {current_lv}, Target level: {target_level}")
    if current_lv >= target_level:
        return
    for lv in range(current_lv, target_level):
        set_param("level", lv + 1)
        sleep(1)
        cheat.open_cheat()
        cheat.win_level_and_continue()
        wrapper.log_info(f"Advanced to level {lv + 1}")
        sleep(2)
        close_all_popups(home_page)
        daily.click_tap_to_continued()
        home_page.click_play()
    wrapper.log_info(f"Advanced from level {current_lv} to {target_level}")


def _set_level_and_win(cheat: CheatPage, home: HomePage, game: GamePage, level: int) -> None:
    """Set the level and win it to return to home.

    Args:
        cheat (CheatPage): CheatPage instance to open cheat and win the level
        home (HomePage): HomePage instance to start the game
        level (int): The level to set and win
    """
    home.click_play()
    _autoplay_to_level(game, level)
    set_param("level", level)
    sleep(3)
    cheat.open_cheat()
    cheat.win_level_and_continue()
    sleep(3)
    wrapper.log_info(f"Set level to {level} and won the level to return home")


# ==================== SETUP / TEARDOWN ====================
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
    wrapper.log_info("Deleting progress for fresh install setup")
    setting.delete_progress()
    wrapper.log_info("Waiting for progress deletion to take effect")
    sleep(20)
    _wait_for_splash_and_enter_game(home, game)
    wrapper.log_info(
        "Setting level to 3 and winning to return home for fresh install setup"
    )
    _autoplay_to_level(game, 3)
    wrapper.log_info(
        "Reached level 3, now setting to default target level for fresh install setup"
    )
    sleep(1)
    set_param("level", DEFAULT_TARGET_LEVEL)
    wrapper.log_info(f"Set level to {DEFAULT_TARGET_LEVEL} for fresh install setup")
    sleep(2)
    game.activate_boosters()
    wrapper.log_info("Activated boosters for fresh install setup")
    go_home_clean(home)
    wrapper.log_info(
        "Finished fresh install setup, now at home with default target level and boosters activated"
    )


def reset_progress(
    home: HomePage,
    cheat: CheatPage,
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
    wrapper.log_info("Deleting progress for reset setup")
    setting.delete_progress()
    wrapper.log_info("Waiting for progress deletion to take effect for reset setup")
    sleep(20)
    _set_level_and_win(cheat, home, game, 3)
    wrapper.log_info("Set level to 3 and won to return home for reset setup")
    set_param("level", target_level)
    wrapper.log_info(f"Set level to {target_level} for reset setup")
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
    setting.delete_progress()
    sleep(20)
    _wait_for_splash_and_enter_game(home, game)
    cold_start_with_param("level", DEFAULT_TARGET_LEVEL)
    wrapper.log_info(
        f"Cold started with level {DEFAULT_TARGET_LEVEL} to unlock daily mission"
    )


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
        _set_level_and_win(cheat, home, game, target_level)
        home.click_btn_next()
    go_home_clean(home)


def teardown_app() -> None:
    """Stop the app."""
    wrapper.log_info("Stopping the app for teardown")
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
    elif mission_type in (
        "use_booster",
        "use_booster_drill",
        "use_booster_hammer",
        "use_booster_magnet",
    ):
        booster_name = mission_type.replace("use_booster_", "")
        if booster_name == "use_booster":
            booster_name = random.choice(["drill", "hammer", "magnet"])
        set_param("booster", {booster_name: value + 10})
        sleep(1)
        game.use_booster(booster_name, value)
        go_home_clean(home_page)
    elif mission_type == "spend_coins":
        set_param("coin", value + 1000)
        sleep(1)
        game.spend_coins(value)
    elif mission_type == "level_run":
        home_page.click_play()
        game.get_current_level()
        _autoplay_to_level(game, game.get_current_level() + (value + 5))
        go_home_clean(home_page)
    elif mission_type == "collect_nails_red":
        home_page.click_play()
        set_param("level", game.get_current_level())
        _autoplay_to_level(game, game.get_current_level() + 10)
        go_home_clean(home_page)
    elif mission_type == "collect_nails_blue":
        set_param("level", game.get_current_level() + (value // 10))
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
        cold_start_with_json({"fakeads": True})
        sleep(20)
        close_all_popups(home_page)
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


def wait_for_next_day(hours: int = 24) -> None:
    """Setup time for test

    Args:
        hours (int, optional): Input time for the change. Defaults to 24.
    """
    target_time = datetime.now() + timedelta(hours=hours)
    time_str = target_time.strftime("%Y%m%d.%H:%M:%S")
    set_system_time(time_str)
