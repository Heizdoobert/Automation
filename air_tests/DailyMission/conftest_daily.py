import time
from airtest.core.api import exists, sleep, stop_app
import pixon.pixonwrapper as wrapper
from pages.home_page import HomePage
from pages.cheat_page import CheatPage
from pages.remove_ads import RemoveAds
from pages.setting_page import SettingPage
from pages.game_page import GamePage

package_name = "com.woodpuzzle.pin3d"
DEFAULT_TARGET_LEVEL = 11
DEFAULT_PRE_LEVEL_MIN = 7
DEFAULT_PRE_LEVEL_MAX = 8
LEVEL_CHECK_INTERVAL = 10
LEVEL_WAIT_TIMEOUT = 300

# ==================== LOW-LEVEL HELPERS ====================

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
    for attempt in range(retries):
        close_all_popups(home)
        if home.go_home(force=False, retries=2):
            sleep(1)
            close_all_popups(home)
            if home.is_at_home():
                wrapper.log_info("Home screen confirmed ✓")
                return
        wrapper.log_warning(f"go_home_clean attempt {attempt+1} failed, retrying...")
        sleep(2)
    assert False, "go_home_clean FAIL: not at home after navigation"

def _wait_for_splash_and_enter_game(home: HomePage, game: GamePage) -> int:
    if not wrapper.wait_not_exists(home.splash_screen_icon, timeout=60, interval=1):
        wrapper.log_info("Splash still showing after 60s — proceeding anyway")
    close_all_popups(home)
    if home.is_at_home():
        wrapper.log_info("At home after restart — clicking Play to enter game")
        home.click_play()
        sleep(3)
    return game.get_current_level()

def _autoplay_to_level(cheat: CheatPage, game: GamePage, ads: RemoveAds, 
                       target_level: int, timeout: int = LEVEL_WAIT_TIMEOUT) -> None:
    cheat.open_cheat()
    ads.fake_ads_on()
    cheat.auto_play_on()
    cheat.close_cheat()
    start = time.time()
    while time.time() - start < timeout:
        current_lv = game.get_current_level()
        if current_lv >= target_level:
            cheat.open_cheat()
            cheat.auto_play_off()
            cheat.close_cheat()
            return
        sleep(LEVEL_CHECK_INTERVAL)
    raise AssertionError(f"Not reach level {target_level} in {timeout}s")

def _set_level_and_win(cheat: CheatPage, level: int) -> None:
    cheat.open_cheat()
    cheat.auto_play_off()
    cheat.set_level(level)
    cheat.win_level()
    cheat.close_cheat()
    sleep(3)

# ==================== PUBLIC SETUP HELPERS ====================

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
        _autoplay_to_level(cheat, game, ads, pre_level_max, pre_level_timeout)
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
        _autoplay_to_level(cheat, game, ads, target_level, level_timeout)
    wrapper.log_info("Begin use boost")
    game.activate_boosters()

def reset_progress(
    home: HomePage,
    setting: SettingPage,
    cheat: CheatPage,
    game: GamePage,
    ads: RemoveAds,                    
    target_level: int = DEFAULT_TARGET_LEVEL,
    wait: int = 15,
) -> None:
    go_home_clean(home)
    setting.delete_progress()
    sleep(wait)
    current_lv = _wait_for_splash_and_enter_game(home, game)
    wrapper.log_info(f"Level after reset: {current_lv} — starting autoplay...")
    _autoplay_to_level(cheat, game, ads, target_level, LEVEL_WAIT_TIMEOUT)
    go_home_clean(home)

def unlock_daily_mission_fresh(
    home: HomePage,
    cheat: CheatPage,
    game: GamePage,
    ads: RemoveAds,
    setting: SettingPage,
    target_level: int = DEFAULT_TARGET_LEVEL,
) -> None:
    go_home_clean(home)
    setting.delete_progress()
    _wait_for_splash_and_enter_game(home, game)
    _autoplay_to_level(cheat, game, ads, target_level, LEVEL_WAIT_TIMEOUT)
    wrapper.log_info(f"Reached level {target_level} – popup will appear.")

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
        _set_level_and_win(cheat, target_level)
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

def teardown_app() -> None:
    stop_app(package_name)

# ==================== PLACEHOLDERS (implement later) ====================

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