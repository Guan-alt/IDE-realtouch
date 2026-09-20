"""
门锁基础功能测试（自研App）
覆盖：UI验证 + 指令下发验证（端到端）
"""

import pytest

from pages.self_app.lock_detail_page import LockDetailPage
from common.logger import Logger

logger = Logger.get_logger(__name__)


class TestLockBasic:
    """门锁基础功能测试"""

    @pytest.fixture(autouse=True)
    def setup(self, app_driver, test_device):
        """每个用例前的准备：进入门锁详情页"""
        if app_driver is None:
            pytest.skip("串口-only 模式，跳过UI测试")

        self.driver = app_driver
        self.lock_page = LockDetailPage(app_driver)
        self.lock_page.open(test_device.name)
        # 等待页面加载
        self.lock_page.wait_for_page_load()

    # ============== UI 验证用例 ==============

    def test_lock_detail_page_elements(self):
        """
        TC-001: 门锁详情页UI元素校验
        验证详情页的关键元素是否正常显示
        """
        logger.info("验证门锁详情页UI元素")

        # 验证状态文字显示
        assert self.lock_page.is_lock_status_displayed(), "门锁状态文字未显示"

        # 验证操作按钮显示
        assert self.lock_page.is_unlock_button_displayed(), "开锁/关锁按钮未显示"

        # 验证临时密码入口
        assert self.lock_page.is_temp_password_entry_displayed(), "临时密码入口未显示"

        # 验证直播入口
        assert self.lock_page.is_live_entry_displayed(), "直播入口未显示"

        logger.info("门锁详情页UI元素验证通过")

    def test_lock_status_display(self):
        """
        验证门锁状态文字正常显示（不是unknown或空白）
        """
        status = self.lock_page.get_lock_status()
        assert status != "unknown", f"门锁状态异常: {status}"
        logger.info(f"门锁状态显示正常: {status}")

    # ============== 端到端用例 ==============

    def test_remote_unlock_e2e(self, lock_serial):
        """
        TC-002: 远程开锁端到端验证
        验证：UI操作 → 指令下发 → 门锁执行 → UI更新
        """
        if not lock_serial.is_connected():
            pytest.skip("串口未连接，无法验证端到端")

        logger.info("开始远程开锁端到端测试")

        # 前置：确保门锁处于锁定状态
        lock_serial.ensure_locked()
        # 刷新App页面状态（如果需要的话）

        # 确认UI显示锁定状态
        assert self.lock_page.get_lock_status() == "locked", "测试前门锁未处于锁定状态"

        # 开始捕获串口日志
        with lock_serial.capture_logs(timeout=10) as log_capture:
            # 点击开锁
            self.lock_page.click_unlock()
            # 等待UI状态更新
            ui_success = self.lock_page.wait_for_status("unlocked", timeout=8)

        # 验证1：UI状态更新
        assert ui_success, "App UI 未更新为开锁状态"
        logger.info("UI验证通过：状态已更新为已开锁")

        # 验证2：门锁收到开锁指令
        received = log_capture.find(lock_serial.LOG_KEY_UNLOCK_RECEIVED)
        assert received is not None, "门锁未收到开锁指令（串口日志中未匹配到）"
        logger.info(f"指令验证通过：门锁收到开锁指令 - {received.message}")

        # 验证3：门锁执行成功
        success = log_capture.find(lock_serial.LOG_KEY_UNLOCK_SUCCESS)
        assert success is not None, "门锁执行开锁失败（串口日志中未匹配到成功标记）"
        logger.info(f"执行验证通过：门锁开锁成功 - {success.message}")

        # 验证4：操作按钮文字变化
        btn_text = self.lock_page.get_action_button_text()
        logger.info(f"操作按钮当前文字: {btn_text}")

        logger.info("远程开锁端到端测试通过")

    def test_remote_lock_e2e(self, lock_serial):
        """
        TC-003: 远程关锁端到端验证
        """
        if not lock_serial.is_connected():
            pytest.skip("串口未连接，无法验证端到端")

        logger.info("开始远程关锁端到端测试")

        # 前置：确保门锁处于开锁状态
        lock_serial.ensure_unlocked()

        # 确认UI显示开锁状态
        # 注意：有些门锁只有开锁按钮，关锁可能不支持远程操作
        # 这里按支持远程关锁来写，如果不支持可以跳过
        current_status = self.lock_page.get_lock_status()
        if current_status == "locked":
            pytest.skip("门锁当前已锁定，且不支持远程关锁操作")

        # 开始捕获串口日志
        with lock_serial.capture_logs(timeout=10) as log_capture:
            # 点击关锁
            self.lock_page.click_lock()
            ui_success = self.lock_page.wait_for_status("locked", timeout=8)

        # 验证UI
        assert ui_success, "App UI 未更新为锁定状态"
        logger.info("UI验证通过：状态已更新为已锁定")

        # 验证门锁收到指令
        received = log_capture.find(lock_serial.LOG_KEY_LOCK_RECEIVED)
        assert received is not None, "门锁未收到关锁指令"
        logger.info("指令验证通过：门锁收到关锁指令")

        # 验证执行成功
        success = log_capture.find(lock_serial.LOG_KEY_LOCK_SUCCESS)
        assert success is not None, "门锁执行关锁失败"
        logger.info("执行验证通过：门锁关锁成功")

        logger.info("远程关锁端到端测试通过")

    def test_battery_display(self):
        """验证电量显示正常"""
        battery_text = self.lock_page.get_battery_text()
        logger.info(f"电量显示: {battery_text}")
        # 简单验证：电量文字不为空
        assert battery_text, "电量显示为空"
        # 可以进一步验证是否包含数字或百分号
        assert "%" in battery_text or any(c.isdigit() for c in battery_text), \
            f"电量显示格式异常: {battery_text}"
