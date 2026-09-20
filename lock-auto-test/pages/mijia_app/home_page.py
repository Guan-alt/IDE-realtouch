"""
米家App首页（设备列表）
"""

from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from pages.mijia_app.base_page import MijiaBasePage
from common.logger import Logger

logger = Logger.get_logger(__name__)


class MijiaHomePage(MijiaBasePage):
    """米家首页"""

    # ===== 元素定位器（需根据实际米家App调整） =====
    # 首页设备列表
    LOCATOR_DEVICE_LIST = (By.ID, "com.xiaomi.smarthome:id/recycler_view")
    # 设备名称（在列表项中）
    LOCATOR_DEVICE_NAME_TEXT = "请替换为实际的设备名称text"

    # 底部Tab
    LOCATOR_TAB_HOME = (By.ID, "com.xiaomi.smarthome:id/tab_home")

    def is_home_page(self) -> bool:
        """检查是否在首页"""
        # 先处理可能的弹窗
        self.handle_system_dialogs()
        return self.is_element_displayed(self.LOCATOR_TAB_HOME, timeout=5)

    def click_device_by_name(self, device_name: str) -> bool:
        """
        点击首页指定名称的设备，进入设备插件页

        Args:
            device_name: 设备名称

        Returns:
            是否找到并点击
        """
        logger.info(f"在米家首页查找设备: {device_name}")

        # 处理弹窗
        self.handle_system_dialogs()

        # 滚动查找设备
        if self.scroll_to_text(device_name, max_swipes=8):
            try:
                locator = (
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().text("{device_name}")'
                )
                self.click(locator)
                logger.info(f"已点击设备: {device_name}")
                return True
            except Exception as e:
                logger.warning(f"点击设备失败: {e}")

        logger.error(f"未在米家首页找到设备: {device_name}")
        return False

    def go_to_home_tab(self):
        """切换到首页Tab"""
        try:
            self.click(self.LOCATOR_TAB_HOME)
        except Exception as e:
            logger.warning(f"切换首页Tab失败: {e}")
