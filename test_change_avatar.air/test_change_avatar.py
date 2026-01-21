# -*- encoding=utf8 -*-
__author__ = "Sullivan"
import logging
import random

from airtest.core.api import *
from airtest.aircv import *
from utils import *
from airtest.report.report import simple_report

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
    reload_app()
    go_home()
    verify_avatar(change_avatar(get_current_avatar()))
    simple_report(__file__)

@logwrap
def reload_app():
    restart_app("com.woodpuzzle.pin3d")
    if not wait_exists(splash_screen_icon, interval=1):
        assert False, "Game load too long!"
    if not wait_not_exists(splash_screen_icon, interval=1):
        assert False, "Game load too long!"

@logwrap
def go_home():
    if not wait_exists(home_play_button, 3):
        try_touch_and_wait(setting_icon)
        try_touch_and_wait(go_home_button)
        try_touch_and_wait(go_home_button)
        wait_exists(home_play_button, 5)
        
@logwrap
def get_current_avatar():
    screen = G.DEVICE.snapshot()
    for av in list_avatar:
        if av.match_in(screen):
            return av
        
    assert False, "Can't detect current avatar!"
        
@logwrap
def change_avatar(curent_avatar):
    try_touch_and_wait(curent_avatar)
    try_touch_and_wait(edit_button)
    list_avatar_filtered = [x for x in list_avatar if x != curent_avatar]
    new_avatar = random.choice(list_avatar_filtered)
    try_touch_and_wait(new_avatar)
    try_touch_and_wait(save_button)
    try_touch_and_wait(close_button)
    try_touch_and_wait(close_button)
    return new_avatar
    
@logwrap    
def verify_avatar(img):
    if not wait_exists(img, 5):
        print("Fail change avatar")
        return
    try_touch_and_wait(img)
    if not wait_exists(img, 5):
        print("Fail change avatar")
        return
    try_touch_and_wait(edit_button)

    if not wait_exists(img, 5, area=(425,343,656,567)):
        print("Fail change avatar")
    try_touch_and_wait(close_button)
    try_touch_and_wait(close_button)

main()






