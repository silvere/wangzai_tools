# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

---

## [LRN-20260305-001] correction

**Logged**: 2026-03-05T17:47:38+08:00
**Priority**: high
**Status**: pending
**Area**: tools

### Summary
避免构建重复工具，聚焦真实场景和商业价值

### Details
老大反馈：最近构建的工具出现了重复情况。需要：
1. 严格避免构建重复或相似的工具
2. 让工具更有用、更有价值
3. 贴近真实项目、真实场景
4. 朝可以赚钱的方向发展

### Metadata
- Source: user_feedback
- Tags: tool_building, product_thinking, avoid_duplication

---

## [LRN-20260305-002] correction

**Logged**: 2026-03-05T20:07:51+08:00
**Priority**: critical
**Status**: pending
**Area**: tools

### Summary
【禁止】不再构建任何评测相关的小工具

### Details
老大明确指令：评测相关的小工具都不要做了。
包括但不限于：benchmark对比、评测指标计算、模型评分、prompt测试等一切与大模型评测相关的工具。

### Suggested Action
构建新工具时，完全避开评测方向。转向：
- 内容创作工具（小红书/公众号/社交媒体）
- 自动化工具（浏览器自动化、工作流）
- AI应用（有实际商业价值的）
- 生活/效率工具（非评测类）

### Metadata
- Source: user_feedback
- Tags: tool_building, hard_rule, no_eval_tools

---
