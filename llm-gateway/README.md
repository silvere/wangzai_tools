# LLM Gateway

统一多模型 API 网关 + 用量监控 + 成本分析

## 快速开始

```bash
cd llm-gateway
pip install -r requirements.txt
cp .env.example .env  # 填入你的 API Keys
python -m app.main
```

访问 http://localhost:8800

## 功能

### v0.1 — 能用
- [x] 统一 `/v1/chat/completions` 接口
- [x] 支持 OpenAI / Anthropic / Google / DeepSeek
- [x] API Key 管理（多 provider key 配置）
- [x] 请求日志记录（SQLite）
- [x] 用量统计 + 成本计算
- [x] Web 管理界面
- [x] Token 认证（分发 access token 给下游用户）
- [ ] Docker 一键部署

### v0.2 — 好用
- [ ] 用量仪表盘（按模型/天/用户）
- [ ] 速率限制
- [ ] 自动重试 + 故障降级
- [ ] 多用户管理

### v0.3 — 值钱
- [ ] 语义缓存
- [ ] 多 Key 负载均衡
- [ ] Prompt 模板管理
- [ ] 用量告警 + Webhook

## 技术栈

- Python 3.10+
- FastAPI + Uvicorn
- SQLite (aiosqlite)
- httpx (异步 HTTP 客户端)
- 前端：纯 HTML/JS（零框架依赖）

## 架构

```
请求 → [认证] → [路由] → [Provider 适配] → [上游 API]
                              ↓
                         [日志记录]
                         [成本计算]
```

## License

MIT
