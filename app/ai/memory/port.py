"""记忆端口：跨项目可复用的抽象，业务只依赖本接口。"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class MemoryPort(ABC):
    """长期记忆端口。后续可换成 Graphiti / MySQL 事实表等实现。"""

    @abstractmethod
    def add(
        self,
        messages: list[dict[str, str]],
        *,
        user_id: str,
        agent_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """从对话中抽取并写入长期记忆。"""

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        user_id: str,
        agent_id: Optional[str] = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """按语义检索与用户相关的记忆条目。"""

    @abstractmethod
    def get_all(
        self,
        *,
        user_id: str,
        agent_id: Optional[str] = None,
        top_k: int = 50,
    ) -> list[dict[str, Any]]:
        """列出某用户（及可选 agent）下的记忆，便于调试。"""
