# pages/remove_ads.py
from common.base_page import BasePage
from .home_page import get_template
from airtest.core.api import sleep
import pixon.pixonwrapper as wrapper


class RemoveAds(BasePage):
    btn_fake_ads_off = get_template("cheat/console/ads/btn_fake_ads_off.png", (-0.25, 0.41))
    btn_fake_ads_on  = get_template("cheat/console/ads/btn_fake_ads_on.png",  (-0.256, 0.407))

    def _scroll_to_ads_section(self) -> int:
        scrolls = 0
        for _ in range(20):
            if (wrapper.wait_exists(self.btn_fake_ads_off, timeout=1)
                    or wrapper.wait_exists(self.btn_fake_ads_on, timeout=1)):
                return scrolls
            self.swipe("up")
            sleep(1)
            scrolls += 1
        raise Exception("Ads section not found after 20 scrolls")

    def _scroll_back(self, scrolls: int) -> None:
        for _ in range(scrolls):
            self.swipe("down")
            sleep(0.5)

    def fake_ads_on(self) -> bool:
        scrolls = self._scroll_to_ads_section()

        already_on  = wrapper.wait_exists(self.btn_fake_ads_on,  timeout=1)
        needs_tap   = wrapper.wait_exists(self.btn_fake_ads_off, timeout=1)

        if already_on and not needs_tap:
            wrapper.log_info("fake_ads_on: already ON — skipping tap")
        elif needs_tap:
            self.tap(self.btn_fake_ads_off)
            sleep(1)
            if not wrapper.wait_exists(self.btn_fake_ads_on, timeout=3):
                wrapper.log_error("fake_ads_on: checkbox did not switch to ON state")
                self._scroll_back(scrolls)
                return False
            wrapper.log_info("fake_ads_on: confirmed ON ✓")
        else:
            wrapper.log_error("fake_ads_on: neither ON nor OFF button found after scroll")
            self._scroll_back(scrolls)
            return False

        self._scroll_back(scrolls)
        return True

    def fake_ads_off(self) -> bool:
        scrolls = self._scroll_to_ads_section()

        already_off = wrapper.wait_exists(self.btn_fake_ads_off, timeout=1)
        needs_tap   = wrapper.wait_exists(self.btn_fake_ads_on,  timeout=1)

        if already_off and not needs_tap:
            wrapper.log_info("fake_ads_off: already OFF — skipping tap")
        elif needs_tap:
            self.tap(self.btn_fake_ads_on)
            sleep(1)
            if not wrapper.wait_exists(self.btn_fake_ads_off, timeout=3):
                wrapper.log_error("fake_ads_off: checkbox did not switch to OFF state")
                self._scroll_back(scrolls)
                return False
            wrapper.log_info("fake_ads_off: confirmed OFF ✓")
        else:
            wrapper.log_error("fake_ads_off: neither ON nor OFF button found after scroll")
            self._scroll_back(scrolls)
            return False

        self._scroll_back(scrolls)
        return True
