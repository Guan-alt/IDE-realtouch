"""
pytest 全局 fixture 配置
"""

import os
import sys
import pytest

# 把项目根目录加入 path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from common.config import Config
from common.logger import Logger
from common.utils import take_screenshot, ensure_dir
from drivers.appium_driver import AppiumDriver
from lock_controller.lock_serial import LockSerialController

logger = Logger.get_logger(__name__)


def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption(
        "--app",
        action="store",
        default="self_app",
        help="测试的App类型: self_app 或 mijia_app"
    )
    parser.addoption(
        "--device",
        action="store",
        default="default",
        help="测试设备配置键名，对应 devices.yaml 中的设备"
    )
    parser.addoption(
        "--serial-only",
        action="store_true",
        default=False,
        help="仅测试串口功能，不启动Appium"
    )


@pytest.fixture(scope="session")
def app_type(request):
    """获取当前测试的App类型"""
    return request.config.getoption("--app")


@pytest.fixture(scope="session")
def device_key(request):
    """获取设备配置键名"""
    return request.config.getoption("--device")


@pytest.fixture(scope="session")
def test_device(device_key):
    """获取测试设备配置"""
    device_config = Config.get_device(device_key)
    if not device_config:
        logger.warning(f"未找到设备配置: {device_key}，使用默认配置")
        device_config = Config.get_device("default") or {}
    return type("DeviceConfig", (), device_config)()


@pytest.fixture(scope="session")
def serial_only(request):
    """是否仅串口测试模式"""
    return request.config.getoption("--serial-only")


@pytest.fixture(scope="function")
def app_driver(app_type, test_device, serial_only):
    """
    Appium driver fixture
    每个测试函数创建一个新的 driver，测试结束后关闭

    如果是 serial-only 模式，返回 None
    """
    if serial_only:
        yield None
        return

    appium = AppiumDriver(app_type=app_type)
    driver = appium.create_driver(
        device_name=Config.get("android.device_name")
    )

    yield driver

    # 测试结束后的清理
    appium.quit()


@pytest.fixture(scope="function")
def lock_serial(test_device):
    """
    门锁串口控制器 fixture
    每个测试函数创建一个新的连接，测试结束后关闭
    """
    # 合并设备的串口配置和默认配置
    serial_config = Config.get("serial", {}).copy()
    device_serial = getattr(test_device, "serial", None)
    if device_serial:
        serial_config.update(device_serial)

    controller = LockSerialController(serial_config)

    try:
        controller.connect()
    except Exception as e:
        logger.warning(f"串口连接失败: {e}，串口相关验证将跳过")
        # 连接失败时仍然返回 controller，但 is_connected 为 False
        # 用例中需要检查连接状态
        yield controller
        return

    yield controller

    # 测试结束后断开
    controller.disconnect()


@pytest.fixture(scope="session", autouse=True)
def ensure_directories():
    """确保报告和日志目录存在"""
    ensure_dir(Config.get("report.report_dir", "./reports"))
    ensure_dir(Config.get("report.screenshot_dir", "./reports/screenshots"))
    ensure_dir(Config.get("log.log_dir", "./reports/logs"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试失败时自动截图
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # 尝试从 fixture 中获取 driver
        driver_fixture = item.funcargs.get("app_driver")
        if driver_fixture:
            screenshot_dir = Config.get("report.screenshot_dir", "./reports/screenshots")
            screenshot_dir = os.path.join(BASE_DIR, screenshot_dir)
            take_screenshot(driver_fixture, screenshot_dir, prefix=item.name)
