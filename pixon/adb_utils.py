# adb_utils.py
import subprocess
import json
import sys
from airtest.core.api import shell, stop_app
import pixon.pixonwrapper as wrapper

PACKAGE = "com.woodpuzzle.pin3d"
ACTIVITY = f"{PACKAGE}/com.pixon.studio.CustomUnityActivity"


def _is_app_running():
    try:
        output = shell(f"pidof {PACKAGE}")
        return output.strip() != ""
    except Exception:
        return False


def _send_intent(payload, warm_start=False):
    """Send ADB intent using PowerShell with $payload variable (exact required syntax)."""
    if payload is None:
        wrapper.log_error("Payload is None, cannot send intent")
        return False

    # Convert payload to JSON string
    if isinstance(payload, dict):
        json_str = json.dumps(payload, separators=(',', ':'))
    else:
        json_str = str(payload)

    # Escape single quotes for PowerShell
    escaped_json = json_str.replace("'", "''")

    # Build the adb command part (without variable expansion)
    if warm_start:
        adb_cmd = f"am start --activity-single-top -n {ACTIVITY} --es json '$payload'"
    else:
        adb_cmd = f"am start -n {ACTIVITY} --es json '$payload'"

    # Full PowerShell command: set variable and run adb
    ps_cmd = f"$payload='{escaped_json}'; adb shell \"{adb_cmd}\""
    wrapper.log_info(f"Sending ADB intent via PowerShell: {ps_cmd}")

    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            wrapper.log_warning(f"ADB intent failed: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        wrapper.log_error(f"ADB exception: {e}")
        return False


# ==================== COLD START ====================
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


def cold_start_with_autoplay(enabled, playspeed=2):
    payload = {"autoplay": enabled}
    if enabled:
        payload["playSpeed"] = playspeed
    return cold_start_with_json(payload)


def cold_start_with_playspeed(speed):
    return cold_start_with_json({"playSpeed": speed})


def cold_start_with_heart(heart):
    return cold_start_with_json({"heart": heart})


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
    return cold_start_with_json(payload)


# ==================== WARM START ====================
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


def set_autoplay(enabled, playspeed=2):
    payload = {"autoplay": enabled}
    if enabled:
        payload["playSpeed"] = playspeed
    return warm_send_json(payload)


def set_playspeed(speed):
    return warm_send_json({"playSpeed": speed})


def set_heart(heart):
    return warm_send_json({"heart": heart})


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
    return warm_send_json(payload)


# ==================== SYSTEM HELPERS ====================
def set_system_time(datetime_str: str):
    subprocess.run("adb shell settings put global auto_time 0", shell=True)
    subprocess.run(f"adb shell date -s \"{datetime_str}\"", shell=True)

# =============== PROCESS & NETWORK CONTROL ==============

def run_adb_command(cmd: list, timeout: int =30) -> tuple:
    """
    run an ADB command and return (returncode, stdout, stderr)
    """
    try:
        proc = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        wrapper.log_error(f"ADB command timed out after {timeout}s: {' '.join(cmd)}")
        return -1, "". "Timeout"
    except Exception as e:
        warpper.log_error(f"ADB command failed: {e}")
        return -1, "", str(e)

def stop_adb_server() -> bool:
    """
    Kill ADB server
    """
    return run_adb_command(["kill-server"])[0] == 0

def disable_wifi() -> bool:
    """
    Turn off Wi-Fi on device (requires root/emulator)
    """
    return run_adb_command(["shell", "svc", "wifi", "disable"])[0] == 0

def enable_wifi() -> bool:
    """
    Turn on Wi-Fi on device
    """
    return run_adb_command(["shell", "svc", "wifi", "enable"])[0] == 0

def set_airplane_mode(on: bool) -> bool:
    cmd = ["shell", "settings", "put", "global", "airplane_mode_on", "1" if on else "0"]
    ret, _, _ = run_adb_command(cmd)
    if ret == 0:
        broadcast_cmd = ["shell", "am", "broadcast", "-a","android.intent.action.AIRPLANE_MODE"]
        run_adb_command(broadcast_cmd)
    return ret == 0

def stop_subprocess(proc: subprocess.Popen, timeout: float = 5.0) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
