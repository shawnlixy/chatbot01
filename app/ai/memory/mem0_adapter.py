"""Mem0 适配器：默认长期记忆实现（本地 Qdrant 路径，无独立向量服务）。"""

from pathlib import Path
from typing import Any, Optional

from mem0 import Memory

from app.ai.memory.port import MemoryPort
from app.config import Settings


class Mem0Adapter(MemoryPort):
    def __init__(self, settings: Settings) -> None:
        # 确保本地数据目录存在
        Path(settings.mem0_qdrant_path).mkdir(parents=True, exist_ok=True)
        Path(settings.mem0_history_db).parent.mkdir(parents=True, exist_ok=True)

        # 与聊天 LLM 共用同一套 OpenAI 兼容凭证
        config: dict[str, Any] = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": settings.llm_model,
                    "api_key": settings.openai_api_key,
                    "openai_base_url": settings.openai_base_url,
                    "temperature": 0.1,
                },
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": settings.embed_model,
                    "api_key": settings.openai_api_key,
                    "openai_base_url": settings.openai_base_url,
                },
            },
            # 嵌入式本地 Qdrant：不启独立进程/集群
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": settings.mem0_collection,
                    "path": settings.mem0_qdrant_path,
                    "on_disk": True,
                },
            },
            "history_db_path": settings.mem0_history_db,
        }
        self._memory = Memory.from_config(config)

    def add(
        self,
        messages: list[dict[str, str]],
        *,
        user_id: str,
        agent_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"user_id": user_id}
        if agent_id:
            kwargs["agent_id"] = agent_id
        if metadata:
            kwargs["metadata"] = metadata
        return self._memory.add(messages, **kwargs)

    def search(
        self,
        query: str,
        *,
        user_id: str,
        agent_id: Optional[str] = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {"user_id": user_id}
        if agent_id:
            filters["agent_id"] = agent_id
        result = self._memory.search(query, filters=filters, top_k=top_k)
        return list(result.get("results") or [])

    def get_all(
        self,
        *,
        user_id: str,
        agent_id: Optional[str] = None,
        top_k: int = 50,
    ) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {"user_id": user_id}
        if agent_id:
            filters["agent_id"] = agent_id
        result = self._memory.get_all(filters=filters, top_k=top_k)
        return list(result.get("results") or [])
