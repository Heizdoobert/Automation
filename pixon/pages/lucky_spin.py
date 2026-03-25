# pages/lucky_spin.py
from pixon.common.base_page import BasePage
from .home_page import get_template, HomePage
from airtest.core.api import touch, sleep, keyevent, text
import pixon.pixonwrapper as wrapper

class LuckySpinPage(BasePage):
    btn_spin = get_template("lucky_spin/btn_spin.png", (-0.001, 0.528))
    label_lucky_spin = get_template("lucky_spin/label_lucky_spin.png", (0.004, -0.644))      

    def roll_out(self) -> None:
        home = HomePage()
        home.tap(home.btn_lucky_spin)
        self.spin()
        sleep(4)
        home.tap(home.btn_close)

    def spin(self) -> None:
        self.tap(self.btn_spin)
        sleep(2)