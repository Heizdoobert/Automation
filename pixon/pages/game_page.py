# pages/game_page.py
import re
import pixon.pixonwrapper as wrapper
from airtest.core.api import sleep
from pixon.common.base_page import BasePage
from .home_page import get_template


class GamePage(BasePage):
    booster = [
        get_template("extend_play/btn_booster_1.png", (-0.218,  0.744)),
        get_template("extend_play/btn_booster_2.png", (-0.01,   0.74 )),
        get_template("extend_play/btn_booster_3.png", ( 0.218,  0.744)),
    ]
    title_booster = [
        get_template("extend_play/title_booster_1.png", (0.007, -0.556)),
        get_template("extend_play/title_booster_2.png", (0.007, -0.554)),
        get_template("extend_play/title_booster_3.png", (0.007, -0.552)),
    ]
    pay_coin = [
        get_template("extend_play/cost_booster_1.png", (0.172, 0.072)),
        get_template("extend_play/cost_booster_2.png", (0.171, 0.069)),
        get_template("extend_play/cost_booster_3.png", (0.170, 0.066)),
    ]

    BOOSTER_INDEX = {
        "drill":  0,
        "hammer": 1,
        "magnet": 2,
    }

    @property
    def CENTER(self):
        w, h = self.get_screen_size()
        return (w // 2, h // 2)

    @property
    def LEVEL_AREA(self):
        w, h = self.get_screen_size()
        return (0, 0, w, int(120 * h / 1280))

    def get_current_level(self) -> int:
        @wrapper.retry(times=3, delay=1.0, exceptions=(Exception,))
        def _attempt():
            screen = wrapper.get_screen()
            x1, y1, x2, y2 = self.LEVEL_AREA
            crop = screen[y1:y2, x1:x2]
            texts = wrapper.find_all_text(crop)
            wrapper.log_info(f"get_current_level OCR texts: {texts}")
            for t in texts:
                m = re.search(r'(?:level|lv)[^\d]*(\d+)', t, re.IGNORECASE)
                if m:
                    return int(m.group(1))
                m2 = re.fullmatch(r'\d{1,4}', t.strip())
                if m2:
                    val = int(m2.group())
                    if 1 <= val <= 9999:
                        return val
            return None

        result = _attempt()
        if result is not None:
            wrapper.log_info(f"get_current_level: detected level {result}")
            return result
        raise RuntimeError("get_current_level: failed after all attempts, unable to detect level")

    def activate_boosters(self) -> None:
        for i in range(len(self.booster)):
            sleep(2)
            if self.wait_for_element(self.booster[i], timeout=3):
                self.tap(self.booster[i])
                sleep(2)
                if self.wait_for_element(self.title_booster[i], timeout=3):
                    wrapper.log_info(f"Booster {i+1} ran out — buying with coin")
                    self.tap(self.pay_coin[i])
                    sleep(3)
                    wrapper.log_info(f"Center coordinates: {self.CENTER}")
                    self.tap(self.CENTER)
                    sleep(2)
                else:
                    wrapper.log_info(f"Booster {i+1} available — no need to buy")
                    wrapper.log_info(f"Center coordinates: {self.CENTER}")
                    self.tap(self.CENTER)
                    sleep(2)
            else:
                wrapper.log_warning(f"Booster {i+1} not found on screen")

    def _activate_single_booster(self, index: int) -> None:
        sleep(2)
        if self.wait_for_element(self.booster[index], timeout=3):
            self.tap(self.booster[index])
            sleep(2)
            if self.wait_for_element(self.title_booster[index], timeout=3):
                wrapper.log_info(f"Booster {index+1} ran out — buying with coin")
                self.tap(self.pay_coin[index])
                sleep(3)
                self.tap(self.CENTER)
                sleep(2)
            else:
                wrapper.log_info(f"Booster {index+1} available — no need to buy")
                self.tap(self.CENTER)
                sleep(2)
        else:
            wrapper.log_warning(f"Booster {index+1} not found on screen")

    def use_booster(self, booster_type: str, count: int) -> None:
        if booster_type in ("", "any"):
            wrapper.log_info(f"use_booster: any type x{count} — activating all boosters {count} time(s)")
            for _ in range(count):
                self.activate_boosters()
            return
        index = self.BOOSTER_INDEX.get(booster_type)
        if index is None:
            wrapper.log_warning(f"use_booster: unknown booster type '{booster_type}'")
            return
        wrapper.log_info(f"use_booster: {booster_type} (index={index}) x{count}")
        for _ in range(count):
            self._activate_single_booster(index)

    def spend_coins(self, amount: int) -> None:
        wrapper.log_info(f"spend_coins: amount={amount} — not implemented")
        times = (amount + 99) // 100
        if times <= 0:
            times = 1
        wrapper.log_info(f"spend_coins: will activate boosters {times} time(s)")
        self.use_booster("any", times)

    def collect_nails(self, color: str, count: int) -> None:
        wrapper.log_info(f"collect_nails: color={color}, count={count} — not implemented")
