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

def cold_start_with_combined(level=None, coin=None, booster=None, fakeads=None, autorotate=None, autoplay=None, playspeed=None):
    """Cold start with comprehensive payload support.
    
    Args:
        level (int, optional): Set absolute level (min=1)
        coin (int, optional): Set absolute coin amount
        booster (dict, optional): Set booster counts by name
        fakeads (bool, optional): Enable/disable fake ads mode
        autorotate (bool, optional): Enable/disable auto-rotation
        autoplay (bool, optional): Enable/disable AutoAgent
        playspeed (int, optional): Set game time scale (1, 2, 4, etc.)
    """
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
    return warm_send_json({"level": level})

def set_coin(coin):
    return warm_send_json({"coin": coin})

def set_booster(booster_dict):
    return warm_send_json({"booster": booster_dict})

def set_fake_ads(enabled):
    return warm_send_json({"fakeads": enabled})

def set_autorotate(enabled):
    """Enable/disable auto-rotation."""
    return warm_send_json({"autorotate": enabled})

def set_autoplay(enabled):
    """Enable/disable AutoAgent for automated gameplay actions."""
    return warm_send_json({"autoplay": enabled})

def set_playspeed(speed):
    """Set game time scale (1, 2, 4, etc.)."""
    return warm_send_json({"playspeed": speed})

def set_combined(level=None, coin=None, booster=None, fakeads=None, autorotate=None, autoplay=None, playspeed=None):
    """Set combined payload with all supported keys.
    
    Args:
        level (int, optional): Set absolute level (min=1)
        coin (int, optional): Set absolute coin amount
        booster (dict, optional): Set booster counts by name
        fakeads (bool, optional): Enable/disable fake ads mode
        autorotate (bool, optional): Enable/disable auto-rotation
        autoplay (bool, optional): Enable/disable AutoAgent
        playspeed (int, optional): Set game time scale (1, 2, 4, etc.)
    """
    payload = {}
    if level is not None: payload["level"] = level
    if coin is not None: payload["coin"] = coin
    if booster is not None: payload["booster"] = booster
    if fakeads is not None: payload["fakeads"] = fakeads
    if autorotate is not None: payload["autorotate"] = autorotate
    if autoplay is not None: payload["autoplay"] = autoplay
    if playspeed is not None: payload["playspeed"] = playspeed
    return warm_send_json(payload) if payload else False
