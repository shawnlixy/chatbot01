# chatbot01：外接 LLM + Mem0 长期记忆 MVP

Python 3.13 + FastAPI 聊天服务，通过 `MemoryPort` 外挂 [mem0ai/mem0](https://github.com/mem0ai/mem0)（约 65k stars，Apache-2.0，近期持续更新）。文档：https://docs.mem0.ai

## 能力

- `POST /api/chat`：检索记忆 → 调外接 LLM → 回写记忆
- `GET /api/memories`：按 `user_id` 查看已存事实（调试）
- 向量用 **本地路径 Qdrant**（进程内嵌入式），不部署独立向量集群
- `agent_id` 字段已预留，便于后续升到 Agent 编排

## 快速启动

```bash
cd D:/cursor/chatbot/chatbot01
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY（或兼容网关的 KEY + OPENAI_BASE_URL）

uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：`GET http://127.0.0.1:8000/health`

## 验收示例

同一 `user_id` 跨两次请求：

```bash
curl -X POST http://127.0.0.1:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"demo\",\"message\":\"我叫小明，喜欢深色主题\"}"

curl -X POST http://127.0.0.1:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"demo\",\"message\":\"我喜欢什么主题？\"}"
```

第二次应答应能提到深色主题；也可用 `GET /api/memories?user_id=demo` 查看抽取结果。

## 目录（可复用脚手架）

```
app/
  ai/
    llm/          # 外接模型
    memory/       # MemoryPort + Mem0Adapter
  http/           # 薄路由
  config.py
  main.py
```

跨项目复用时：拷贝 `app/ai/memory/`，业务只依赖 `MemoryPort`；换后端实现工厂即可。

## 升级到 Agent 级（预留，本 MVP 未实现）

1. 继续使用同一 `MemoryPort`，请求带上 `agent_id`
2. 增加有限步 Agent 编排（LangGraph 或自研状态机），工具写回记忆
3. 需要时序事实时，可新增 `GraphitiAdapter` 实现同一端口
4. 一般不必先换 Letta；若要整栈 Agent OS 再评估

## 选型摘要

| 库 | 建议 |
| --- | --- |
| Mem0 | **主选**：外挂记忆层，上手低，可脚手架化 |
| Graphiti | 二号位：事实会过期/变更时再加 |
| Letta | 不做 MVP：会替换运行时，违背「先外挂」 |
| LangMem | 仅已深度使用 LangGraph 时考虑 |
