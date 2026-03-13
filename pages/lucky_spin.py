# pages/lucky_spin.py
from common.base_page import BasePage
from pathlib import Path
from airtest.core.api import Template, sleep
import pixon.pixonwrapper as wrapper

IMAGE_DIR = Path(__file__).resolve().parent / "images"

def get_template(relative_path, record_pos, resolution=(720, 1280)):
    return Template(str(IMAGE_DIR / relative_path), record_pos=record_pos, resolution=resolution)


class LuckySpinPage(BasePage):


    def open_spin(self):
        return
    def spin(self):
        return