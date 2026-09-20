"""
门锁App操作抽象接口
自研App和米家App都需要实现这个接口，以便测试用例复用
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class LockAppInterface(ABC):
    """门锁App操作抽象接口"""

    # ============== 导航相关 ==============

    @abstractmethod
    def open_lock_detail(self, device_name: str) -> None:
        """
        进入门锁详情页

        Args:
            device_name: 门锁设备名称
        """
        ...

    @abstractmethod
    def go_back(self) -> None:
        """返回上一页"""
        ...

    # ============== 状态查询 ==============

    @abstractmethod
    def get_lock_status(self) -> str:
        """
        获取门锁当前状态

        Returns:
            "locked" - 已锁定
            "unlocked" - 已开锁
            "unknown" - 未知
        """
        ...

    @abstractmethod
    def is_lock_detail_displayed(self) -> bool:
        """检查是否在门锁详情页"""
        ...

    # ============== 操作相关 ==============

    @abstractmethod
    def click_unlock(self) -> None:
        """点击开锁按钮"""
        ...

    @abstractmethod
    def click_lock(self) -> None:
        """点击关锁按钮"""
        ...

    # ============== UI 元素验证 ==============

    @abstractmethod
    def is_unlock_button_displayed(self) -> bool:
        """检查开锁按钮是否显示"""
        ...

    @abstractmethod
    def is_lock_status_displayed(self) -> bool:
        """检查状态文字是否显示"""
        ...

    @abstractmethod
    def get_action_button_text(self) -> str:
        """
        获取操作按钮的文字

        Returns:
            "开锁" 或 "关锁" 或其他
        """
        ...

    # ============== 等待相关 ==============

    @abstractmethod
    def wait_for_status(self, status: str, timeout: float = 10) -> bool:
        """
        等待门锁状态变为指定值

        Args:
            status: 期望的状态 ("locked" / "unlocked")
            timeout: 超时时间（秒）

        Returns:
            是否在超时前变为指定状态
        """
        ...

    # ============== 临时密码（可选实现） ==============

    def add_temp_password(self, password: str, name: str = "") -> bool:
        """
        添加临时密码（可选方法，子类可按需实现）

        Args:
            password: 密码内容
            name: 密码名称

        Returns:
            是否添加成功
        """
        raise NotImplementedError("该方法未实现")

    def delete_temp_password(self, password_name: str) -> bool:
        """
        删除临时密码（可选方法，子类可按需实现）

        Args:
            password_name: 密码名称

        Returns:
            是否删除成功
        """
        raise NotImplementedError("该方法未实现")

    def get_temp_password_list(self) -> List[str]:
        """
        获取临时密码列表（可选方法，子类可按需实现）

        Returns:
            密码名称列表
        """
        raise NotImplementedError("该方法未实现")
