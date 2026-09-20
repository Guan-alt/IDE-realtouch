"""
米家App页面基类
"""

from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from pages.self_app.base_page import BasePage
from common.logger import Logger

logger = Logger.get_logger(__name__)


class MijiaBasePage(BasePage):
    """米家App页面基类"""

    # 米家通用的弹窗处理
    LOCATOR_PERMISSION_ALLOW = (By.ID, "com.xiaomi.smarthome:id/btn_positive")
    LOCATOR_UPDATE_CANCEL = (By.ID, "com.xiaomi.smarthome:id/btn_negative")
    LOCATOR_AD_CLOSE = (By.ID, "com.xiaomi.smarthome:id/iv_close")

    def handle_system_dialogs(self):
        """
        处理各种可能出现的系统弹窗
        包括：权限申请、更新提示、广告等
        """
        # 依次尝试处理各种弹窗
        dialog_handlers = [
            (self.LOCATOR_PERMISSION_ALLOW, "权限申请-允许"),
            (self.LOCATOR_UPDATE_CANCEL, "更新提示-取消"),
            (self.LOCATOR_AD_CLOSE, "广告弹窗-关闭"),
        ]

        for locator, name in dialog_handlers:
            try:
                if self.is_element_displayed(locator, timeout=2):
                    self.click(locator)
                    logger.info(f"已处理弹窗: {name}")
            except Exception:
                pass

    def switch_to_webview(self, webview_name: str = None) -> bool:
        """
        切换到 webview 上下文（米家插件很多是H5页面）

        Args:
            webview_name: webview名称，不传则切到第一个webview

        Returns:
            是否切换成功
        """
        contexts = self.driver.contexts
        logger.info(f"可用上下文: {contexts}")

        for ctx in contexts:
            if "WEBVIEW" in ctx:
                if webview_name is None or webview_name in ctx:
                    self.driver.switch_to.context(ctx)
                    logger.info(f"已切换到 webview: {ctx}")
                    return True

        logger.warning("未找到 webview 上下文")
        return False

    def switch_to_native(self):
        """切回原生上下文"""
        self.driver.switch_to.context("NATIVE_APP")
        logger.info("已切换到原生上下文")
