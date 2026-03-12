import time
from airtest.core.api import exists, sleep, stop_app
import pixon.pixonwrapper as wrapper
from pages.home_page import HomePage
from pages.cheat_page import CheatPage
from pages.remove_ads import RemoveAds
from pages.setting_page import SettingPage
from pages.game_page import GamePage

package_name = "com.woodpuzzle.pin3d"
DEFAULT_TARGET_LEVEL = 10
DEFAULT_PRE_LEVEL_MIN = 7
DEFAULT_PRE_LEVEL_MAX = 8
LEVEL_CHECK_INTERVAL = 10
LEVEL_WAIT_TIMEOUT = 300


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


def go_home_clean(home: HomePage) -> None:
    close_all_popups(home)
    home.go_home(force=False)
    sleep(1)
    close_all_popups(home)
    assert home.is_at_home(), "go_home_clean FAIL: not at home after navigation"
    wrapper.log_info("Home screen confirmed ✓")


def _wait_for_splash_and_enter_game(home: HomePage, game: GamePage) -> int:
    if not wrapper.wait_not_exists(home.splash_screen_icon, timeout=60, interval=1):
        wrapper.log_info("Splash still showing after 60s — proceeding anyway")
    close_all_popups(home)
    if home.is_at_home():
        wrapper.log_info("At home after restart — clicking Play to enter game")
        home.click_play()
        sleep(3)
    return game.get_current_level()


def setup_app(home: HomePage, cheat: CheatPage, ads: RemoveAds) -> None:
    wrapper.launch_app_wait_load_done(package_name, home.splash_screen_icon)
    close_all_popups(home)
    cheat.open_cheat()
    ads.fake_ads_on()
    sleep(2)
    cheat.close_cheat()
    wrapper.log_info("Remove Ads On")
    go_home_clean(home)
    assert home.is_at_home(), "SETUP FAIL: not at home after launch"


def launch_and_reach_pre_level(
    home: HomePage,
    cheat: CheatPage,
    game: GamePage,
    ads: RemoveAds,
    pre_level_min: int = DEFAULT_PRE_LEVEL_MIN,
    pre_level_max: int = DEFAULT_PRE_LEVEL_MAX,
    pre_level_timeout: int = 180,
) -> None:
    wrapper.log_info(f"launch_and_reach_pre_level: checking home...")
    close_all_popups(home)
    if home.is_at_home():
        wrapper.log_info("Already at home — skip pre-level phase.")
        return
    current_lv = game.get_current_level()
    wrapper.log_info(f"Not at home. Current level: {current_lv}")
    if current_lv == 0:
        cheat.open_cheat()
        ads.fake_ads_on()
        sleep(2)
        cheat.auto_play_on()
        cheat.close_cheat()
        wrapper.log_info(f"Autoplay x2 ON — waiting for level {pre_level_min}-{pre_level_max}...")
        start_time = time.time()
        while (time.time() - start_time) < pre_level_timeout:
            sleep(LEVEL_CHECK_INTERVAL)
            current_lv = game.get_current_level()
            wrapper.log_info(f"Level check: {current_lv}")
            if pre_level_min <= current_lv <= pre_level_max:
                wrapper.log_info(f"Pre-level reached: {current_lv} — stopping autoplay.")
                cheat.open_cheat()
                cheat.auto_play_off()
                cheat.close_cheat()
                break
        else:
            raise AssertionError(
                f"launch_and_reach_pre_level TIMEOUT: lv {pre_level_min}-{pre_level_max} "
                f"not reached in {pre_level_timeout}s. Last lv: {current_lv}"
            )
    elif current_lv > pre_level_max:
        wrapper.log_info(f"Level {current_lv} already past pre-level range — going home.")
    else:
        wrapper.log_info(f"Level {current_lv} in valid range — going home.")
    go_home_clean(home)


def setup_fresh_install(
    home: HomePage,
    cheat: CheatPage,
    game: GamePage,
    ads: RemoveAds,
    setting: SettingPage,
    target_level: int = DEFAULT_TARGET_LEVEL,
    level_timeout: int = 260,
) -> None:
    wrapper.launch_app_wait_load_done(package_name, home.splash_screen_icon)
    launch_and_reach_pre_level(home, cheat, game, ads)
    close_all_popups(home)
    setting.delete_progress()
    current_lv = _wait_for_splash_and_enter_game(home, game)
    wrapper.log_info(f"Level after fresh install: {current_lv}")
    if current_lv < target_level:
        wrapper.log_info(f"level < {target_level}: starting autoplay cheat...")
        cheat.open_cheat()
        ads.fake_ads_on()
        sleep(2)
        cheat.auto_play_on()
        cheat.close_cheat()
        start_time = time.time()
        while (time.time() - start_time) < level_timeout:
            current_lv = game.get_current_level()
            wrapper.log_info(f"Checking level... Current: {current_lv}")
            if current_lv >= target_level:
                wrapper.log_info(f"Reached target level: {current_lv} ✓")
                break
            sleep(LEVEL_CHECK_INTERVAL)
        else:
            raise AssertionError(
                f"setup_fresh_install TIMEOUT: lv {target_level} not reached "
                f"in {level_timeout}s. Last lv: {current_lv}"
            )
    else:
        wrapper.log_info(f"Already at level {current_lv} — skip autoplay.")
    wrapper.log_info("Begin use boost")
    cheat.open_cheat()
    cheat.auto_play_off()
    cheat.close_cheat()
    game.activate_boosters()


def reset_progress(
    home: HomePage,
    setting: SettingPage,
    cheat: CheatPage,
    game: GamePage,
    target_level: int = DEFAULT_TARGET_LEVEL,
    wait: int = 15,
) -> None:
    go_home_clean(home)
    setting.delete_progress()
    sleep(wait)
    current_lv = _wait_for_splash_and_enter_game(home, game)
    wrapper.log_info(f"Level after reset: {current_lv} — starting autoplay...")
    cheat.open_cheat()
    cheat.auto_play_on()
    cheat.close_cheat()
    wrapper.log_info(f"Autoplay ON — waiting for level {target_level}...")
    start = time.time()
    while time.time() - start < LEVEL_WAIT_TIMEOUT:
        current_lv = game.get_current_level()
        wrapper.log_info(f"Current level: {current_lv}")
        if current_lv >= target_level:
            wrapper.log_info(f"Reached level {current_lv} ✓")
            break
        sleep(LEVEL_CHECK_INTERVAL)
    else:
        raise AssertionError(
            f"FAIL: did not reach level {target_level} within {LEVEL_WAIT_TIMEOUT}s"
        )
    cheat.open_cheat()
    cheat.auto_play_off()
    cheat.close_cheat()
    go_home_clean(home)


def teardown_app() -> None:
    stop_app(package_name)


def setup_unlocked_daily_mission(
    home: HomePage,
    cheat: CheatPage,
    game: GamePage,
    ads: RemoveAds,
    setting: SettingPage,
    target_level: int = DEFAULT_TARGET_LEVEL,
) -> None:
    setup_app(home, cheat, ads)
    home.click_play()
    sleep(3)
    current_lv = game.get_current_level()
    wrapper.log_info(f"setup_unlocked_daily_mission: current level = {current_lv}")
    if current_lv < target_level:
        cheat.open_cheat()
        cheat.set_level(target_level)
        cheat.close_cheat()
        sleep(2)
        cheat.open_cheat()
        cheat.win_level()
        cheat.close_cheat()
        sleep(3)
    go_home_clean(home)


def setup_with_level(
    home: HomePage,
    cheat: CheatPage,
    game: GamePage,
    ads: RemoveAds,
    level: int,
) -> None:
    setup_app(home, cheat, ads)
    cheat.open_cheat()
    cheat.set_level(level)
    cheat.close_cheat()
    sleep(2)
    if home.is_at_home():
        home.click_play()
        sleep(2)
    go_home_clean(home)


def reset_daily_mission_data(
    setting: SettingPage,
    home: HomePage,
    game: GamePage,
) -> None:
    setting.delete_progress()
    _wait_for_splash_and_enter_game(home, game)


def wait_for_next_day(cheat: CheatPage) -> None:
    wrapper.log_info("wait_for_next_day: cheat time advance not implemented yet")


def execute_mission_action(
    game: GamePage,
    cheat: CheatPage,
    mission_type: str,
    value: int,
) -> None:
    if mission_type == "complete_levels":
        cheat.open_cheat()
        for _ in range(value):
            cheat.win_level()
            sleep(1)
        cheat.close_cheat()
    elif mission_type.startswith("use_booster"):
        booster = mission_type.replace("use_booster_", "")
        game.use_booster(booster, value)
    elif mission_type == "spend_coins":
        game.spend_coins(value)
    elif mission_type == "collect_nails_red":
        game.collect_nails("red", value)
    elif mission_type == "collect_nails_blue":
        game.collect_nails("blue", value)
    elif mission_type == "lucky_spin":
        wrapper.log_info("Lucky spin action not yet implemented")
    elif mission_type == "watch_ads":
        wrapper.log_info("Watch ads action not yet implemented")
    else:
        wrapper.log_warning(f"Unknown mission type: {mission_type}")