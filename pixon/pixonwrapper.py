import __main__
import time
import functools
import json
import subprocess
from pathlib import Path

from airtest.core.api import *
from airtest.aircv import *
from airtest.report.report import *


# =========================
# Airtest wrapped utilities
# =========================

@logwrap
def wait_not_exists(img: Template, timeout=30, interval=0.5, area=None, snapshot=True):
    """
    Wait until an image is no longer found on screen.

    Args:
        img (Template): Image template to search for.
        timeout (int): Max wait time in seconds.
        interval (float): Sleep interval between checks.
        area (tuple): Optional crop area (x, y, w, h).
        snapshot (bool): Whether to take snapshot for report.

    Returns:
        bool: True if image disappears before timeout, False otherwise.
    """
    img = default_img_setup(img)
    start_time = time.time()
    while partial_search(img, area):
        if time.time() - start_time > timeout:
            return False
        sleep(interval)
    return True


@logwrap
def wait_exists(img: Template, timeout=30, interval=0.1, area=None, snapshot=True):
    """
    Wait until an image appears on screen.

    Args:
        img (Template): Image template to search for.
        timeout (int): Max wait time in seconds.
        interval (float): Sleep interval between checks.
        area (tuple): Optional crop area (x, y, w, h).
        snapshot (bool): Whether to take snapshot for report.

    Returns:
        MatchResult | False: Match result if found, otherwise False.
    """
    img = default_img_setup(img)
    start_time = time.time()
    result = partial_search(img, area)
    while not result:
        if time.time() - start_time > timeout:
            return False
        sleep(interval)
        result = partial_search(img, area)
    return result


@logwrap
def partial_search(img: Template, area=None):
    """
    Perform a partial image search on current screen.

    Args:
        img (Template): Image template to match.
        area (tuple): Optional crop area (x, y, w, h).

    Returns:
        MatchResult | None: Match result if found.
    """
    img = default_img_setup(img)
    screen = G.DEVICE.snapshot()
    if area:
        local_screen = aircv.crop_image(screen, area)
        return img.match_in(local_screen)
    return img.match_in(screen)


@logwrap
def try_touch_and_wait(img_or_pos, wait_time=2, area=None):
    """
    Try to touch a template or coordinate, then wait.

    Args:
        img_or_pos (Template | tuple): Image template or (x, y) position.
        wait_time (int): Time to wait after touch.
        area (tuple): Optional crop area.

    Returns:
        bool: True if touched successfully, False otherwise.
    """
    if isinstance(img_or_pos, Template):
        img_or_pos = default_img_setup(img_or_pos)
        coord = wait_exists(img_or_pos, 3, area=area)
    else:
        coord = img_or_pos
    if coord:
        touch(coord)
        sleep(wait_time)
        return True
    log_error(f"Fail to touch at {img_or_pos}")
    return False


@logwrap
def try_touch_and_hold(img_or_pos, hold_time=2, area=None):
    """
    Try to touch and hold a template or coordinate.

    Args:
        img_or_pos (Template | tuple): Image template or (x, y) position.
        hold_time (int): Hold duration in seconds.
        area (tuple): Optional crop area.

    Returns:
        bool: True if touched successfully, False otherwise.
    """
    if isinstance(img_or_pos, Template):
        img_or_pos = default_img_setup(img_or_pos)
        coord = wait_exists(img_or_pos, 3, area=area)
    else:
        coord = img_or_pos
    if coord:
        touch(coord, duration=hold_time)
        sleep(1)
        return True
    log_error(f"Fail to touch at {img_or_pos}")
    return False


@logwrap
def zoom_in(center=None):
    """
    Perform pinch-in gesture (zoom in).

    Args:
        center (tuple): Optional center point.
    """
    pinch("in", center)
    sleep(1)


@logwrap
def zoom_out(center=None):
    """
    Perform pinch-out gesture (zoom out).

    Args:
        center (tuple): Optional center point.
    """
    pinch("out", center)
    sleep(1)


@logwrap
def swipe_up(start=None):
    """
    Swipe upward from a start position.
    """
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, -1])
    sleep(1)


@logwrap
def swipe_down(start=None):
    """
    Swipe downward from a start position.
    """
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, 1])
    sleep(1)


@logwrap
def swipe_left(start=None):
    """
    Swipe left from a start position.
    """
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, -1])
    sleep(1)


@logwrap
def swipe_right(start=None):
    """
    Swipe right from a start position.
    """
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, 1])
    sleep(1)


@logwrap
def swipe_from_to(start, end):
    """
    Swipe from start position to end position.

    Args:
        start (tuple): Start coordinate.
        end (tuple): End coordinate.
    """
    swipe(start, end)
    sleep(1)


@logwrap
def restart_app(package_name):
    """
    Force-stop and relaunch an Android app.

    Args:
        package_name (str): App package name.
    """
    stop_app(package_name)
    sleep(3)
    start_app(package_name)


@logwrap
def launch_app_wait_load_done(package_name, splash_screen_icon):
    """
    Restart app, start logcat capture, and wait for splash screen to appear and disappear.

    Args:
        package_name (str): App package name.
        splash_screen_icon (Template): Splash screen image template.
    """
    restart_app(package_name)
    sleep(3)
    logcat_to_file(
        package_name, os.path.join(ST.LOG_DIR, f"logcat.log")
    )
    if not wait_exists(splash_screen_icon, interval=1):
        log_error("Game load too long!")
    if not wait_not_exists(splash_screen_icon, interval=1):
        log_error("Game load too long!")


# =========================
# Text recognition utilities
# =========================

def is_text_present(text_value, area=None):
    """
    Check if specific text exists on screen using OCR.

    Args:
        text_value (str): Text to search for.
        area (tuple): Optional crop area.

    Returns:
        bool: True if text is found, False otherwise.
    """
    screen = G.DEVICE.snapshot()
    if area:
        cropped = aircv.crop_image(screen, area)
        texts = find_all_text(cropped)
    else:
        texts = find_all_text(screen)
    return text_value in texts


def find_all_text(screen):
    """
    Extract all text from an image using Gemini Vision API.

    Args:
        screen (ndarray): Screenshot image.

    Returns:
        list[str]: List of detected text strings.
    """
    from google import genai
    import PIL.Image

    aircv.imwrite(r"screen.png", screen, ST.SNAPSHOT_QUALITY, max_size=ST.IMAGE_MAXSIZE)
    client = genai.Client(api_key="AIzaSyAwvEvWTnPjQI1GpHUG9y8gVGK2N1MEpkY")
    image = PIL.Image.open("screen.png")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                image,
                "Extract all the text from this image exactly as it appears."
                'Return the texts as plain json list `["text1", "text2", ...]`',
            ],
        )
        result_text = response.text.replace("`", "").replace("json", "").strip()
        arr = json.loads(result_text)
        return arr
    except Exception as e:
        print(e)


# =========================
# Image template defaults
# =========================

def default_img_setup(img):
    """
    Apply default matching parameters to an Airtest Template.

    Args:
        img (Template): Image template.

    Returns:
        Template: Modified template.
    """
    if isinstance(img, Template):
        img.rgb = True
        img.threshold = 0.7
        img.target_pos = 5
        img.record_pos = ()
        img.resolution = ()
        img.scale_max = 800
        img.scale_step = 0.001
    return img


# =========================
# Logging helpers
# =========================

def log_info(msg, snapshot=True):
    """
    Log informational message to Airtest report.
    """
    log(msg, snapshot=snapshot)


def log_error(msg, snapshot=True):
    """
    Log error message to Airtest report.
    """
    log(RuntimeError(msg), snapshot=snapshot)


# =========================
# Logcat capture
# =========================

def logcat_to_file(
    package: str,
    output_file: str | Path,
    clear=True,
):
    """
    Capture Android logcat output for a specific app process and write to file.

    Args:
        package (str): App package name.
        output_file (str | Path): Output log file path.
        clear (bool): Clear existing logcat buffer before capturing.
    """
    from airtest.core.android.adb import ADB

    adb: ADB = G.DEVICE.adb
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if clear:
        try:
            adb.cmd("logcat -c")
        except:
            pass

    pid_output = adb.cmd(f"shell pidof {package}").strip()
    if not pid_output:
        raise RuntimeError(f"Package '{package}' is not running")

    pids = pid_output.split()
    pid_args = [f"--pid={pid}" for pid in pids]

    cmd = [adb.adb_path] + ["-s", adb.serialno, "logcat"] + pid_args

    print(f"[logcat] writing directly to {output_file}")
    f = open(output_file, "w", encoding="utf-8")
    subprocess.Popen(
        cmd,
        stdout=f,
        stderr=subprocess.STDOUT,
    )


# =========================
# Test step decorator
# =========================

def teststep(f):
    """
    Decorator to wrap a test step with begin/end logs.

    Args:
        f (callable): Test function.

    Returns:
        callable: Wrapped function.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        log_info(f"------Begin - {f.__name__}------")
        res = f(*args, **kwargs)
        log_info(f"------End - {f.__name__}------")
        return res

    return wrapper
