"""
自研App页面对象基类
封装通用的页面操作方法
"""

import time
from typing import Optional, Tuple, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy

from common.config import Config
from common.logger import Logger
from common.utils import wait_for

logger = Logger.get_logger(__name__)


class BasePage:
    """页面基类"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait_timeout = Config.get("appium.element_wait_timeout", 15)

    # ============== 元素查找 ==============

    def find_element(self, locator: Tuple[str, str], timeout: Optional[float] = None):
        """
        查找单个元素

        Args:
            locator: 定位器，如 (By.ID, "com.example:id/btn_unlock")
            timeout: 超时时间，不传用默认值

        Returns:
            WebElement
        """
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def find_elements(self, locator: Tuple[str, str], timeout: Optional[float] = None):
        """
        查找多个元素

        Args:
            locator: 定位器
            timeout: 超时时间

        Returns:
            WebElement 列表
        """
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    def is_element_displayed(self, locator: Tuple[str, str], timeout: float = 3) -> bool:
        """
        检查元素是否显示

        Args:
            locator: 定位器
            timeout: 等待超时时间

        Returns:
            是否显示
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element is not None
        except Exception:
            return False

    # ============== 元素操作 ==============

    def click(self, locator: Tuple[str, str], timeout: Optional[float] = None):
        """点击元素"""
        element = self.find_element(locator, timeout)
        element.click()
        logger.debug(f"点击元素: {locator}")

    def input_text(self, locator: Tuple[str, str], text: str, timeout: Optional[float] = None):
        """输入文本"""
        element = self.find_element(locator, timeout)
        element.clear()
        element.send_keys(text)
        logger.debug(f"输入文本 '{text}' 到元素: {locator}")

    def get_text(self, locator: Tuple[str, str], timeout: Optional[float] = None) -> str:
        """获取元素文本"""
        element = self.find_element(locator, timeout)
        return element.text or ""

    # ============== 等待 ==============

    def wait_for_element(self, locator: Tuple[str, str], timeout: Optional[float] = None):
        """等待元素出现"""
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: Optional[float] = None):
        """等待元素可点击"""
        timeout = timeout or self.wait_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_text(self, locator: Tuple[str, str], text: str, timeout: float = 10) -> bool:
        """
        等待元素文本变为指定值

        Args:
            locator: 元素定位器
            text: 期望的文本
            timeout: 超时时间

        Returns:
            是否在超时前匹配
        """
        try:
            wait_for(
                lambda: text in self.get_text(locator),
                timeout=timeout,
                interval=0.5
            )
            return True
        except TimeoutError:
            return False

    # ============== 页面操作 ==============

    def go_back(self):
        """返回上一页"""
        self.driver.back()
        logger.debug("返回上一页")

    def swipe_up(self, duration: int = 500):
        """向上滑动"""
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.7)
        end_y = int(size["height"] * 0.3)
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        logger.debug("向上滑动")

    def swipe_down(self, duration: int = 500):
        """向下滑动"""
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = int(size["height"] * 0.3)
        end_y = int(size["height"] * 0.7)
        self.driver.swipe(start_x, start_y, start_x, end_y, duration)
        logger.debug("向下滑动")

    def scroll_to_text(self, text: str, max_swipes: int = 5) -> bool:
        """
        滚动到指定文字（使用 UiScrollable）

        Args:
            text: 要查找的文字
            max_swipes: 最大滑动次数

        Returns:
            是否找到
        """
        try:
            element = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true))'
                f'.scrollIntoView(new UiSelector().text("{text}"))'
            )
            return element is not None
        except Exception as e:
            logger.warning(f"滚动查找文本 '{text}' 失败: {e}")
            return False

    # ============== 断言辅助 ==============

    def assert_element_displayed(self, locator: Tuple[str, str], msg: str = ""):
        """断言元素显示"""
        assert self.is_element_displayed(locator), msg or f"元素未显示: {locator}"

    def assert_text_equals(self, locator: Tuple[str, str], expected: str, msg: str = ""):
        """断言元素文本等于期望值"""
        actual = self.get_text(locator)
        assert actual == expected, msg or f"文本不匹配: 期望 '{expected}', 实际 '{actual}'"

    def assert_text_contains(self, locator: Tuple[str, str], expected: str, msg: str = ""):
        """断言元素文本包含期望值"""
        actual = self.get_text(locator)
        assert expected in actual, msg or f"文本不包含: 期望包含 '{expected}', 实际 '{actual}'"
