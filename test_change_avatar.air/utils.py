# -*- encoding=utf8 -*-
__author__ = "Sullivan"

from airtest.core.api import *
from airtest.aircv import *

import time

@logwrap
def wait_not_exists(img, timeout=30, interval=0.5, area=None):
    img = default_img_setup(img)
    start_time = time.time()
    if area:
        while partial_search(img, area):
            if time.time() - start_time > timeout:
                return False
            sleep(interval)
    else:
        while exists(img):
            if time.time() - start_time > timeout:
                return False
            sleep(interval)
    return True


@logwrap
def wait_exists(img, timeout=30, interval=0.1, area=None):
    img = default_img_setup(img)
    start_time = time.time()
    if area:
        result = partial_search(img, area)
        while not result:
            if time.time() - start_time > timeout:
                return False
            sleep(interval)
            result = partial_search(img, area)
        return result
    else:
        try:
            return wait(img, timeout, interval)
        except:
            return False
    return True

def default_img_setup(img):
    img.rgb = True
    img.threshold = 0.75
    img.target_pos = 5
    img.record_pos = ()
    img.resolution = ()
    img.scale_max = 800
    img.scale_step = 0.001
    return img

def partial_search(img, area):
    img = default_img_setup(img)
    screen = G.DEVICE.snapshot()
    local_screen = aircv.crop_image(screen, area)
    return img.match_in(local_screen)

@logwrap
def count_image(img):
    img = default_img_setup(img)
    result = find_all(img)
    if result:
        return len(result)
    return 0
             
@logwrap
def try_touch_and_wait(img, wait_time=2, area=None):
    img = default_img_setup(img)
    coord = wait_exists(img, 3, area)
    if coord:
        touch(coord)
        sleep(wait_time)
        return
    assert False, f"Fail to find {img}"
    
    
@logwrap
def restart_app(package_name):
    stop_app(package_name)
    start_app(package_name)


    
    
