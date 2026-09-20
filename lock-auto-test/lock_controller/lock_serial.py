"""
门锁串口控制器
通过串口与门锁通信，实现：
- 读取日志验证指令到达
- 查询门锁状态
- 发送调试指令
- 环境准备（重置门锁状态）
"""

import time
import re
from typing import List, Optional, Dict, Any, ContextManager
from contextlib import contextmanager

from drivers.serial_driver import SerialDriver
from lock_controller.log_parser import LogParser, LogEntry
from common.logger import Logger
from common.utils import wait_for

logger = Logger.get_logger(__name__)


class LockSerialController:
    """门锁串口控制器"""

    # ===== 常用日志关键字（请根据实际固件日志调整） =====
    LOG_KEY_UNLOCK_RECEIVED = r"unlock.*command.*received|收到.*开锁.*指令"
    LOG_KEY_UNLOCK_SUCCESS = r"unlock.*success|开锁.*成功"
    LOG_KEY_UNLOCK_FAILED = r"unlock.*fail|开锁.*失败"
    LOG_KEY_LOCK_RECEIVED = r"lock.*command.*received|收到.*关锁.*指令"
    LOG_KEY_LOCK_SUCCESS = r"lock.*success|关锁.*成功"
    LOG_KEY_STATUS_LOCKED = r"status.*locked|状态.*锁定"
    LOG_KEY_STATUS_UNLOCKED = r"status.*unlocked|状态.*开锁"
    LOG_KEY_PASSWORD_ADD = r"password.*add|添加.*密码"
    LOG_KEY_PASSWORD_DELETE = r"password.*delete|删除.*密码"

    def __init__(self, serial_config: Optional[dict] = None):
        """
        初始化门锁控制器

        Args:
            serial_config: 串口配置字典，不传则从配置文件读取
        """
        self.serial = SerialDriver(serial_config)
        self.parser = LogParser()

    # ============== 连接管理 ==============

    def connect(self):
        """连接门锁串口"""
        self.serial.connect()
        # 清空缓冲区
        self.serial.flush()
        logger.info("门锁串口控制器已就绪")

    def disconnect(self):
        """断开连接"""
        self.serial.disconnect()

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.serial.is_connected()

    # ============== 日志捕获 ==============

    @contextmanager
    def capture_logs(self, patterns: Optional[List[str]] = None, timeout: float = 10):
        """
        上下文管理器：捕获一段时间内的串口日志

        Args:
            patterns: 要关注的正则模式列表（可选，不提供则捕获所有日志）
            timeout: 最长捕获时间（秒）

        Yields:
            LogCaptureResult 对象，包含捕获到的日志
        """
        if not self.is_connected():
            raise RuntimeError("串口未连接")

        # 清空输入缓冲区
        self.serial.flush()

        captured_lines: List[str] = []
        result = LogCaptureResult(captured_lines, self.parser, patterns)

        start_time = time.time()
        logger.info(f"开始捕获串口日志 (超时: {timeout}s)")

        try:
            yield result
        finally:
            # 继续读取一段时间，确保捕获到后续日志
            remaining = timeout - (time.time() - start_time)
            if remaining > 0:
                logger.debug(f"继续读取剩余日志，剩余 {remaining:.1f}s")
                self._read_logs_until(captured_lines, timeout=remaining)
            logger.info(f"日志捕获结束，共捕获 {len(captured_lines)} 行")

    def _read_logs_until(self, lines: List[str], timeout: float):
        """持续读取日志直到超时"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            line = self.serial.read_line(timeout=0.2)
            if line:
                lines.append(line)
                logger.debug(f"[串口] {line}")

    # ============== 指令验证 ==============

    def wait_for_log(self, pattern: str, timeout: float = 10) -> Optional[LogEntry]:
        """
        等待匹配指定模式的日志出现

        Args:
            pattern: 正则表达式模式
            timeout: 超时时间（秒）

        Returns:
            匹配的日志条目，超时返回 None
        """
        if not self.is_connected():
            raise RuntimeError("串口未连接")

        self.serial.flush()
        regex = re.compile(pattern)
        start_time = time.time()

        logger.info(f"等待日志匹配: {pattern} (超时: {timeout}s)")

        while time.time() - start_time < timeout:
            line = self.serial.read_line(timeout=0.5)
            if line:
                logger.debug(f"[串口] {line}")
                if regex.search(line):
                    entry = self.parser.parse_line(line)
                    logger.info(f"匹配到日志: {line}")
                    return entry

        logger.warning(f"等待日志超时: {pattern}")
        return None

    def verify_command_received(self, command_type: str, timeout: float = 10) -> bool:
        """
        验证指令是否被门锁收到

        Args:
            command_type: 指令类型 ("unlock" / "lock" / "password_add" 等)
            timeout: 超时时间

        Returns:
            是否收到指令
        """
        pattern_map = {
            "unlock": self.LOG_KEY_UNLOCK_RECEIVED,
            "lock": self.LOG_KEY_LOCK_RECEIVED,
            "password_add": self.LOG_KEY_PASSWORD_ADD,
            "password_delete": self.LOG_KEY_PASSWORD_DELETE,
        }

        pattern = pattern_map.get(command_type)
        if not pattern:
            logger.warning(f"未知指令类型: {command_type}")
            return False

        return self.wait_for_log(pattern, timeout) is not None

    def verify_command_success(self, command_type: str, timeout: float = 10) -> bool:
        """
        验证指令是否执行成功

        Args:
            command_type: 指令类型
            timeout: 超时时间

        Returns:
            是否执行成功
        """
        success_map = {
            "unlock": self.LOG_KEY_UNLOCK_SUCCESS,
            "lock": self.LOG_KEY_LOCK_SUCCESS,
        }

        pattern = success_map.get(command_type)
        if not pattern:
            logger.warning(f"未知指令类型: {command_type}")
            return False

        return self.wait_for_log(pattern, timeout) is not None

    # ============== 状态查询 ==============

    def get_lock_status(self) -> str:
        """
        查询门锁当前状态

        Returns:
            "locked" / "unlocked" / "unknown"

        Note:
            具体实现取决于固件是否提供查询指令，
            如果没有，可以通过发送状态查询命令并解析返回日志来实现
        """
        # 方法一：发送查询指令（需要固件支持）
        # self.serial.write("AT+STATUS?")

        # 方法二：从持续的日志中推断（如果状态有心跳日志）
        # 这里提供一个简化实现，实际根据固件情况调整

        # 先清空缓冲区
        self.serial.flush()

        # 发送查询指令（示例，请替换为实际指令）
        # self.serial.write("get_status")

        # 读取一段时间的日志，查找状态相关的
        lines = []
        end_time = time.time() + 3
        while time.time() < end_time:
            line = self.serial.read_line(timeout=0.3)
            if line:
                lines.append(line)

        # 在日志中查找状态
        if self.parser.contains_keyword(lines, "locked") or \
           self.parser.find_first_match(lines, self.LOG_KEY_STATUS_LOCKED):
            return "locked"
        if self.parser.contains_keyword(lines, "unlocked") or \
           self.parser.find_first_match(lines, self.LOG_KEY_STATUS_UNLOCKED):
            return "unlocked"

        logger.warning("无法从日志中确定门锁状态")
        return "unknown"

    # ============== 环境准备 ==============

    def ensure_locked(self) -> bool:
        """
        确保门锁处于锁定状态
        如果当前是开锁状态，则发送关锁指令（如果支持）

        Returns:
            是否处于锁定状态
        """
        status = self.get_lock_status()
        if status == "locked":
            logger.info("门锁已处于锁定状态")
            return True

        if status == "unlocked":
            logger.info("门锁当前为开锁状态，尝试锁定...")
            # 尝试通过串口发送锁定指令（需要固件支持）
            # self.serial.write("lock")
            # 等待锁定成功
            if self.wait_for_log(self.LOG_KEY_LOCK_SUCCESS, timeout=5):
                logger.info("门锁已锁定")
                return True
            logger.warning("锁定门锁失败")
            return False

        # 状态未知，尝试发送关锁指令
        logger.info("门锁状态未知，尝试发送锁定指令...")
        # self.serial.write("lock")
        time.sleep(2)
        return self.get_lock_status() == "locked"

    def ensure_unlocked(self) -> bool:
        """
        确保门锁处于开锁状态

        Returns:
            是否处于开锁状态
        """
        status = self.get_lock_status()
        if status == "unlocked":
            logger.info("门锁已处于开锁状态")
            return True

        if status == "locked":
            logger.info("门锁当前为锁定状态，尝试开锁...")
            # self.serial.write("unlock")
            if self.wait_for_log(self.LOG_KEY_UNLOCK_SUCCESS, timeout=5):
                logger.info("门锁已开锁")
                return True
            logger.warning("开锁失败")
            return False

        logger.info("门锁状态未知，尝试发送开锁指令...")
        # self.serial.write("unlock")
        time.sleep(2)
        return self.get_lock_status() == "unlocked"

    # ============== 发送指令 ==============

    def send_command(self, command: str) -> bool:
        """
        发送调试指令（需要固件支持相应的调试指令）

        Args:
            command: 指令字符串

        Returns:
            是否发送成功
        """
        try:
            self.serial.write(command)
            logger.info(f"已发送指令: {command}")
            return True
        except Exception as e:
            logger.error(f"发送指令失败: {e}")
            return False

    # ============== 日志获取 ==============

    def dump_logs(self, duration: float = 2) -> str:
        """
        导出一段时间的日志（用于调试）

        Args:
            duration: 持续时间（秒）

        Returns:
            日志内容
        """
        return self.serial.read_all(duration)


class LogCaptureResult:
    """日志捕获结果"""

    def __init__(self, lines: List[str], parser: LogParser, patterns: Optional[List[str]] = None):
        self._lines = lines
        self._parser = parser
        self._patterns = patterns or []

    @property
    def all_lines(self) -> List[str]:
        """所有捕获到的日志行"""
        return self._lines.copy()

    def find(self, pattern: str) -> Optional[LogEntry]:
        """
        在捕获的日志中查找匹配的条目

        Args:
            pattern: 正则表达式

        Returns:
            第一个匹配的条目，找不到返回 None
        """
        return self._parser.find_first_match(self._lines, pattern)

    def find_all(self, pattern: str) -> List[LogEntry]:
        """查找所有匹配的条目"""
        return self._parser.find_matches(self._lines, pattern)

    def contains(self, keyword: str) -> bool:
        """是否包含指定关键字"""
        return self._parser.contains_keyword(self._lines, keyword)

    def count(self, pattern: str) -> int:
        """统计匹配次数"""
        return self._parser.count_matches(self._lines, pattern)

    def __len__(self) -> int:
        return len(self._lines)

    def __str__(self) -> str:
        return "\n".join(self._lines)
