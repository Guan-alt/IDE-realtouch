"""
配置管理模块
统一读取 yaml 配置文件，提供全局配置访问接口
"""

import os
import yaml
from typing import Any, Dict


class Config:
    """配置管理器"""

    _instance = None
    _config: Dict[str, Any] = {}
    _devices: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置文件"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "config", "config.yaml")
        devices_path = os.path.join(base_dir, "config", "devices.yaml")

        # 加载主配置
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

        # 加载设备配置
        if os.path.exists(devices_path):
            with open(devices_path, "r", encoding="utf-8") as f:
                devices_data = yaml.safe_load(f) or {}
                self._devices = devices_data.get("devices", {})

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点分隔的嵌套键
        例如: Config.get("appium.host")
        """
        config = cls()._config
        keys = key.split(".")
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
        return config

    @classmethod
    def get_device(cls, device_key: str = "default") -> Dict[str, Any]:
        """获取指定设备的配置"""
        devices = cls()._devices
        return devices.get(device_key, {})

    @classmethod
    def get_all_devices(cls) -> Dict[str, Any]:
        """获取所有设备配置"""
        return cls()._devices

    @classmethod
    def reload(cls):
        """重新加载配置"""
        cls._instance = None
        return cls()
