
"""
串口 Driver 封装
封装 pyserial 的基础操作，提供串口连接、读取、写入等能力
作为 LockSerialController 的底层驱动
"""

import time
from typing import Optional

import serial
import serial.tools.list_ports

from common.config import Config
from common.logger import Logger

logger = Logger.get_logger(__name__)


class SerialDriver:
    """串口驱动封装"""

    def __init__(self, config: Optional[dict] = None):
        """
        初始化串口驱动

        Args:
            config: 串口配置字典，不传则从配置文件读取
        """
        if config is None:
            config = Config.get("serial", {})

        self.port = config.get("port", "COM3")
        self.baudrate = config.get("baudrate", 115200)
        self.bytesize = config.get("bytesize", 8)
        self.stopbits = config.get("stopbits", 1)
        self.parity = config.get("parity", "N")
        self.timeout = config.get("timeout", 1)

        self.ser: Optional[serial.Serial] = None

    @staticmethod
    def list_ports() -> list:
        """列出当前所有可用串口"""
        ports = serial.tools.list_ports.comports()
        return [{"device": p.device, "description": p.description} for p in ports]

    def connect(self):
        """打开串口连接"""
        if self.ser and self.ser.is_open:
            logger.warning(f"串口 {self.port} 已打开，无需重复连接")
            return

        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                stopbits=self.stopbits,
                parity=self.parity,
                timeout=self.timeout
            )
            logger.info(f"串口 {self.port} 连接成功 (波特率: {self.baudrate})")
        except serial.SerialException as e:
            logger.error(f"串口 {self.port} 连接失败: {e}")
            raise

    def disconnect(self):
        """关闭串口连接"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                logger.info(f"串口 {self.port} 已关闭")
            except Exception as e:
                logger.warning(f"关闭串口时出错: {e}")
            finally:
                self.ser = None

    def is_connected(self) -> bool:
        """检查串口是否已连接"""
        return self.ser is not None and self.ser.is_open

    def read_line(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        读取一行数据

        Args:
            timeout: 超时时间（秒），不传则使用默认超时

        Returns:
            读取到的一行字符串（不含换行符），超时返回 None
        """
        if not self.is_connected():
            raise RuntimeError("串口未连接")

        original_timeout = self.ser.timeout
        if timeout is not None:
            self.ser.timeout = timeout

        try:
            line = self.ser.readline()
            if line:
                try:
                    return line.decode("utf-8", errors="replace").rstrip("\r\n")
                except Exception:
                    return repr(line)
            return None
        finally:
            if timeout is not None:
                self.ser.timeout = original_timeout

    def read_all(self, duration: float = 0.5) -> str:
        """
        读取一段时间内的所有数据

        Args:
            duration: 读取持续时间（秒）

        Returns:
            读取到的所有内容
        """
        if not self.is_connected():
            raise RuntimeError("串口未连接")

        # 先清空输入缓冲区
        self.ser.reset_input_buffer()

        lines = []
        start_time = time.time()
        while time.time() - start_time < duration:
            line = self.read_line(timeout=0.1)
            if line:
                lines.append(line)

        return "\n".join(lines)

    def write(self, data: str):
        """
        向串口写入数据

        Args:
            data: 要写入的字符串
        """
        if not self.is_connected():
            raise RuntimeError("串口未连接")

        if not data.endswith("\r\n"):
            data = data + "\r\n"

        self.ser.write(data.encode("utf-8"))
        logger.debug(f"串口写入: {data.strip()}")

    def flush(self):
        """清空串口缓冲区"""
        if self.is_connected():
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
