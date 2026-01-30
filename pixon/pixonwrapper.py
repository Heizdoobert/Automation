import __main__
import time
import functools
import json
import subprocess
from pathlib import Path

from airtest.core.api import *
from airtest.aircv import *
from airtest.report.report import *


# wrapped functions from airtest
@logwrap
def wait_not_exists(img: Template, timeout=30, interval=0.5, area=None, snapshot=True):
    img = default_img_setup(img)
    start_time = time.time()
    while partial_search(img, area):
        if time.time() - start_time > timeout:
            return False
        sleep(interval)
    return True


@logwrap
def wait_exists(img: Template, timeout=30, interval=0.1, area=None, snapshot=True):
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
    img = default_img_setup(img)
    screen = G.DEVICE.snapshot()
    if area:
        local_screen = aircv.crop_image(screen, area)
        return img.match_in(local_screen)
    return img.match_in(screen)


@logwrap
def try_touch_and_wait(img_or_pos, wait_time=2, area=None):
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
    pinch("in", center)
    sleep(1)


@logwrap
def zoom_out(center=None):
    pinch("out", center)
    sleep(1)


@logwrap
def swipe_up(start=None):
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, -1])
    sleep(1)


@logwrap
def swipe_down(start=None):
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, 1])
    sleep(1)


@logwrap
def swipe_left(start=None):
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, -1])
    sleep(1)


@logwrap
def swipe_right(start=None):
    if not start:
        start = (0.5, 0.5)
    swipe(start, [0, 1])
    sleep(1)


@logwrap
def swipe_from_to(start, end):
    swipe(start, end)
    sleep(1)


@logwrap
def restart_app(package_name):
    stop_app(package_name)
    sleep(3)
    start_app(package_name)


@logwrap
def launch_app_wait_load_done(package_name, splash_screen_icon):
    restart_app(package_name)
    sleep(3)
    logcat_to_file(
        package_name, os.path.join(ST.LOG_DIR, f"logcat.log")
    )
    if not wait_exists(splash_screen_icon, interval=1):
        log_error("Game load too long!")
    if not wait_not_exists(splash_screen_icon, interval=1):
        log_error("Game load too long!")


# utilites for text recognition
def is_text_present(text_value, area=None):
    screen = G.DEVICE.snapshot()
    if area:
        cropped = aircv.crop_image(screen, area)
        texts = find_all_text(cropped)
    else:
        texts = find_all_text(screen)
    return text_value in texts


def find_all_text(screen):
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


def default_img_setup(img):
    if isinstance(img, Template):
        img.rgb = True
        img.threshold = 0.7
        img.target_pos = 5
        img.record_pos = ()
        img.resolution = ()
        img.scale_max = 800
        img.scale_step = 0.001
    return img


def log_info(msg, snapshot=True):
    log(msg, snapshot=snapshot)


def log_error(msg, snapshot=True):
    log(RuntimeError(msg), snapshot=snapshot)


def logcat_to_file(
    package: str,
    output_file: str | Path,
    clear=True,
):
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


def teststep(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        log_info(f"------Begin - {f.__name__}------")
        res = f(*args, **kwargs)
        log_info(f"------End - {f.__name__}------")
        return res

    return wrapper
