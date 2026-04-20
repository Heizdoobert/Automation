# conftest_daily.py
import os
import time
import random
from datetime import datetime, timedelta
from airtest.core.api import exists, sleep, stop_app
import pixon.pixonwrapper as wrapper
from pixon.common.test_flow import ensure_home, log_step, run_step
from pixon.pages.home_page import HomePage
from pixon.pages.cheat_page import CheatPage
from pixon.pages.setting_page import SettingPage
from pixon.pages.game_page import GamePage
from pixon.pages.daily_mission import DailyMissionPage
from pixon.pages.lucky_spin import LuckySpinPage
from pixon.adb_utils import (
    clear_app_data,
    cold_start_with_combined,
    set_autoplay,
    set_param,
    cold_start_with_json,
    cold_start_with_param,
    set_system_time,
)

package_name = os.getenv("GAME_PACKAGE", "com.woodpuzzle.pin3d")
DEFAULT_TARGET_LEVEL = 11
DEFAULT_PRE_LEVEL_MIN = 7
DEFAULT_PRE_LEVEL_MAX = 8
LEVEL_CHECK_INTERVAL = 10
LEVEL_WAIT_TIMEOUT = 300


# ==================== UI HELPERS ====================
def get_default_start_profile() -> dict:
    """Return a reusable default app-start profile that can be overridden by env vars."""
    return {
        "fakeads": True,
        "heart": int(os.getenv("GAME_START_HEART", "5")),
        "level": int(os.getenv("GAME_START_LEVEL", "3")),
        "booster": {
            "drill": int(os.getenv("GAME_START_DRILL", "20")),
            "hammer": int(os.getenv("GAME_START_HAMMER", "20")),
            "magnet": int(os.getenv("GAME_START_MAGNET", "20")),
        },
        "coin": int(os.getenv("GAME_START_COIN", "5000")),
    }


def open_app_with_profile(home: HomePage, profile: dict, wait_seconds: int = 30) -> None:
    """Open app with a provided profile payload for reusable test setup across suites."""
    run_step("cold start app with profile payload", cold_start_with_combined, **profile)
    wrapper.log_info(f"Applied start profile: {profile}")
    sleep(wait_seconds)
    run_step("close startup popups", close_all_popups, home)


def open_app_with_fake_ads(home: HomePage) -> None:
    """Setup app with fake ads on.

    Args:
        home (HomePage): Checking home
    """
    profile = get_default_start_profile()
    wrapper.log_info("Using default start profile for fake-ads setup")
    open_app_with_profile(home, profile=profile, wait_seconds=30)
    wrapper.log_info("Finished setup with fake ads")


def close_all_popups(home: HomePage, repeat: int = 5) -> None:
    """Close popups displayed on screen.

    Args:
        home (HomePage): HomePage instance to check for popups
        repeat (int, optional): Number of times to repeat checking for popups. Defaults to 5.
    """
    log_step(f"close_all_popups scan start (repeat={repeat})")
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
    else:
        wrapper.log_info("No popup to close")


def go_home_clean(home: HomePage, retries: int = 3) -> None:
    try:
        run_step("ensure app is at home", ensure_home, home, close_all_popups, retries, 1)
    except AssertionError:
        has_close = bool(exists(home.btn_close))
        has_setting = bool(exists(home.btn_setting))
        has_home = bool(exists(home.btn_home))
        has_main_home = bool(exists(home.main_home_btn))
        has_main_play = bool(exists(home.main_play_btn))
        raise AssertionError(
            "Not at home after navigation "
            f"(close={has_close}, setting={has_setting}, home={has_home}, "
            f"main_home={has_main_home}, main_play={has_main_play})"
        )


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

    for attempt in range(3):
        try:
            return game.get_current_level()
        except RuntimeError as exc:
            wrapper.log_warning(
                f"get_current_level failed on attempt {attempt + 1}/3: {exc}"
            )
            if attempt == 0:
                wrapper.log_info("Retrying enter-game flow by normalizing back to home")
                try:
                    home.go_home(force=True)
                    sleep(2)
                    home.click_play()
                except Exception as play_exc:
                    wrapper.log_warning(f"Retry enter-game flow failed: {play_exc}")
            sleep(2)

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
    wrapper.log_info(f"Started autoplay to reach level {target_level}")
    start = time.time()
    while True:
        current_lv = game.get_current_level()
        elapsed = time.time() - start
        wrapper.log_info(
            f"Elapsed: {elapsed:.1f}s ,Current lv: {current_lv}, Target: {target_level}"
        )
        if current_lv >= target_level:
            set_autoplay(False, 1)
            wrapper.log_info(
                f"Autoplay reached level {target_level}, after {elapsed:.2f} seconds"
            )
            return
        sleep(5)


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


def _set_level_and_win(
    cheat: CheatPage, home: HomePage, game: GamePage, level: int
) -> None:
    """Set the level, with optional win step to return to home.

    Args:
        cheat (CheatPage): CheatPage instance to open cheat and win the level
        home (HomePage): HomePage instance to start the game
        level (int): The level to set. For level 3, win step is skipped due to gameplay bug.
    """
    run_step("enter level by clicking play", home.click_play)
    run_step("autoplay to base level 3", _autoplay_to_level, game, 3)
    run_step(f"set level to {level}", set_param, "level", level)
    sleep(3)
    if level == 3:
        wrapper.log_warning(
            "Skip win_level at level 3 due to known gameplay bug; keep flow in-game"
        )
        return

    run_step("open cheat menu", cheat.open_cheat)
    run_step("win current level and continue", cheat.win_level_and_continue)
    sleep(3)
    wrapper.log_info(f"Set level to {level} and won the level to return home")


# ==================== SETUP / TEARDOWN ====================
def setup_fresh_install(
    home: HomePage,
    game: GamePage,
    setting: SettingPage,
) -> None:
    """Set up a fresh install state by clearing app data and returning home.

    Args:
        home (HomePage): HomePage instance for navigation
        game (GamePage): GamePage instance for game actions
        setting (SettingPage): Kept for compatibility with existing callers.
    """
    run_step("navigate to home before fresh install reset", go_home_clean, home)
    wrapper.log_info("Clearing app data for fresh install setup")
    if not clear_app_data():
        raise AssertionError("setup_fresh_install: clear_app_data failed")
    sleep(10)
    run_step("restart app with fake ads after clear", open_app_with_fake_ads, home)
    run_step("return to home after setup", go_home_clean, home)
    wrapper.log_info("Finished fresh install setup, now at home with cleared progress")


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
    run_step("navigate to home before reset", go_home_clean, home)
    wrapper.log_info("Deleting progress for reset setup")
    run_step("delete progress", setting.delete_progress)
    wrapper.log_info("Waiting for progress deletion to take effect for reset setup")
    sleep(20)
    run_step("set base level 3 setup", _set_level_and_win, cheat, home, game, 3)
    wrapper.log_info("Completed base level-3 setup for reset flow")
    run_step(f"set target level {target_level}", set_param, "level", target_level)
    wrapper.log_info(f"Set level to {target_level} for reset setup")
    run_step("return to home after reset", go_home_clean, home)


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
    run_step("navigate to home before cold unlock", go_home_clean, home)
    run_step("delete progress", setting.delete_progress)
    sleep(20)
    run_step("wait splash and enter game", _wait_for_splash_and_enter_game, home, game)
    run_step(
        f"cold start with level {DEFAULT_TARGET_LEVEL}",
        cold_start_with_param,
        "level",
        DEFAULT_TARGET_LEVEL,
    )
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
    current_lv = run_step("read current level", _enter_game_and_get_level, home, game)
    if current_lv < target_level:
        run_step(
            f"set and win to target level {target_level}",
            _set_level_and_win,
            cheat,
            home,
            game,
            target_level,
        )
        run_step("click next after unlock flow", home.click_btn_next)
    run_step("return to home after unlock", go_home_clean, home)


def teardown_app() -> None:
    """Stop the app."""
    wrapper.log_info("Stopping the app for teardown")
    wrapper.log_info(f"Teardown package: {package_name}")
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
    log_step(f"execute_mission_action: type={mission_type}, value={value}")
    run_step("take mission", daily.take_mission)
    if mission_type == "complete_levels":
        target_level = game.get_current_level() + value
        log_step(f"complete_levels target={target_level}")
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
        run_step(
            f"set booster inventory for {booster_name}",
            set_param,
            "booster",
            {booster_name: value + 10},
        )
        sleep(1)
        run_step(f"use booster {booster_name} x{value}", game.use_booster, booster_name, value)
        go_home_clean(home_page)
    elif mission_type == "spend_coins":
        run_step("set coin amount for spend mission", set_param, "coin", value + 1000)
        sleep(1)
        run_step(f"spend coins amount={value}", game.spend_coins, value)
    elif mission_type == "level_run":
        run_step("enter game", home_page.click_play)
        run_step("read current level", game.get_current_level)
        _autoplay_to_level(game, game.get_current_level() + (value + 5))
        go_home_clean(home_page)
    elif mission_type == "collect_nails_red":
        run_step("enter game", home_page.click_play)
        run_step("sync level param", set_param, "level", game.get_current_level())
        _autoplay_to_level(game, game.get_current_level() + 10)
        go_home_clean(home_page)
    elif mission_type == "collect_nails_blue":
        run_step(
            "set level for collect_nails_blue",
            set_param,
            "level",
            game.get_current_level() + (value // 10),
        )
        _autoplay_to_level(game, game.get_current_level() + (value // 10))
        go_home_clean(home_page)
    elif mission_type == "lucky_spin":
        run_step("run lucky spin", lucky_spin.roll_out)
    elif mission_type == "watch_ads":
        log_step("watch_ads mission: placeholder (no action yet)")
    elif mission_type == "play_minutes":
        log_step("play_minutes mission: placeholder (no action yet)")
    elif mission_type == "complete_levels_kill":
        target_level = game.get_current_level() + value
        _autoplay_to_level(game, target_level)
        run_step("teardown app", teardown_app)
        run_step("cold start app after kill mission", cold_start_with_json, {"fakeads": True})
        sleep(20)
        run_step("close popups after restart", close_all_popups, home_page)
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
