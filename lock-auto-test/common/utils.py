"""
通用工具函数
"""

import os
import time
import base64
from datetime import datetime
from typing import Optional

from common.logger import Logger

logger = Logger.get_logger(__name__)


def take_screenshot(driver, save_dir: str, prefix: str = "screenshot") -> Optional[str]:
    """
    截取屏幕截图并保存

    Args:
        driver: Appium driver
        save_dir: 保存目录
        prefix: 文件名前缀

    Returns:
        截图文件路径，失败返回 None
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(save_dir, filename)
        driver.save_screenshot(filepath)
        logger.info(f"截图已保存: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"截图失败: {e}")
        return None


def get_page_source(driver, save_dir: str, prefix: str = "pagesource") -> Optional[str]:
    """
    保存页面结构（用于调试）

    Args:
        driver: Appium driver
        save_dir: 保存目录
        prefix: 文件名前缀

    Returns:
        文件路径，失败返回 None
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.xml"
        filepath = os.path.join(save_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info(f"页面结构已保存: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"保存页面结构失败: {e}")
        return None


def wait_for(condition_func, timeout: float = 10, interval: float = 0.5, **kwargs):
    """
    通用等待函数，等待条件满足

    Args:
        condition_func: 判断条件的函数，返回 True 表示条件满足
        timeout: 超时时间（秒）
        interval: 轮询间隔（秒）
        **kwargs: 传给 condition_func 的参数

    Returns:
        条件函数的返回值（如果在超时前满足）

    Raises:
        TimeoutError: 超时仍未满足条件
    """
    start_time = time.time()
    last_result = None

    while time.time() - start_time < timeout:
        try:
            last_result = condition_func(**kwargs)
            if last_result:
                return last_result
        except Exception:
            # 条件函数执行异常时继续等待
            pass
        time.sleep(interval)

    raise TimeoutError(
        f"等待超时 ({timeout}s)，条件函数始终未满足。最后结果: {last_result}"
    )


def retry(func, max_retries: int = 3, delay: float = 1, **kwargs):
    """
    通用重试函数

    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
        **kwargs: 传给 func 的参数

    Returns:
        函数执行结果

    Raises:
        Exception: 超过最大重试次数仍失败
    """
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            result = func(**kwargs)
            if attempt > 1:
                logger.info(f"重试成功（第 {attempt} 次）")
            return result
        except Exception as e:
            last_exception = e
            logger.warning(f"第 {attempt} 次执行失败: {e}")
            if attempt < max_retries:
                time.sleep(delay)

    raise last_exception


def timestamp_str(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime(fmt)


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
