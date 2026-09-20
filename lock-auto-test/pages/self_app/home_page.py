"""
自研App首页（设备列表页）
"""

from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from pages.self_app.base_page import BasePage
from common.logger import Logger

logger = Logger.get_logger(__name__)


class HomePage(BasePage):
    """首页 - 设备列表"""

    # 元素定位器
    # 注意：实际项目中请替换为真实的元素ID
    LOCATOR_TITLE = (By.ID, "com.yourcompany.smartlock:id/tv_title")
    LOCATOR_DEVICE_LIST = (By.ID, "com.yourcompany.smartlock:id/recycler_devices")
    LOCATOR_DEVICE_NAME = (By.ID, "com.yourcompany.smartlock:id/tv_device_name")
    LOCATOR_DEVICE_STATUS = (By.ID, "com.yourcompany.smartlock:id/tv_device_status")

    def is_home_page(self) -> bool:
        """检查是否在首页"""
        return self.is_element_displayed(self.LOCATOR_TITLE, timeout=5)

    def get_device_count(self) -> int:
        """获取设备列表中的设备数量"""
        try:
            elements = self.find_elements(self.LOCATOR_DEVICE_NAME, timeout=5)
            return len(elements)
        except Exception:
            return 0

    def click_device_by_name(self, device_name: str) -> bool:
        """
        点击指定名称的设备进入详情页

        Args:
            device_name: 设备名称

        Returns:
            是否找到并点击
        """
        logger.info(f"点击设备: {device_name}")

        # 先尝试直接找
        try:
            locator = (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().text("{device_name}")'
            )
            self.click(locator)
            return True
        except Exception:
            pass

        # 找不到就滚动查找
        if self.scroll_to_text(device_name):
            try:
                locator = (
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    f'new UiSelector().text("{device_name}")'
                )
                self.click(locator)
                return True
            except Exception as e:
                logger.warning(f"点击设备失败: {e}")

        logger.error(f"未找到设备: {device_name}")
        return False

    def get_device_status(self, device_name: str) -> str:
        """
        获取指定设备的在线状态（首页列表上显示的状态）

        Args:
            device_name: 设备名称

        Returns:
            状态文本，找不到返回空字符串
        """
        # 注意：实际实现需要根据列表项的层级关系来定位
        # 这里提供一个简化的思路，具体根据实际UI调整
        try:
            # 滚动到设备
            self.scroll_to_text(device_name)
            # 找到对应的状态元素（根据实际布局调整）
            # 这里简化处理，实际需要根据具体UI层级来定位
            return ""
        except Exception as e:
            logger.warning(f"获取设备状态失败: {e}")
            return ""
