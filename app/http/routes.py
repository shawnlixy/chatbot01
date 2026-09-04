"""HTTP 路由：薄传输层，业务编排放在本模块函数内即可。"""

from fastapi import APIRouter, Depends, HTTPException

from app.ai.llm.client import LlmClient, get_llm_client
from app.ai.memory.factory import get_memory_port
from app.ai.memory.port import MemoryPort
from app.config import Settings, get_settings
from app.http.schemas import ChatRequest, ChatResponse, MemoriesResponse

router = APIRouter()


def _format_memories(items: list[dict]) -> list[str]:
    """把 Mem0 结果整理成可注入 prompt 的短句列表。"""
    lines: list[str] = []
    for item in items:
        text = item.get("memory") or item.get("text") or ""
        if text:
            lines.append(str(text))
    return lines


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    settings: Settings = Depends(get_settings),
    llm: LlmClient = Depends(get_llm_client),
    memory: MemoryPort = Depends(get_memory_port),
) -> ChatResponse:
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="未配置 OPENAI_API_KEY")

    # 1) 检索长期记忆
    hits = memory.search(
        body.message,
        user_id=body.user_id,
        agent_id=body.agent_id,
        top_k=settings.memory_top_k,
    )
    memory_lines = _format_memories(hits)
    memories_block = "\n".join(f"- {line}" for line in memory_lines) or "- （暂无历史记忆）"

    # 2) 拼装上下文并调用外接 LLM
    system_prompt = (
        "你是有长期记忆的助手。优先依据「用户记忆」回答与用户相关的事实性问题；"
        "记忆不足时再据常识作答，并说明不确定之处。\n"
        f"用户记忆：\n{memories_block}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": body.message},
    ]
    reply = llm.chat(messages)

    # 3) 回写记忆（含本轮问答，便于抽取偏好/事实）
    memory.add(
        [
            {"role": "user", "content": body.message},
            {"role": "assistant", "content": reply},
        ],
        user_id=body.user_id,
        agent_id=body.agent_id,
    )

    return ChatResponse(
        reply=reply,
        memories_used=memory_lines,
        user_id=body.user_id,
        agent_id=body.agent_id,
    )


@router.get("/memories", response_model=MemoriesResponse)
def list_memories(
    user_id: str,
    agent_id: str | None = None,
    top_k: int = 50,
    memory: MemoryPort = Depends(get_memory_port),
) -> MemoriesResponse:
    items = memory.get_all(user_id=user_id, agent_id=agent_id, top_k=top_k)
    return MemoriesResponse(user_id=user_id, agent_id=agent_id, items=items)
