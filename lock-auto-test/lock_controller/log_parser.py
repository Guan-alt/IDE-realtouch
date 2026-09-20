"""
门锁日志解析器
解析串口日志，提取关键信息
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from common.logger import Logger

logger = Logger.get_logger(__name__)


@dataclass
class LogEntry:
    """日志条目"""
    raw: str                    # 原始日志行
    timestamp: str = ""         # 时间戳（如果有）
    level: str = ""             # 日志级别（INFO/WARN/ERROR等）
    module: str = ""            # 模块名
    message: str = ""           # 消息内容
    matched: bool = False       # 是否匹配到了关键字


class LogParser:
    """日志解析器"""

    def __init__(self):
        # 常见日志格式的正则（可根据实际日志格式调整）
        self._patterns = [
            # 格式: [时间] [级别] 模块: 消息
            re.compile(
                r'^\[(?P<timestamp>[\d\-:\s.]+)\]\s+'
                r'\[(?P<level>\w+)\]\s+'
                r'(?P<module>[\w_]+):\s+'
                r'(?P<message>.*)$'
            ),
            # 格式: 时间 级别 模块: 消息
            re.compile(
                r'^(?P<timestamp>[\d\-:\s.]+)\s+'
                r'(?P<level>\w+)\s+'
                r'(?P<module>[\w_]+):\s+'
                r'(?P<message>.*)$'
            ),
        ]

    def parse_line(self, line: str) -> LogEntry:
        """
        解析一行日志

        Args:
            line: 原始日志行

        Returns:
            LogEntry 对象
        """
        line = line.strip()
        entry = LogEntry(raw=line, message=line)

        for pattern in self._patterns:
            match = pattern.match(line)
            if match:
                entry.timestamp = match.group("timestamp").strip()
                entry.level = match.group("level").strip()
                entry.module = match.group("module").strip()
                entry.message = match.group("message").strip()
                break

        return entry

    def find_matches(self, lines: List[str], pattern: str) -> List[LogEntry]:
        """
        在日志行列表中查找匹配指定模式的条目

        Args:
            lines: 日志行列表
            pattern: 正则表达式模式

        Returns:
            匹配的 LogEntry 列表
        """
        regex = re.compile(pattern)
        matches = []

        for line in lines:
            entry = self.parse_line(line)
            if regex.search(entry.message) or regex.search(entry.raw):
                entry.matched = True
                matches.append(entry)

        return matches

    def find_first_match(self, lines: List[str], pattern: str) -> Optional[LogEntry]:
        """
        查找第一个匹配的日志条目

        Args:
            lines: 日志行列表
            pattern: 正则表达式模式

        Returns:
            第一个匹配的 LogEntry，找不到返回 None
        """
        matches = self.find_matches(lines, pattern)
        return matches[0] if matches else None

    def extract_value(self, line: str, key: str) -> Optional[str]:
        """
        从日志中提取 key=value 格式的值

        Args:
            line: 日志行
            key: 键名

        Returns:
            值，找不到返回 None
        """
        # 支持 key=value, key: value, "key":"value" 等格式
        patterns = [
            rf'{key}\s*=\s*"([^"]+)"',
            rf'{key}\s*=\s*([^\s,]+)',
            rf'{key}\s*:\s*"([^"]+)"',
            rf'{key}\s*:\s*([^\s,}}]+)',
        ]

        for pat in patterns:
            match = re.search(pat, line)
            if match:
                return match.group(1)

        return None

    def contains_keyword(self, lines: List[str], keyword: str) -> bool:
        """检查日志列表中是否包含指定关键字"""
        for line in lines:
            if keyword in line:
                return True
        return False

    def count_matches(self, lines: List[str], pattern: str) -> int:
        """统计匹配次数"""
        return len(self.find_matches(lines, pattern))
