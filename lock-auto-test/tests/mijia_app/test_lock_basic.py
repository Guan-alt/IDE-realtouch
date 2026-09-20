"""
米家App门锁基础功能测试
（骨架代码，待元素定位确认后完善）

运行方式: pytest tests/mijia_app/ --app=mijia_app
"""

import pytest

from pages.mijia_app.lock_plugin_page import MijiaLockPage
from common.logger import Logger

logger = Logger.get_logger(__name__)


class TestMijiaLockBasic:
    """米家App门锁基础功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, app_driver, test_device):
        """每个用例前的准备：进入门锁插件页"""
        if app_driver is None:
            pytest.skip("串口-only 模式，跳过UI测试")

        self.driver = app_driver
        self.lock_page = MijiaLockPage(app_driver)
        self.lock_page.open_lock_detail(test_device.name)

    def test_lock_page_displayed(self):
        """验证门锁插件页是否正常打开"""
        assert self.lock_page.is_lock_detail_displayed(), "门锁插件页未正常加载"
        logger.info("米家门锁插件页加载成功")

    def test_lock_status(self):
        """验证门锁状态显示"""
        status = self.lock_page.get_lock_status()
        assert status != "unknown", f"门锁状态异常: {status}"
        logger.info(f"门锁状态: {status}")

    def test_remote_unlock_e2e(self, lock_serial):
        """
        远程开锁端到端测试（米家）
        """
        if not lock_serial.is_connected():
            pytest.skip("串口未连接")

        logger.info("米家App：远程开锁端到端测试")

        # 前置：确保门锁锁定
        lock_serial.ensure_locked()

        # 捕获日志并操作
        with lock_serial.capture_logs(timeout=15) as log_capture:
            self.lock_page.click_unlock()
            ui_success = self.lock_page.wait_for_status("unlocked", timeout=10)

        # 验证UI
        assert ui_success, "UI未更新为开锁状态"

        # 验证门锁收到指令
        assert log_capture.find(lock_capture.LOG_KEY_UNLOCK_RECEIVED if hasattr(log_capture, 'LOG_KEY_UNLOCK_RECEIVED') else "unlock"), \
            "门锁未收到开锁指令"

        logger.info("米家App远程开锁测试通过")
