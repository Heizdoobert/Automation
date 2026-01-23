# -*- encoding=utf8 -*-
__author__ = "Sullivan"
import logging
import random
import string
import sys

from airtest.core.api import *
from airtest.aircv import *
from airtest.report.report import *
from pathlib import *

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pixonwrapper import *

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

auto_setup(__file__, )

splash_screen_icon = Template(r"splash_icon.png")
home_play_button = Template(r"tpl1768970459486.png")
setting_icon = Template(r"tpl1768972090195.png")
go_home_button = Template(r"tpl1768970707289.png")
close_button = Template(r"tpl1768971072303.png")
save_button = Template(r"tpl1768984965560.png")
continue_button = Template(r"tpl1769067579970.png")
edit_button = Template(r"tpl1768984937403.png")
profile_corner = Template(r"tpl1769067360216.png")
name_corner = Template(r"tpl1769067500585.png")


def main():
    try:
        connect_device(r"android://127.0.0.1:5037/emulator-5554")
        launch_app_wait_load_done("com.woodpuzzle.pin3d", splash_screen_icon)
        go_home()
        
        name = change_name()
        check_name(name)
        # export_log(__file__, r"C:\Users\Sullivan\Documents\AirTestProjects\Reports")
    except:    
        pass
    finally:
        pass
        # stop_app("com.woodpuzzle.pin3d")

@teststep
def go_home():
    if not wait_exists(home_play_button, 3):
        try_touch_and_wait(setting_icon)
        try_touch_and_wait(go_home_button)
        try_touch_and_wait(go_home_button)
        wait_exists(home_play_button, 5)
        
def random_string(max_len=11):
    length = random.randint(5, max_len)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@teststep        
def change_name():
    name = random_string()
    try_touch_and_wait(profile_corner)
    try_touch_and_wait(edit_button)
    try_touch_and_wait(edit_button)
    try_touch_and_wait(name_corner)
    text(name)
    try_touch_and_wait(continue_button)
    return name

@teststep
def check_name(name):
    if not is_text_present(name, (335,421,738,526)):
        print("Change name verify fail!")
        log_error("Change name verify fail!")
    else:
        print("Change name verify success!")
    # try_touch_and_wait(profile_corner)
    # try_touch_and_wait(edit_button)
    # try_touch_and_wait(edit_button)
    # try_touch_and_wait(name_corner)
    # keyevent("KEYCODE_COPY")
    # sleep(1)
    # text = get_clipboard()
    # if name != text:
    #     log_error("Change name verify fail!")
    
main()
