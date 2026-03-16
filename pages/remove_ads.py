# pages/remove_ads.py
from common.base_page import BasePage
from .home_page import get_template
from airtest.core.api import sleep
import pixon.pixonwrapper as wrapper


class RemoveAds(BasePage):
    btn_fake_ads_off = get_template("cheat/console/ads/btn_fake_ads_off.png", (-0.25,  0.41 ))
    btn_fake_ads_on  = get_template("cheat/console/ads/btn_fake_ads_on.png",  (-0.256, 0.407))

    def fake_ads_on(self):
        for _ in range(10):
            self.swipe("up")
            sleep(0.3)
        self.tap(self.btn_fake_ads_off)
        wrapper.log_info("Fake Ads ON")
        for _ in range(10):
            self.swipe("down")
            sleep(0.3)
