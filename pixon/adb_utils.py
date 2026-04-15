# adb_utils.py
import subprocess
import json
import base64
from airtest.core.api import stop_app
import pixon.pixonwrapper as wrapper

PACKAGE = "com.woodpuzzle.pin3d"
ACTIVITY = f"{PACKAGE}/com.pixon.studio.CustomUnityActivity"


def _is_app_running():
    try:
        result = subprocess.run(
            ["adb", "shell", "pidof", PACKAGE], capture_output=True, text=True
        )
        return result.stdout.strip() != ""
    except Exception:
        return False


def _send_intent(payload, warm_start=False, use_base64=False):
    if payload is None:
        wrapper.log_error("Payload is None, cannot send intent")
        return False

    if isinstance(payload, dict):
        json_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    else:
        json_str = str(payload)

    if use_base64:
        extra_key = "jsonBase64"
        encoded_value = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
    else:
        extra_key = "json"
        encoded_value = json_str

    escaped_value = encoded_value.replace("'", "''")

    if warm_start:
        adb_cmd = (
            f"am start --activity-single-top -n {ACTIVITY} --es {extra_key} '$payload'"
        )
    else:
        adb_cmd = f"am start -n {ACTIVITY} --es {extra_key} '$payload'"

    ps_cmd = f"$payload='{escaped_value}'; adb shell \"{adb_cmd}\""

    wrapper.log_info(f"Sending {'warm' if warm_start else 'cold'} intent: {json_str}")

    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            wrapper.log_error(f"ADB intent failed with code {result.returncode}")
            if result.stderr:
                wrapper.log_error(f"ADB error output: {result.stderr.strip()}")
            return False
        wrapper.log_info("Intent sent successfully")
        return True
    except subprocess.TimeoutExpired:
        wrapper.log_error("ADB command timed out")
    except Exception as e:
        wrapper.log_error(f"ADB exception: {e}")
        return False


# ==================== COLD START ====================
def cold_start_with_json(payload, use_base64=True):
    stop_app(PACKAGE)
    return _send_intent(payload, warm_start=False, use_base64=use_base64)


def cold_start_with_param(key, value, use_base64=True):
    return cold_start_with_json({key: value}, use_base64=use_base64)


def cold_start_with_autoplay(enabled, playspeed=None):
    payload = {"autoplay": enabled}
    if enabled:
        payload["playSpeed"] = playspeed
    return cold_start_with_json(payload)


def cold_start_with_combined(
    level=None,
    coin=None,
    booster=None,
    fakeads=None,
    autorotate=None,
    autoplay=None,
    playspeed=None,
    heart=None,
):
    payload = {}
    if level is not None:
        payload["level"] = level
    if coin is not None:
        payload["coin"] = coin
    if booster is not None:
        payload["booster"] = booster
    if fakeads is not None:
        payload["fakeads"] = fakeads
    if autorotate is not None:
        payload["autorotate"] = autorotate
    if autoplay is not None:
        payload["autoplay"] = autoplay
    if playspeed is not None:
        payload["playSpeed"] = playspeed
    if heart is not None:
        payload["heart"] = heart
    return cold_start_with_json(payload)


# ==================== WARM START ====================
def warm_send_json(payload, use_base64=True):
    if not _is_app_running():
        wrapper.log_warning("App not running, cannot warm send")
        return False
    return _send_intent(payload, warm_start=True, use_base64=use_base64)


def set_param(key, value, use_base64=True):
    return warm_send_json({key: value}, use_base64=use_base64)


def set_autoplay(enabled, playspeed=None):
    payload = {"autoplay": enabled}
    if playspeed is not None:
        payload["playSpeed"] = playspeed
    elif enabled:
        payload["playSpeed"] = 2
    else:
        payload["playSpeed"] = 1
    return warm_send_json(payload)


def set_combined(
    level=None,
    coin=None,
    booster=None,
    fakeads=None,
    autorotate=None,
    autoplay=None,
    playspeed=None,
    heart=None,
):
    payload = {}
    if level is not None:
        payload["level"] = level
    if coin is not None:
        payload["coin"] = coin
    if booster is not None:
        payload["booster"] = booster
    if fakeads is not None:
        payload["fakeads"] = fakeads
    if autorotate is not None:
        payload["autorotate"] = autorotate
    if autoplay is not None:
        payload["autoplay"] = autoplay
    if playspeed is not None:
        payload["playSpeed"] = playspeed
    if heart is not None:
        payload["heart"] = heart
    return warm_send_json(payload)


# ==================== SYSTEM HELPERS ====================
def set_system_time(datetime_str: str):
    subprocess.run(["adb", "shell", "settings", "put", "global", "auto_time", "0"])
    subprocess.run(["adb", "shell", "date", "-s", datetime_str], check=False)
    wrapper.log_info(f"System time set to {datetime_str}")


# =============== PROCESS & NETWORK CONTROL ==============
def is_adb_device_connected():
    try:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split("\n")
        return any("\tdevice" in line for line in lines[1:])
    except Exception:
        return False


def run_adb_command(cmd: list, timeout: int = 30) -> tuple:
    """
    run an ADB command and return (returncode, stdout, stderr)
    """
    try:
        proc = subprocess.run(
            ["adb"] + cmd, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        wrapper.log_error(f"ADB command timed out after {timeout}s: {' '.join(cmd)}")
        return -1, "", "Command timed out"
    except Exception as e:
        wrapper.log_error(f"ADB command failed: {e}")
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
        broadcast_cmd = [
            "shell",
            "am",
            "broadcast",
            "-a",
            "android.intent.action.AIRPLANE_MODE",
        ]
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
