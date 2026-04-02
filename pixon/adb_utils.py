# adb_utils.py
import subprocess
import json
from airtest.core.api import shell, stop_app
import pixon.pixonwrapper as wrapper

PACKAGE = "com.woodpuzzle.pin3d"
ACTIVITY = f"{PACKAGE}/com.pixon.studio.CustomUnityActivity"

def _is_app_running():
    """Check if the target app is currently running."""
    try:
        output = shell("dumpsys window | grep mCurrentFocus")
        return PACKAGE in output
    except:
        return False

def _send_intent(payload, warm_start=False):
    """Send an ADB intent with the given payload."""
    json_str = json.dumps(payload, separators=(',', ':'))
    if warm_start:
        cmd = f"am start --activity-single-top -n {ACTIVITY} --es json '{json_str}'"
    else:
        cmd = f"am start -n {ACTIVITY} --es json '{json_str}'"
    full_cmd = f"adb shell \"{cmd}\""
    wrapper.log_info(f"Sending ADB intent: {full_cmd}")
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            wrapper.log_warning(f"ADB intent failed: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        wrapper.log_error(f"ADB exception: {e}")
        return False

def cold_start_with_json(payload):
    """Cold start the app with a custom payload."""
    stop_app(PACKAGE)
    return _send_intent(payload, warm_start=False)

def warm_send_json(payload):
    """Send a payload to a running app."""
    if not _is_app_running():
        wrapper.log_warning("App not running, cannot warm send")
        return False
    return _send_intent(payload, warm_start=True)

def cold_start_with_level(level):
    """Cold start the app at a specific level."""
    return cold_start_with_json({"level": level})

def cold_start_with_coin(coin):
    """Cold start the app with a specific coin amount."""
    return cold_start_with_json({"coin": coin})

def cold_start_with_booster(booster_dict):
    """Cold start the app with specified boosters."""
    return cold_start_with_json({"booster": booster_dict})

def cold_start_with_fake_ads(enabled):
    """Cold start the app with fake ads mode."""
    return cold_start_with_json({"fakeads": enabled})

def cold_start_with_autorotate(enabled):
    """Cold start the app with auto‑rotation enabled/disabled."""
    return cold_start_with_json({"autorotate": enabled})

def cold_start_with_combined(level=None, coin=None, booster=None, fakeads=None, autorotate=None, autoplay=None, playspeed=None):
    """Cold start the app with a comprehensive payload."""
    payload = {}
    if level is not None: payload["level"] = level
    if coin is not None: payload["coin"] = coin
    if booster is not None: payload["booster"] = booster
    if fakeads is not None: payload["fakeads"] = fakeads
    if autorotate is not None: payload["autorotate"] = autorotate
    if autoplay is not None: payload["autoplay"] = autoplay
    if playspeed is not None: payload["playspeed"] = playspeed
    return cold_start_with_json(payload) if payload else False

def set_level(level):
    """Set the app's level while running."""
    return warm_send_json({"level": level})

def set_coin(coin):
    """Set the app's coin amount while running."""
    return warm_send_json({"coin": coin})

def set_booster(booster_dict):
    """Set boosters while the app is running."""
    return warm_send_json({"booster": booster_dict})

def set_fake_ads(enabled):
    """Enable or disable fake ads while the app is running."""
    return warm_send_json({"fakeads": enabled})

def set_autorotate(enabled):
    """Enable or disable auto‑rotation while the app is running."""
    return warm_send_json({"autorotate": enabled})

def set_autoplay(enabled):
    """Enable or disable AutoAgent while the app is running."""
    return warm_send_json({"autoplay": enabled})

def set_playspeed(speed):
    """Set the game time scale while the app is running."""
    return warm_send_json({"playspeed": speed})

def set_combined(level=None, coin=None, booster=None, fakeads=None, autorotate=None, autoplay=None, playspeed=None):
    """Set a combined payload while the app is running."""
    payload = {}
    if level is not None: payload["level"] = level
    if coin is not None: payload["coin"] = coin
    if booster is not None: payload["booster"] = booster
    if fakeads is not None: payload["fakeads"] = fakeads
    if autorotate is not None: payload["autorotate"] = autorotate
    if autoplay is not None: payload["autoplay"] = autoplay
    if playspeed is not None: payload["playspeed"] = playspeed
    return warm_send_json(payload) if payload else False

def set_system_time(datetime_str: str):
    """Set system time (requires emulator or root)."""
    subprocess.run(f"adb shell settings put global auto_time 0", shell=True)
    subprocess.run(f"adb shell date -s \"{datetime_str}\"", shell=True)

def set_system_timezone(timezone_str: str):
    """Set system timezone (requires emulator or root)."""
    subprocess.run(f"adb shell settings put global timezone {timezone_str}", shell=True)