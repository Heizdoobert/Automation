from common.base_page import BasePage
from .home_page import get_template
from airtest.core.api import sleep
import pixon.pixonwrapper as wrapper


class RemoveAds(BasePage):
    btn_fake_ads_off = get_template("cheat/console/ads/btn_fake_ads_off.png", (-0.25, 0.41))
    btn_fake_ads_on = get_template("cheat/console/ads/btn_fake_ads_on.png", (-0.256, 0.407))

    def _scroll_to_ads_section(self):
        for _ in range(10):
            self.swipe("up")
            sleep(0.5)

    def _scroll_back(self):
        for _ in range(10):
            self.swipe("down")
            sleep(0.5)

    def fake_ads_on(self):
        self._scroll_to_ads_section()
        if wrapper.wait_exists(self.btn_fake_ads_off, timeout=1):
            self.tap(self.btn_fake_ads_off)
            sleep(1)
            wrapper.log_info("Fake Ads ON")
        self._scroll_back()
        return True

    def fake_ads_off(self):
        self._scroll_to_ads_section()
        if wrapper.wait_exists(self.btn_fake_ads_on, timeout=1):
            self.tap(self.btn_fake_ads_on)
            sleep(1)
            wrapper.log_info("Fake Ads OFF")
        self._scroll_back()
        return True