"""
自研App门锁详情页
实现 LockAppInterface 接口
"""

from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from pages.self_app.base_page import BasePage
from pages.base.lock_app_interface import LockAppInterface
from common.logger import Logger

logger = Logger.get_logger(__name__)


class LockDetailPage(BasePage, LockAppInterface):
    """门锁详情页"""

    # ===== 元素定位器（请根据实际App替换） =====

    # 页面标题
    LOCATOR_PAGE_TITLE = (By.ID, "com.yourcompany.smartlock:id/tv_title")
    # 门锁状态文字（如"已锁定"/"已开锁"）
    LOCATOR_LOCK_STATUS = (By.ID, "com.yourcompany.smartlock:id/tv_lock_status")
    # 门锁图标（用于状态视觉确认）
    LOCATOR_LOCK_ICON = (By.ID, "com.yourcompany.smartlock:id/iv_lock_icon")
    # 主操作按钮（开锁/关锁）
    LOCATOR_ACTION_BUTTON = (By.ID, "com.yourcompany.smartlock:id/btn_action")
    # 临时密码入口
    LOCATOR_TEMP_PASSWORD_ENTRY = (By.ID, "com.yourcompany.smartlock:id/layout_temp_password")
    # 直播入口
    LOCATOR_LIVE_ENTRY = (By.ID, "com.yourcompany.smartlock:id/layout_live")
    # 电量显示
    LOCATOR_BATTERY = (By.ID, "com.yourcompany.smartlock:id/tv_battery")
    # 加载中状态
    LOCATOR_LOADING = (By.ID, "com.yourcompany.smartlock:id/progress_loading")

    # 状态文本常量
    STATUS_LOCKED = "已锁定"
    STATUS_UNLOCKED = "已开锁"
    STATUS_UNKNOWN = "unknown"

    # ============== 导航相关 ==============

    def open(self, device_name: str):
        """
        从首页进入门锁详情页
        （这个方法会自动导航，所以需要首页的引用，这里简化处理）
        """
        from pages.self_app.home_page import HomePage
        home = HomePage(self.driver)
        home.click_device_by_name(device_name)
        self.wait_for_page_load()

    def open_lock_detail(self, device_name: str) -> None:
        """实现接口方法：进入门锁详情页"""
        self.open(device_name)

    def go_back(self) -> None:
        """返回上一页"""
        super().go_back()

    # ============== 页面加载 ==============

    def wait_for_page_load(self, timeout: float = 10) -> bool:
        """等待页面加载完成"""
        try:
            self.wait_for_element(self.LOCATOR_LOCK_STATUS, timeout=timeout)
            # 等待loading消失
            if self.is_element_displayed(self.LOCATOR_LOADING, timeout=2):
                self.wait_for_element_disappear(self.LOCATOR_LOADING, timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element_disappear(self, locator, timeout: float = 10):
        """等待元素消失"""
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(self.driver, timeout).until(
            lambda d: not self.is_element_displayed(locator, timeout=1)
        )

    # ============== 状态查询 ==============

    def get_lock_status(self) -> str:
        """
        获取门锁当前状态

        Returns:
            "locked" / "unlocked" / "unknown"
        """
        try:
            status_text = self.get_text(self.LOCATOR_LOCK_STATUS)
            if self.STATUS_LOCKED in status_text:
                return "locked"
            elif self.STATUS_UNLOCKED in status_text:
                return "unlocked"
            else:
                logger.warning(f"未知的门锁状态: {status_text}")
                return "unknown"
        except Exception as e:
            logger.error(f"获取门锁状态失败: {e}")
            return "unknown"

    def is_lock_detail_displayed(self) -> bool:
        """检查是否在门锁详情页"""
        return self.is_element_displayed(self.LOCATOR_LOCK_STATUS, timeout=5)

    # ============== 操作相关 ==============

    def click_unlock(self) -> None:
        """点击开锁按钮"""
        logger.info("点击开锁按钮")
        current_status = self.get_lock_status()
        if current_status == "unlocked":
            logger.warning("门锁已经是开锁状态")
            return
        self.click(self.LOCATOR_ACTION_BUTTON)

    def click_lock(self) -> None:
        """点击关锁按钮"""
        logger.info("点击关锁按钮")
        current_status = self.get_lock_status()
        if current_status == "locked":
            logger.warning("门锁已经是锁定状态")
            return
        self.click(self.LOCATOR_ACTION_BUTTON)

    # ============== UI 元素验证 ==============

    def is_unlock_button_displayed(self) -> bool:
        """检查开锁按钮是否显示"""
        return self.is_element_displayed(self.LOCATOR_ACTION_BUTTON, timeout=5)

    def is_lock_status_displayed(self) -> bool:
        """检查状态文字是否显示"""
        return self.is_element_displayed(self.LOCATOR_LOCK_STATUS, timeout=5)

    def get_action_button_text(self) -> str:
        """获取操作按钮的文字"""
        try:
            return self.get_text(self.LOCATOR_ACTION_BUTTON)
        except Exception as e:
            logger.error(f"获取按钮文字失败: {e}")
            return ""

    def is_temp_password_entry_displayed(self) -> bool:
        """检查临时密码入口是否显示"""
        return self.is_element_displayed(self.LOCATOR_TEMP_PASSWORD_ENTRY, timeout=5)

    def is_live_entry_displayed(self) -> bool:
        """检查直播入口是否显示"""
        return self.is_element_displayed(self.LOCATOR_LIVE_ENTRY, timeout=5)

    def get_battery_text(self) -> str:
        """获取电量显示文本"""
        try:
            return self.get_text(self.LOCATOR_BATTERY)
        except Exception:
            return ""

    # ============== 等待相关 ==============

    def wait_for_status(self, status: str, timeout: float = 10) -> bool:
        """
        等待门锁状态变为指定值

        Args:
            status: 期望的状态 ("locked" / "unlocked")
            timeout: 超时时间

        Returns:
            是否在超时前变为指定状态
        """
        from common.utils import wait_for

        try:
            wait_for(
                lambda: self.get_lock_status() == status,
                timeout=timeout,
                interval=0.5
            )
            logger.info(f"门锁状态已变为: {status}")
            return True
        except TimeoutError:
            actual = self.get_lock_status()
            logger.warning(f"等待状态超时，期望: {status}, 实际: {actual}")
            return False

    # ============== 临时密码 ==============

    def open_temp_password_page(self):
        """进入临时密码页面"""
        self.click(self.LOCATOR_TEMP_PASSWORD_ENTRY)
