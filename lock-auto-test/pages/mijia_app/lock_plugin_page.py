"""
米家App门锁插件页
实现 LockAppInterface 接口

注意：米家门锁插件可能是H5页面，需要切换到webview上下文操作
具体元素定位需要根据实际插件页面调整
"""

from selenium.webdriver.common.by import By

from pages.mijia_app.base_page import MijiaBasePage
from pages.base.lock_app_interface import LockAppInterface
from common.logger import Logger

logger = Logger.get_logger(__name__)


class MijiaLockPage(MijiaBasePage, LockAppInterface):
    """米家门锁插件页"""

    # ===== 元素定位器（需根据实际插件页面调整） =====
    # 状态文字
    LOCATOR_LOCK_STATUS = (By.ID, "tv_lock_status")
    # 操作按钮
    LOCATOR_ACTION_BUTTON = (By.ID, "btn_unlock")
    # 临时密码入口
    LOCATOR_TEMP_PASSWORD = (By.ID, "layout_temp_pwd")

    # 状态文本
    STATUS_LOCKED = "已锁定"
    STATUS_UNLOCKED = "已开锁"

    # 是否是H5页面（如果是，需要切换webview）
    IS_H5_PAGE = True

    def open_lock_detail(self, device_name: str) -> None:
        """实现接口：进入门锁详情页"""
        from pages.mijia_app.home_page import MijiaHomePage
        home = MijiaHomePage(self.driver)
        home.click_device_by_name(device_name)
        # 等待页面加载
        self.wait_for_page_load()

        # 如果是H5页面，切换到webview
        if self.IS_H5_PAGE:
            self.switch_to_webview()

    def go_back(self) -> None:
        """返回上一页"""
        # 如果在webview里，先切回原生再返回
        if self.IS_H5_PAGE:
            self.switch_to_native()
        super().go_back()

    def wait_for_page_load(self, timeout: float = 15) -> bool:
        """等待页面加载"""
        # 米家插件加载可能比较慢
        try:
            if self.IS_H5_PAGE:
                # H5页面需要切换webview后再等元素
                self.switch_to_webview()
                self.wait_for_element(self.LOCATOR_LOCK_STATUS, timeout=timeout)
                return True
            else:
                self.wait_for_element(self.LOCATOR_LOCK_STATUS, timeout=timeout)
                return True
        except Exception as e:
            logger.warning(f"等待页面加载超时: {e}")
            return False

    # ============== 状态查询 ==============

    def get_lock_status(self) -> str:
        """获取门锁状态"""
        try:
            status_text = self.get_text(self.LOCATOR_LOCK_STATUS)
            if self.STATUS_LOCKED in status_text:
                return "locked"
            elif self.STATUS_UNLOCKED in status_text:
                return "unlocked"
            else:
                logger.warning(f"未知状态: {status_text}")
                return "unknown"
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return "unknown"

    def is_lock_detail_displayed(self) -> bool:
        """检查是否在门锁详情页"""
        return self.is_element_displayed(self.LOCATOR_LOCK_STATUS, timeout=5)

    # ============== 操作相关 ==============

    def click_unlock(self) -> None:
        """点击开锁"""
        logger.info("米家App：点击开锁")
        self.click(self.LOCATOR_ACTION_BUTTON)

    def click_lock(self) -> None:
        """点击关锁"""
        logger.info("米家App：点击关锁")
        # 米家可能开锁和关锁是同一个按钮，根据状态切换
        self.click(self.LOCATOR_ACTION_BUTTON)

    # ============== UI 验证 ==============

    def is_unlock_button_displayed(self) -> bool:
        """检查开锁按钮是否显示"""
        return self.is_element_displayed(self.LOCATOR_ACTION_BUTTON, timeout=5)

    def is_lock_status_displayed(self) -> bool:
        """检查状态文字是否显示"""
        return self.is_element_displayed(self.LOCATOR_LOCK_STATUS, timeout=5)

    def get_action_button_text(self) -> str:
        """获取操作按钮文字"""
        try:
            return self.get_text(self.LOCATOR_ACTION_BUTTON)
        except Exception:
            return ""

    # ============== 等待 ==============

    def wait_for_status(self, status: str, timeout: float = 10) -> bool:
        """等待状态变化"""
        from common.utils import wait_for
        try:
            wait_for(
                lambda: self.get_lock_status() == status,
                timeout=timeout,
                interval=0.5
            )
            return True
        except TimeoutError:
            return False
