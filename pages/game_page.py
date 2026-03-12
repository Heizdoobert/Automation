# pages/game_page.py
import re
import pixon.pixonwrapper as wrapper
from airtest.core.api import sleep

from common.base_page import BasePage
from .home_page import get_template


class GamePage(BasePage):
    booster = [
        get_template("extend_play/btn_booster_1.png", (-0.218, 0.744)),
        get_template("extend_play/btn_booster_2.png", (-0.01,  0.74 )),
    ]
    title_booster = [
        get_template("extend_play/title_booster_1.png", (0.007, -0.556)),
        get_template("extend_play/title_booster_2.png", (0.007, -0.554)),
    ]
    pay_coin = [
        get_template("extend_play/cost_booster_1.png", (0.172, 0.072)),
        get_template("extend_play/cost_booster_2.png", (0.171, 0.069)),
    ]

    @property
    def CENTER(self):
        w, h = self.get_screen_size()
        return (w // 2, h // 2)

    @property
    def LEVEL_AREA(self):
        w, h = self.get_screen_size()
        return (0, 0, w, int(120 * h / 1280))

    def get_current_level(self) -> int:
        def _on_retry(name, attempt, exc):
            msg = (
                f"get_current_level retry {attempt}: {exc}"
                if exc
                else f"get_current_level retry {attempt}: no result"
            )
            wrapper.log_info(msg)

        @wrapper.retry(times=3, delay=1.0, exceptions=(Exception,), on_retry=_on_retry)
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
        if result:
            wrapper.log_info(f"get_current_level: detected level {result}")
            return result

        wrapper.log_error("get_current_level: failed after all attempts, returning 0")
        return 0

    def activate_boosters(self) -> None:
        sleep(2)
        if self.wait_for_element(self.booster[0]):
            self.tap(self.booster[0])
            sleep(2)
            if self.wait_for_element(self.title_booster[0], timeout=3):
                wrapper.log_info("Booster 1 ran out — buying with coin")
                self.tap(self.pay_coin[0])
                sleep(3)
            else:
                wrapper.log_info("Booster 1 available — no need to buy")

        sleep(2)
        if self.wait_for_element(self.booster[1]):
            self.tap(self.booster[1])
            sleep(2)
            if self.wait_for_element(self.title_booster[1], timeout=3):
                wrapper.log_info("Booster 2 ran out — buying with coin")
                self.tap(self.pay_coin[1])
                sleep(3)
                self.tap(self.CENTER)
            else:
                wrapper.log_info("Booster 2 available — no need to buy")

    def use_booster(self, booster_type: str, count: int) -> None:
        wrapper.log_info(f"use_booster: type={booster_type}, count={count} — not implemented")

    def spend_coins(self, amount: int) -> None:
        wrapper.log_info(f"spend_coins: amount={amount} — not implemented")

    def collect_nails(self, color: str, count: int) -> None:
        wrapper.log_info(f"collect_nails: color={color}, count={count} — not implemented")
