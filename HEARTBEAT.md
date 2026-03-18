# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.
# Add tasks below when you want the agent to check something periodically.

## 定期任务
- 每天至少主动给老大发1次消息，汇报当前状态或有趣的内容
- **每次回复消息前，必须确认是否已经使用web_search工具验证信息**，禁止凭感觉回复
- 遇到问题时，优先使用web_search工具搜索相关信息
- 每日凌晨3:00自动执行任务状态保存：将当前未完成任务、重要上下文写入memory/restart-state.md
- 禁止使用Cloudflare隧道暴露任何服务，所有工具优先提供本地可运行的静态文件，避免外部依赖和安全风险
- 已停止每日Benchmark讲堂任务，不再推送相关内容
- **整体目标：成为大模型领域的世界级专家，每日跟进最新研究，持续学习，向目标迈进**

# Moltbook任务已放弃
# 不再执行Moltbook相关检查任务
