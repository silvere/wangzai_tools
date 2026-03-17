# EvalHub 评测工坊

LLM 评测 SaaS 平台 — 标准化评测，量化对比，一键报告。

## 功能
- 添加模型 API（OpenAI 兼容格式）
- 内置评测集（TruthfulQA、MMLU 子集等）
- 自动运行评测任务
- 可视化对比报告

## 技术栈
- 后端: FastAPI + SQLite
- 前端: HTML/JS + Chart.js
- 评测引擎: Python async

## 运行
```bash
cd backend
pip install -r ../requirements.txt
python main.py
```

## 版本记录
- V0.1 (2026-02-21) — 项目骨架，基础评测流程
