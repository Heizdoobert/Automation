# adb_utils.py
import subprocess
import json
from airtest.core.api import shell, stop_app
import pixon.pixonwrapper as wrapper

PACKAGE = "com.woodpuzzle.pin3d"
ACTIVITY = f"{PACKAGE}/com.pixon.studio.CustomUnityActivity"

def _is_app_running():
    try:
        output = shell("dumpsys window | grep mCurrentFocus")
        return PACKAGE in output
    except:
        return False

def _send_intent(payload, warm_start=False):
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
    stop_app(PACKAGE)
    return _send_intent(payload, warm_start=False)

def warm_send_json(payload):
    if not _is_app_running():
        wrapper.log_warning("App not running, cannot warm send")
        return False
    return _send_intent(payload, warm_start=True)

def cold_start_with_level(level):
    return cold_start_with_json({"level": level})

def cold_start_with_coin(coin):
    return cold_start_with_json({"coin": coin})

def cold_start_with_booster(booster_dict):
    return cold_start_with_json({"booster": booster_dict})

def cold_start_with_fake_ads(enabled):
    return cold_start_with_json({"fakeads": enabled})

def cold_start_with_autorotate(enabeld):
    return cold_start_with_json({"autorotate": enabeld})

def cold_start_with_autoplay_and_play_speed(enabled):
    return cold_start_with_json({"autoplay": enabled, "playspeed": 2 if enabled else 1})

def cold_start_with_combined(level=None, coin=None, booster=None, fakeads=None, autorotate=None, autoplay=None):
    payload = {}
    if level is not None: payload["level"] = level
    if coin is not None: payload["coin"] = coin
    if booster is not None: payload["booster"] = booster
    if fakeads is not None: payload["fakeads"] = fakeads
    if autorotate is not None: payload["autorotate"] = autorotate
    if autoplay is not None: payload["autoplay"] = autoplay
    return cold_start_with_json(payload) if payload else False

def set_level(level):
    return warm_send_json({"level": level})

def set_coin(coin):
    return warm_send_json({"coin": coin})

def set_booster(booster_dict):
    return warm_send_json({"booster": booster_dict})

def set_fake_ads(enabled):
    return warm_send_json({"fakeads": enabled})

def set_autorotate(enabled):
    return warm_send_json({"autorotate": enabled})

def set_autoplay_and_play_speed(enabled):
    return warm_send_json({"autoplay": enabled, "playspeed": 2 if enabled else 1})

def set_combined(level=None, coin=None, booster=None, fakeads=None, autorotate=None, autoplay=None):
    payload = {}
    if level is not None: payload["level"] = level
    if coin is not None: payload["coin"] = coin
    if booster is not None: payload["booster"] = booster
    if fakeads is not None: payload["fakeads"] = fakeads
    if autorotate is not None: payload["autorotate"] = autorotate
    if autoplay is not None: payload["autoplay"] = autoplay
    return warm_send_json(payload) if payload else False

def set_system_time(datetime_str: str):
    """Set system time (requires emulator or root)."""
    subprocess.run(f"adb shell settings put global auto_time 0", shell=True)
    subprocess.run(f"adb shell date -s \"{datetime_str}\"", shell=True)