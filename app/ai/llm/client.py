"""外接 LLM 客户端（OpenAI 兼容）。"""

from functools import lru_cache

from openai import OpenAI

from app.config import Settings, get_settings


class LlmClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValueError("缺少 OPENAI_API_KEY，请在 .env 中配置")
        self._settings = settings
        self._client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    def chat(self, messages: list[dict[str, str]]) -> str:
        """同步聊天补全，返回助手文本。"""
        response = self._client.chat.completions.create(
            model=self._settings.llm_model,
            messages=messages,
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return content or ""


@lru_cache
def get_llm_client() -> LlmClient:
    return LlmClient(get_settings())
