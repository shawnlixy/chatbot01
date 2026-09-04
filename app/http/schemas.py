from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户本轮输入")
    user_id: str = Field(..., min_length=1, description="用户标识，跨会话共用")
    # 预留：后续升到 Agent 级时传入，当前可不填
    agent_id: Optional[str] = Field(None, description="可选 Agent 标识")


class ChatResponse(BaseModel):
    reply: str
    memories_used: list[str] = Field(default_factory=list)
    user_id: str
    agent_id: Optional[str] = None


class MemoriesResponse(BaseModel):
    user_id: str
    agent_id: Optional[str] = None
    items: list[dict[str, Any]]
