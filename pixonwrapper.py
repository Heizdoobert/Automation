import time
import functools

from pathlib import Path
from airtest.core.api import *
from airtest.aircv import *
from airtest.report.report import *

@logwrap
def wait_not_exists(img, timeout=30, interval=0.5, area=None, snapshot=True):
    img = default_img_setup(img)
    start_time = time.time()
    while partial_search(img, area):
        if time.time() - start_time > timeout:
            return False
        sleep(interval)
    return True

@logwrap
def wait_exists(img, timeout=30, interval=0.1, area=None, snapshot=True):
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
def partial_search(img, area=None):
    img = default_img_setup(img)
    local_screen = screen = G.DEVICE.snapshot()
    if area:
        local_screen = aircv.crop_image(screen, area)
    return img.match_in(local_screen)

@logwrap
def try_touch_and_wait(img_or_pos, wait_time=2, area=None):
    img_or_pos = default_img_setup(img_or_pos)
    coord = wait_exists(img_or_pos, 3, area=area)
    if coord:
        touch(coord)
        sleep(wait_time)
        return True
    return False

@logwrap
def try_touch_and_hold(img_or_pos, hold_time=2, area=None):
    img_or_pos = default_img_setup(img_or_pos)
    coord = wait_exists(img_or_pos, 3, area=area)
    if coord:
        touch(coord, duration=hold_time)
        sleep(1)
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
    if not wait_exists(splash_screen_icon, interval=1):
        assert False, "Game load too long!"
    if not wait_not_exists(splash_screen_icon, interval=1):
        assert False, "Game load too long!"
        
        
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
    log(msg, snapshot)
    
def log_error(msg, snapshot=True):
    log(RuntimeError(msg), snapshot)

def teststep(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        log_info(f"------{f.__name__} Begin------")
        res = f(*args, **kwargs)
        log_info(f"------{f.__name__} End------")
        return res
    return wrapper

    
    

