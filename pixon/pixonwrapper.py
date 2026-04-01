# pixon/pixonwrapper.py
import os
import re
import time
import functools
import subprocess
import cv2
import imutils
import numpy as np
from pathlib import Path
from typing import Union, Optional, Tuple, Any

from airtest.core.api import (
    G, connect_device, init_device, auto_setup, set_logdir,
    touch, swipe, sleep, wait, Template, snapshot, log,
    start_app, stop_app, pinch, ST
)
from airtest.aircv import crop_image
from airtest.report.report import LogToHtml


def logwrap(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


_ocr = None
_ocr_import_error = None

def _get_ocr():
    global _ocr, _ocr_import_error
    if _ocr is None and _ocr_import_error is None:
        try:
            from paddleocr import PaddleOCR
            _ocr = PaddleOCR(
                use_angle_cls=True, 
                lang="en", 
                use_gpu=False, 
                show_log=False,
                det_db_thresh=0.2,
                det_db_box_thresh=0.5,
                drop_score=0.4
            )
        except ImportError as e:
            _ocr_import_error = e
            print("WARNING: PaddleOCR not installed.")
        except Exception as e:
            _ocr_import_error = e
            print(f"WARNING: Failed to initialize PaddleOCR: {e}")
    return _ocr


def _get_screen_size():
    try:
        w = G.DEVICE.display_info['width']
        h = G.DEVICE.display_info['height']
        return w, h
    except Exception:
        return 720, 1280


@logwrap
def swipe_up():
    w, h = _get_screen_size()
    swipe((int(w * 0.8), int(h * 0.8)), vector=[0, -0.4], duration=0.5)
    sleep(0.1)

@logwrap
def swipe_down():
    w, h = _get_screen_size()
    swipe((int(w * 0.8), int(h * 0.2)), vector=[0, 0.4], duration=0.5)
    sleep(0.1)

@logwrap
def swipe_left(start=None):
    w, h = _get_screen_size()
    if start is None:
        start = (w // 2, h // 2)
    swipe(start, [-0.2, 0], duration=0.5)
    sleep(0.1)

@logwrap
def swipe_right(start=None):
    w, h = _get_screen_size()
    if start is None:
        start = (w // 2, h // 2)
    swipe(start, [0.2, 0], duration=0.5)
    sleep(0.1)

@logwrap
def swipe_from_to(start, end):
    swipe(start, end)
    sleep(1)


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
        local_screen = crop_image(screen, area)
        if local_screen is None or local_screen.size == 0:
            return None
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
def try_touch(img_or_pos, area=None):
    if isinstance(img_or_pos, Template):
        img_or_pos = default_img_setup(img_or_pos)
        coord = partial_search(img_or_pos, area=area)
    else:
        coord = img_or_pos
    if coord:
        touch(coord)
        return True
    log_error(f"Fail to touch at {img_or_pos}")
    return False

@logwrap
def smart_touch(template, timeout=10):
    pos = wait(template, timeout=timeout, interval=0.5, intervalfunc=None)
    if pos:
        touch(pos)
        return True
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
def restart_app(package_name):
    stop_app(package_name)
    sleep(1)
    start_app(package_name)

@logwrap
def launch_app_wait_load_done(package_name, splash_screen_icon):
    G.DEVICE.display_info['orientation'] = 0
    restart_app(package_name)
    sleep(10)
    log_dir = ST.LOG_DIR or "."
    logcat_proc, logcat_file = logcat_to_file(package_name, os.path.join(log_dir, "logcat.log"))
    try:
        if not wait_exists(splash_screen_icon, timeout=60, interval=1):
            raise RuntimeError("Game load too long — splash screen not found")
        if not wait_not_exists(splash_screen_icon, timeout=90, interval=1):
            raise RuntimeError("Game load too long — splash screen not disappearing")
    finally:
        if logcat_proc:
            logcat_proc.terminate()
            logcat_proc.wait(timeout=5)
        if logcat_file:
            logcat_file.close()


def get_screen() -> np.ndarray:
    return G.DEVICE.snapshot()


def find_all_text(img_array: np.ndarray) -> list:
    ocr_instance = _get_ocr()
    if ocr_instance is None:
        return []
    try:
        if img_array.ndim == 3 and img_array.shape[2] == 4:
            img = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
        else:
            img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized = imutils.resize(gray, width=gray.shape[1] * 2)
        _, processed = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        results = ocr_instance.ocr(processed, cls=True)
        
        if not results or results[0] is None:
            results = ocr_instance.ocr(img, cls=True)
            
        if not results or results[0] is None:
            return []

        return [line[1][0] for line in results[0] if line[1][1] >= 0.5]
    except Exception as e:
        print(f"PaddleOCR failed: {e}")
        return []

def is_text_present(text_value: str, area=None) -> bool:
    screen = G.DEVICE.snapshot()
    if area:
        screen = crop_image(screen, area)
        if screen is None or screen.size == 0:
            return False
    texts = find_all_text(screen)
    return any(text_value.lower() in t.lower() for t in texts)


def detect_level_badge(screen_bgr: np.ndarray):
    ranges = [
        (np.array([0, 0, 0]),    np.array([180, 80, 80])),
        (np.array([0, 0, 100]),  np.array([80, 80, 255])),
        (np.array([80, 0, 0]),   np.array([255, 80, 180])),
    ]
    best_bbox = None
    best_area = 0
    for lo, hi in ranges:
        mask = cv2.inRange(screen_bgr, lo, hi)                          # type: ignore[attr-defined]
        contours, _ = cv2.findContours(                                 # type: ignore[attr-defined]
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE            # type: ignore[attr-defined]
        )
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)                         # type: ignore[attr-defined]
            area = w * h
            if area > best_area and 20 < w < 200 and 10 < h < 80:
                best_area = area
                best_bbox = (x, y, w, h)
    return best_bbox

def read_level_from_badge(screen_bgr: np.ndarray, bbox):
    x, y, w, h = bbox
    pad = 4
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(screen_bgr.shape[1], x + w + pad)
    y2 = min(screen_bgr.shape[0], y + h + pad)
    crop_bgr = screen_bgr[y1:y2, x1:x2]
    crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)  # type: ignore[attr-defined]
    texts = find_all_text(crop_rgb)
    for t in texts:
        if 'level' in t.lower():
            m = re.search(r'\d+', t)
            if m:
                return int(m.group())
    for t in texts:
        m = re.search(r'\d+', t)
        if m:
            return int(m.group())
    return None


def retry(times=3, delay=0.5, exceptions=(Exception,), failure_values=(None,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    result = fn(*args, **kwargs)
                    if result not in failure_values: 
                        return result
                except exceptions:
                    if attempt == times:
                        raise
                time.sleep(delay)
            return failure_values[0]
        return wrapper
    return decorator


def default_img_setup(img):
    if isinstance(img, Template):
        img.rgb = True
        img.threshold = 0.55
        if not img.record_pos:
            img.record_pos = ()
        if not img.resolution:
            try:
                w = G.DEVICE.display_info['width']
                h = G.DEVICE.display_info['height']
                img.resolution = (w, h)
            except Exception:
                img.resolution = (720, 1280)
    return img


def log_info(msg, snapshot=True):
    log(msg, snapshot=snapshot)

def log_error(msg, snapshot=True):
    log(RuntimeError(msg), snapshot=snapshot)

def log_warning(msg, snapshot=False):
    log(f"WARNING: {msg}", snapshot=snapshot)


def logcat_to_file(package: str, output_file: Union[str, Path], clear=True) -> Tuple[Optional[subprocess.Popen], Optional[Any]]:
    from airtest.core.android.adb import ADB
    adb: ADB = G.DEVICE.adb
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if clear:
        try:
            adb.cmd("logcat -c")
        except Exception:
            pass
    pid_output = adb.cmd(f"shell pidof {package}").strip()
    if not pid_output:
        print(f"Warning: Package '{package}' not running. No logcat will be captured.")
        return None, None
    pids = pid_output.split()
    pid_args = [f"--pid={pid}" for pid in pids]
    cmd = [adb.adb_path] + ["-s", adb.serialno, "logcat"] + pid_args
    print(f"[logcat] writing to {output_file}")
    log_file = open(output_file, "w", encoding="utf-8")
    proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)
    return proc, log_file


def teststep(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        log_info(f"------Begin - {f.__name__}------")
        res = f(*args, **kwargs)
        log_info(f"------End - {f.__name__}------")
        return res
    return wrapper
