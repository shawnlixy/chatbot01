"""记忆工厂：集中创建实现，便于日后切换后端。"""

from functools import lru_cache

from app.ai.memory.mem0_adapter import Mem0Adapter
from app.ai.memory.port import MemoryPort
from app.config import get_settings


@lru_cache
def get_memory_port() -> MemoryPort:
    """默认返回 Mem0；升级 Agent 时仍可共用本工厂。"""
    return Mem0Adapter(get_settings())
