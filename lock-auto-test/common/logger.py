"""
日志工具模块
提供统一的日志配置和获取接口
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from common.config import Config


class Logger:
    """日志管理器"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = "lock_auto_test") -> logging.Logger:
        """获取 logger 实例"""
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(cls._get_level())
        logger.propagate = False

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setLevel(cls._get_level())
        console_handler.setFormatter(cls._get_formatter())
        logger.addHandler(console_handler)

        # 文件输出
        file_handler = cls._get_file_handler()
        if file_handler:
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @staticmethod
    def _get_level() -> int:
        """获取日志级别"""
        level_str = Config.get("log.level", "INFO").upper()
        return getattr(logging, level_str, logging.INFO)

    @staticmethod
    def _get_formatter() -> logging.Formatter:
        """获取日志格式化器"""
        fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        return logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    @classmethod
    def _get_file_handler(cls) -> RotatingFileHandler | None:
        """获取文件日志处理器"""
        log_dir = Config.get("log.log_dir", "./reports/logs")

        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError:
            return None

        log_file = os.path.join(
            log_dir,
            f"test_{datetime.now().strftime('%Y%m%d')}.log"
        )

        max_bytes = int(Config.get("log.max_bytes", 10)) * 1024 * 1024
        backup_count = int(Config.get("log.backup_count", 5))

        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        handler.setLevel(cls._get_level())
        handler.setFormatter(cls._get_formatter())
        return handler
