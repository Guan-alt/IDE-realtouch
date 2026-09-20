"""
门锁串口功能测试
可以在没有Appium环境的情况下单独测试串口通信是否正常
运行方式: pytest tests/test_serial_smoke.py --serial-only
"""

import pytest

from common.logger import Logger

logger = Logger.get_logger(__name__)


class TestSerialSmoke:
    """串口冒烟测试"""

    def test_serial_connection(self, lock_serial):
        """测试串口能否正常连接"""
        assert lock_serial.is_connected(), "串口连接失败"
        logger.info("串口连接测试通过")

    def test_serial_read_logs(self, lock_serial):
        """测试能否读取到串口日志"""
        if not lock_serial.is_connected():
            pytest.skip("串口未连接")

        # 读取2秒日志
        logs = lock_serial.dump_logs(duration=2)
        logger.info(f"读取到日志行数: {len(logs.splitlines())}")

        # 至少能读到一些数据（正常运行的门锁应该有持续日志输出）
        # 如果完全没有日志，可能是波特率不对或者串口没接对
        if len(logs.strip()) == 0:
            logger.warning("未读取到任何串口日志，请检查波特率和连接")
        else:
            logger.info(f"日志预览 (前200字符): {logs[:200]}")

    def test_lock_status_query(self, lock_serial):
        """测试门锁状态查询"""
        if not lock_serial.is_connected():
            pytest.skip("串口未连接")

        status = lock_serial.get_lock_status()
        logger.info(f"门锁状态: {status}")
        # 状态可能是 locked / unlocked / unknown
        # 只要方法不报错就算基础通信正常
        assert status in ["locked", "unlocked", "unknown"], f"异常的状态值: {status}"

    def test_log_capture_context(self, lock_serial):
        """测试日志捕获上下文管理器"""
        if not lock_serial.is_connected():
            pytest.skip("串口未连接")

        with lock_serial.capture_logs(timeout=3) as capture:
            # 在捕获期间可以做一些操作
            pass

        logger.info(f"捕获到 {len(capture)} 行日志")
        # 验证 capture 对象的方法可用
        assert hasattr(capture, 'find')
        assert hasattr(capture, 'contains')
        assert hasattr(capture, 'all_lines')
