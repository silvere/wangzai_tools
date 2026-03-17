#!/usr/bin/env python3
"""
每日复盘助手 - Daily Review Assistant
帮助用户回顾一天的工作、学习和生活，并给出改进建议
"""

import os
import sys
from datetime import datetime
import json

def read_today_memory():
    """读取今天的记忆文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = f"/root/clawd/memory/{today}.md"
    
    if not os.path.exists(memory_file):
        return None
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        return f.read()

def read_long_term_memory():
    """读取长期记忆"""
    memory_file = "/root/clawd/MEMORY.md"
    
    if not os.path.exists(memory_file):
        return None
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        return f.read()

def analyze_day(content):
    """分析今天的内容"""
    analysis = {
        "completed_tasks": [],
        "time_spent": {},
        "achievements": [],
        "challenges": [],
        "learnings": []
    }
    
    lines = content.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 识别时间标记
        if line.startswith('##') and ':' in line:
            current_section = line
            
        # 识别任务完成
        if '完成' in line or '✅' in line or 'Build #' in line:
            analysis["completed_tasks"].append(line)
            
        # 识别成就
        if '成功' in line or '突破' in line or '优化' in line:
            analysis["achievements"].append(line)
    
    return analysis

def generate_review(analysis, today_content, long_term_memory):
    """生成复盘报告"""
    review = f"""# 📊 每日复盘 - {datetime.now().strftime("%Y-%m-%d")}

## 今日概览

**完成任务数**: {len(analysis['completed_tasks'])}
**主要成就**: {len(analysis['achievements'])} 项

## 今日亮点

"""
    
    if analysis['completed_tasks']:
        review += "### ✅ 完成的任务\n"
        for task in analysis['completed_tasks'][:5]:  # 只显示前5个
            review += f"- {task}\n"
        review += "\n"
    
    if analysis['achievements']:
        review += "### 🎯 今日成就\n"
        for achievement in analysis['achievements'][:3]:
            review += f"- {achievement}\n"
        review += "\n"
    
    # 添加反思问题
    review += """## 🤔 反思问题

1. **今天最有价值的事情是什么？**
   - 

2. **今天遇到的最大挑战是什么？如何解决的？**
   - 

3. **今天学到了什么新知识或技能？**
   - 

4. **明天最重要的3件事是什么？**
   - 
   - 
   - 

5. **有什么需要改进的地方？**
   - 

## 💡 AI 建议

"""
    
    # 基于内容给出建议
    if len(analysis['completed_tasks']) > 10:
        review += "- ✨ 今天完成了很多任务，效率很高！但要注意不要过度劳累。\n"
    elif len(analysis['completed_tasks']) < 3:
        review += "- 💪 今天完成的任务较少，明天可以设定更明确的目标。\n"
    
    if 'Build #' in today_content:
        review += "- 🛠️ 持续构建工具很好，但要确保工具真正有价值，而不是为了做而做。\n"
    
    if '评测' in today_content or 'Benchmark' in today_content:
        review += "- 📊 评测工作进展顺利，可以考虑总结一些方法论和最佳实践。\n"
    
    review += """
## 📝 行动计划

明天的优先级：
1. [ ] 
2. [ ] 
3. [ ] 

本周目标进度：
- [ ] 

---

*这份复盘由 AI 助手生成，请根据实际情况补充和修改*
"""
    
    return review

def save_review(review):
    """保存复盘报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    review_dir = "/root/clawd/memory/reviews"
    
    if not os.path.exists(review_dir):
        os.makedirs(review_dir)
    
    review_file = f"{review_dir}/{today}-review.md"
    
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write(review)
    
    return review_file

def main():
    print("🔍 正在读取今天的记忆...")
    today_content = read_today_memory()
    
    if not today_content:
        print("❌ 今天还没有记录任何内容")
        return
    
    print("📖 正在读取长期记忆...")
    long_term_memory = read_long_term_memory()
    
    print("🧠 正在分析今天的活动...")
    analysis = analyze_day(today_content)
    
    print("✍️ 正在生成复盘报告...")
    review = generate_review(analysis, today_content, long_term_memory)
    
    print("💾 正在保存复盘报告...")
    review_file = save_review(review)
    
    print(f"\n✅ 复盘报告已生成：{review_file}\n")
    print("=" * 60)
    print(review)
    print("=" * 60)
    
    return review_file

if __name__ == "__main__":
    main()
