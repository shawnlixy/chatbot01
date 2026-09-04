"""应用配置：仅从环境变量读取密钥与模型参数。"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（app/ 的上一级）
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI 兼容接口（也可用国内兼容网关的 base_url）
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    embed_model: str = "text-embedding-3-small"

    # 本地向量路径（Qdrant 嵌入式，不启独立服务）
    mem0_collection: str = "chatbot01"
    mem0_qdrant_path: str = str(DATA_DIR / "qdrant")
    mem0_history_db: str = str(DATA_DIR / "history.db")

    # 检索条数
    memory_top_k: int = 5

    app_name: str = "chatbot01"
    debug: bool = True


@lru_cache
def get_settings() -> Settings:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()
