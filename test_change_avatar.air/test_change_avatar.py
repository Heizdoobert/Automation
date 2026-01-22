# -*- encoding=utf8 -*-
__author__ = "Sullivan"
import logging
import random
import sys

from airtest.core.api import *
from airtest.aircv import *
from airtest.report.report import *
from pathlib import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pixonwrapper import *

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

auto_setup(__file__)


splash_screen_icon = Template(r"splash_icon.png")
home_play_button = Template(r"tpl1768970459486.png")
setting_icon = Template(r"tpl1768972090195.png")
go_home_button = Template(r"tpl1768970707289.png")
close_button = Template(r"tpl1768971072303.png")
save_button = Template(r"tpl1768984965560.png")
edit_button = Template(r"tpl1768984937403.png")
tick_v = Template(r"tpl1768985013457.png")
list_avatar = [Template(r"tpl1768980343481.png"),Template(r"tpl1768980349036.png"),Template(r"tpl1768980353866.png"),Template(r"tpl1768980359741.png"),Template(r"tpl1768980365190.png"),Template(r"tpl1768980369829.png"),Template(r"tpl1768980375081.png"),Template(r"tpl1768980379672.png"),Template(r"tpl1768980385058.png")]

def main():
    launch_app_wait_load_done("com.woodpuzzle.pin3d", splash_screen_icon)
    go_home()
    avatar = get_current_avatar()
    new_avatar = change_avatar(avatar)
    verify_avatar(new_avatar)

@teststep
def go_home():
    if not wait_exists(home_play_button, 3):
        try_touch_and_wait(setting_icon)
        try_touch_and_wait(go_home_button)
        try_touch_and_wait(go_home_button)
        wait_exists(home_play_button, 5)
        
@teststep        
def get_current_avatar():
    screen = G.DEVICE.snapshot()
    local_screen = aircv.crop_image(screen, (0,0,200,200))
    for av in list_avatar:
        if av.match_in(local_screen):
            print(f"Current avatar: {av}")
            return av
        
    assert False, "Can't detect current avatar!"

@teststep     
def change_avatar(curent_avatar):
    list_avatar_filtered = [x for x in list_avatar if x != curent_avatar]
    new_avatar = random.choice(list_avatar_filtered)
    
    try_touch_and_wait(curent_avatar)
    try_touch_and_wait(edit_button)
    try_touch_and_wait(new_avatar)
    try_touch_and_wait(save_button)
    try_touch_and_wait(close_button)
    try_touch_and_wait(close_button)
    return new_avatar

@teststep 
def verify_avatar(img):
    if not wait_exists(img, 5):
        log_error("Verify avatar fail in home screen")
    
    try_touch_and_wait(img)
    if not wait_exists(img, 5):
        log_error("Verify avatar fail in profile screen")
    
    try_touch_and_wait(edit_button)
    if not wait_exists(img, 5, area=(400,320,660,580)):
        log_error("Verify avatar fail in profile editing screen")
        
    try_touch_and_wait(close_button)
    try_touch_and_wait(close_button)

main()






