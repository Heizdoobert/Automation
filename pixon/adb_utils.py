# adb_utils.py
import subprocess
import json
from airtest.core.api import shell, stop_app
import pixon.pixonwrapper as wrapper

PACKAGE = "com.woodpuzzle.pin3d"
ACTIVITY = f"{PACKAGE}/com.pixon.studio.CustomUnityActivity"

# ==================== HELPERS ====================
def _is_app_running():
    try:
        output = shell(f"pidof {PACKAGE}")
        return output.strip() != ""
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

# ==================== COLD START (app is not running) ====================
def cold_start_with_json(payload):
    stop_app(PACKAGE)
    return _send_intent(payload, warm_start=False)

def cold_start_with_level(level):
    return cold_start_with_json({"level": level})

def cold_start_with_coin(coin):
    return cold_start_with_json({"coin": coin})

def cold_start_with_booster(booster_dict):
    return cold_start_with_json({"booster": booster_dict})

def cold_start_with_fake_ads(enabled):
    return cold_start_with_json({"fakeads": enabled})

def cold_start_with_autorotate(enabled):
    return cold_start_with_json({"autorotate": enabled})

def cold_start_with_autoplay(enabled: bool, playspeed: int = 2) -> bool:
    return cold_start_with_json({"autoplay": enabled, "playSpeed": playspeed if enabled else 1})

def cold_start_with_playspeed(speed: int) -> bool:
    return cold_start_with_json({"playSpeed": speed})

def cold_start_with_heart(heart_count):
    return cold_start_with_json({"heart": heart_count})

def cold_start_with_combined(level=None, coin=None, booster=None, fakeads=None,
                             autorotate=None, autoplay=None, playspeed=None, heart=None):
    payload = {}
    if level is not None: payload["level"] = level
    if coin is not None: payload["coin"] = coin
    if booster is not None: payload["booster"] = booster
    if fakeads is not None: payload["fakeads"] = fakeads
    if autorotate is not None: payload["autorotate"] = autorotate
    if autoplay is not None: payload["autoplay"] = autoplay
    if playspeed is not None: payload["playSpeed"] = playspeed
    if heart is not None: payload["heart"] = heart
    return cold_start_with_json(payload) if payload else False

# ==================== WARM START (app running) ====================
def warm_send_json(payload):
    if not _is_app_running():
        wrapper.log_warning("App not running, cannot warm send")
        return False
    return _send_intent(payload, warm_start=True)

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

def set_autoplay(enabled: bool, playspeed: int = 2) -> bool:
    return warm_send_json({"autoplay": enabled, "playSpeed": playspeed if enabled else 1})

def set_playspeed(speed: int) -> bool:
    return warm_send_json({"playSpeed": speed})

def set_heart(heart_count):
    return warm_send_json({"heart": heart_count})

def set_combined(level=None, coin=None, booster=None, fakeads=None,
                 autorotate=None, autoplay=None, playspeed=None, heart=None):
    payload = {}
    if level is not None: payload["level"] = level
    if coin is not None: payload["coin"] = coin
    if booster is not None: payload["booster"] = booster
    if fakeads is not None: payload["fakeads"] = fakeads
    if autorotate is not None: payload["autorotate"] = autorotate
    if autoplay is not None: payload["autoplay"] = autoplay
    if playspeed is not None: payload["playSpeed"] = playspeed
    if heart is not None: payload["heart"] = heart
    return warm_send_json(payload) if payload else False

# ==================== SYSTEM TIME (emulator/root) ====================
def set_system_time(datetime_str: str):
    subprocess.run(f"adb shell settings put global auto_time 0", shell=True)
    subprocess.run(f"adb shell date -s \"{datetime_str}\"", shell=True)

def set_system_timezone(timezone_str: str):
    subprocess.run(f"adb shell settings put global timezone {timezone_str}", shell=True)