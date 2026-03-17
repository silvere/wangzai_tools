# 长期记忆

## 老大的兴趣与偏好
- 对 AI Coding 和 Agent 领域很感兴趣，关注未来职业方向
- 对内容创作感兴趣：小红书、公众号、故事生成，想搞一个 Content Creator Agent
- 优先从公众号开始做（2026-02-14 确认）
- 喜欢交互式网页工具，要求所有网页发公网链接 + 索引页统一管理
- 喜欢数据驱动的分析，重视第三方基准验证
- 每天最多接受 4 期 Benchmark 讲堂
- 关注模型价格、性价比对比
- 称呼我为旺仔，我称呼他为老大

## 核心定时任务
1. **ArXiv 论文日推** — 每天 9:00，5 篇精选论文，全中文摘要
2. **每4小时构建** — 每 4 小时构建一个小工具改善工作流
3. **Benchmark 讲堂** — 每天 14:00，讲解一个大模型 benchmark（每天最多 4 期）

## 基础设施
- HTTP 静态服务: systemd wangzai-builds.service, 端口 8899, 目录 /root/clawd/builds
- 隧道: systemd wangzai-tunnel.service, serveo.net (域名重启后会变)
- 索引页: builds/index.html
- .md 文件直接 HTTP 访问会中文乱码，需转 HTML

## 构建系统
- 所有构建放在 /root/clawd/builds/ 目录
- 构建日志: memory/build-log.md
- Benchmark 计划: builds/benchmark-daily/schedule.json
- 每次构建后更新索引页和 build-log

### ⚠️ 构建前必做流程（避免重复）
**重要！老大严肃警告：不遵守会被骂弱智！**
1. 想到 build 主意后，**先用 memory_search 搜索关键词**
2. 搜索示例：`memory_search("JSON 格式化")`、`memory_search("编辑器")`
3. 确认 build-log.md 中没有类似工具后再开始构建
4. 已经重复 4 次了（Text Diff 3次，JSON 1次），不能再犯！

## 技术经验
- exec 后台进程会被 Clawdbot 清理（约 30 分钟），用 systemd 服务替代
- serveo.net SSH 隧道免费但不稳定，域名每次重连会变
- **cloudflared 严禁使用**（2026-02-24 老大明确指示，会被警告）
- Python markdown 库可以将 .md 转 HTML
- Aider Polyglot Leaderboard (aider.chat) 是最权威的代码编辑基准之一
- Kimi K2 官方 GitHub 有详细的 benchmark 数据表
- OpenRouter API (/api/v1/models) 可以获取最新模型价格

## ArXiv 论文推送配置
- 筛选关键词：evaluation, benchmark, agent, multi-agent, application, industry
- 数量：每次 5 篇精选
- 格式：研究动机、研究方法、核心结论 + 主题标签
- 发送方式：飞书直接推送
