"""
Appium Driver 封装
统一管理 Appium driver 的创建、连接、销毁
"""

from typing import Optional, Dict, Any

from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By

from common.config import Config
from common.logger import Logger

logger = Logger.get_logger(__name__)


class AppiumDriver:
    """Appium Driver 管理器"""

    def __init__(self, app_type: str = "self_app"):
        """
        初始化 Appium Driver

        Args:
            app_type: 应用类型，'self_app' 或 'mijia_app'
        """
        self.app_type = app_type
        self.driver: Optional[WebDriver] = None

    def create_driver(self, device_name: Optional[str] = None) -> WebDriver:
        """
        创建 Appium driver 并连接设备

        Args:
            device_name: 设备序列号，不传则从配置读取

        Returns:
            Appium WebDriver 实例
        """
        host = Config.get("appium.host", "127.0.0.1")
        port = Config.get("appium.port", 4723)
        server_url = f"http://{host}:{port}"

        caps = self._build_capabilities(device_name)

        logger.info(f"正在连接 Appium 服务: {server_url}")
        logger.info(f"应用类型: {self.app_type}")
        logger.debug(f"Desired Capabilities: {caps}")

        try:
            self.driver = webdriver.Remote(server_url, caps)
            # 设置隐式等待
            implicit_wait = Config.get("appium.implicit_wait", 10)
            self.driver.implicitly_wait(implicit_wait)
            logger.info("Appium driver 创建成功")
            return self.driver
        except Exception as e:
            logger.error(f"Appium driver 创建失败: {e}")
            raise

    def _build_capabilities(self, device_name: Optional[str] = None) -> Dict[str, Any]:
        """构建 desired capabilities"""
        android_config = Config.get("android", {})
        app_config = Config.get(self.app_type, {})

        caps = {
            "platformName": "Android",
            "platformVersion": android_config.get("platform_version", "13"),
            "deviceName": device_name or android_config.get("device_name", "device"),
            "automationName": android_config.get("automation_name", "UiAutomator2"),
            "appPackage": app_config.get("app_package", ""),
            "appActivity": app_config.get("app_activity", ""),
            "noReset": android_config.get("no_reset", True),
            "dontStopAppOnReset": android_config.get("dont_stop_app_on_reset", True),
            # 中文输入支持
            "unicodeKeyboard": True,
            "resetKeyboard": True,
            # 允许获取 toast
            "automationName": "UiAutomator2",
        }

        return caps

    def quit(self):
        """关闭 driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Appium driver 已关闭")
            except Exception as e:
                logger.warning(f"关闭 driver 时出错: {e}")
            finally:
                self.driver = None

    def get_driver(self) -> Optional[WebDriver]:
        """获取当前 driver"""
        return self.driver

    def is_connected(self) -> bool:
        """检查 driver 是否连接正常"""
        if not self.driver:
            return False
        try:
            # 简单的健康检查
            self.driver.current_activity
            return True
        except Exception:
            return False
