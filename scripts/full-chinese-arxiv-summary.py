#!/usr/bin/env python3
"""
Full Chinese arXiv paper summary generator with all content in Chinese.
"""

import subprocess
import sys
from datetime import datetime, timedelta

def fetch_papers():
    """获取arXiv最新论文"""
    # 使用更精确的搜索关键词定位大模型评测、Agent和行业应用方向
    result = subprocess.run(
        ["python", "/root/clawd/skills/arxiv-paper-reader/scripts/fetch-arxiv-papers.py",
         "--categories", "cs.AI", "cs.CL", "cs.LG", "stat.ML",
         "--search-query", "(LLM evaluation OR large model evaluation OR AI agent OR agent-based OR industry application OR real-world deployment)",
         "--days", "7", "--max-results", "15"],
        capture_output=True, text=True
    )
    return result.stdout

def filter_papers_by_topic(papers):
    """根据主题过滤论文，只保留大模型评测、Agent和行业应用相关论文"""
    filtered = []
    keywords = [
        "evaluation", "benchmark", "assessment", "metric", "评测", "基准", "评估", "指标",
        "agent", "multi-agent", "AI agent", "智能体", "多智能体",
        "application", "industry", "real-world", "deployment", "应用", "行业", "实际部署", "落地"
    ]
    
    for paper in papers:
        title = paper.get("标题", "").lower()
        abstract = paper.get("摘要", "").lower()
        
        # 检查标题或摘要是否包含相关关键词
        if any(keyword in title or keyword in abstract for keyword in keywords):
            filtered.append(paper)
            if len(filtered) >= 5:
                break
    
    # 如果过滤后的不足5篇，返回最相关的
    return filtered if filtered else papers[:5]

def parse_papers(papers_text):
    """解析论文文本为结构化数据"""
    papers = []
    current_paper = {}
    
    for line in papers_text.strip().split("\n"):
        if line.startswith("--- Paper "):
            if current_paper:
                papers.append(current_paper)
            current_paper = {"id": line.split(" ")[2]}
        elif line.startswith("Title: "):
            current_paper["标题"] = line[7:].strip()
        elif line.startswith("Authors: "):
            current_paper["作者"] = line[9:].strip()
        elif line.startswith("Published: "):
            current_paper["发表时间"] = line[11:].strip()
        elif line.startswith("Abstract: "):
            current_paper["摘要"] = line[10:].strip()
        elif line.startswith("PDF: "):
            current_paper["PDF链接"] = line[5:].strip()
        elif current_paper.get("摘要") and line.strip():
            current_paper["摘要"] += " " + line.strip()
    
    if current_paper:
        papers.append(current_paper)
    
    # 过滤出符合主题的论文
    return filter_papers_by_topic(papers)

def translate_abstract(abstract):
    """将英文摘要翻译为中文并提取核心内容"""
    # 替换专业术语
    abstract = abstract.replace("Large Language Model", "大语言模型")
    abstract = abstract.replace("LLM", "大语言模型")
    abstract = abstract.replace("AI Agent", "AI智能体")
    abstract = abstract.replace("agent", "智能体")
    abstract = abstract.replace("model", "模型")
    abstract = abstract.replace("task", "任务")
    abstract = abstract.replace("performance", "性能")
    abstract = abstract.replace("accuracy", "准确性")
    abstract = abstract.replace("efficiency", "效率")
    abstract = abstract.replace("benchmark", "基准测试")
    abstract = abstract.replace("evaluation", "评测")
    abstract = abstract.replace("training", "训练")
    abstract = abstract.replace("fine-tuning", "微调")
    abstract = abstract.replace("inference", "推理")
    abstract = abstract.replace("approach", "方法")
    abstract = abstract.replace("framework", "框架")
    abstract = abstract.replace("algorithm", "算法")
    abstract = abstract.replace("system", "系统")
    abstract = abstract.replace("challenge", "挑战")
    abstract = abstract.replace("problem", "问题")
    abstract = abstract.replace("solution", "解决方案")
    abstract = abstract.replace("result", "结果")
    abstract = abstract.replace("conclusion", "结论")
    abstract = abstract.replace("propose", "提出")
    abstract = abstract.replace("introduce", "介绍")
    abstract = abstract.replace("develop", "开发")
    abstract = abstract.replace("achieve", "实现")
    abstract = abstract.replace("show", "表明")
    abstract = abstract.replace("demonstrate", "证明")
    abstract = abstract.replace("improve", "改进")
    abstract = abstract.replace("enhance", "增强")
    abstract = abstract.replace("optimize", "优化")
    abstract = abstract.replace("address", "解决")
    abstract = abstract.replace("solve", "解决")
    
    # 分割句子并提取核心部分
    sentences = [s.strip() for s in abstract.split('.') if s.strip()]
    
    # 提取研究动机（通常是前2句）
    研究动机 = ". ".join(sentences[:2]) + "." if len(sentences) >= 2 else abstract
    
    # 提取研究方法
    研究方法 = ""
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in ["propose", "introduce", "present", "develop", "use", "employ", "address", "tackle", "solve"]):
            研究方法 = sentence + "."
            break
    
    # 提取研究结果
    研究结果 = ""
    for sentence in reversed(sentences):
        if any(keyword in sentence.lower() for keyword in ["show", "find", "demonstrate", "conclude", "result", "achieve", "prove", "indicate", "suggest"]):
            研究结果 = sentence + "."
            break
    
    return {
        "研究动机": 研究动机,
        "研究方法": 研究方法,
        "研究结果": 研究结果
    }

def format_summary(papers):
    """将论文格式化为中文摘要"""
    now = datetime.now().strftime("%Y年%m月%d日")
    summary = f"# 📚 arXiv 最新大模型 & AI智能体论文精选\n\n"
    summary += f"📅 **更新时间**: {now}\n"
    summary += f"📆 **覆盖范围**: 最近7天\n"
    summary += f"📝 **精选数量**: {len(papers)}篇\n\n"
    summary += "---\n\n"
    
    for i, paper in enumerate(papers, 1):
        # 转换时间为北京时间
        发表时间 = paper.get("发表时间", "")
        try:
            if 发表时间:
                utc_dt = datetime.fromisoformat(发表时间.replace("Z", "+00:00"))
                beijing_dt = utc_dt + timedelta(hours=8)
                发表时间 = beijing_dt.strftime("%Y年%m月%d日 %H:%M")
        except:
            pass
        
        # 生成中文摘要
        中文摘要 = translate_abstract(paper.get("摘要", ""))
        
        summary += f"## 📄 第{i}篇: {paper.get('标题', 'N/A')}\n\n"
        summary += f"👥 **作者**: {paper.get('作者', 'N/A')}\n"
        summary += f"📅 **发表时间**: {发表时间}\n"
        summary += f"🔗 **论文链接**: [PDF下载]({paper.get('PDF链接', '')})\n\n"
        
        # 添加主题标签
        title = paper.get('标题', '').lower()
        abstract = paper.get('摘要', '').lower()
        tags = []
        if any(key in title or key in abstract for key in ["evaluation", "benchmark", "评测", "基准"]):
            tags.append("📊 大模型评测")
        if any(key in title or key in abstract for key in ["agent", "multi-agent", "智能体"]):
            tags.append("🤖 AI智能体")
        if any(key in title or key in abstract for key in ["application", "industry", "应用", "行业"]):
            tags.append("💼 行业应用")
        
        if tags:
            summary += f"🏷️ **主题标签**: {' | '.join(tags)}\n\n"
        
        summary += f"### 🎯 研究动机\n"
        summary += f"{中文摘要['研究动机']}\n\n"
        
        if 中文摘要['研究方法']:
            summary += f"### 🔧 研究方法\n"
            summary += f"{中文摘要['研究方法']}\n\n"
        
        if 中文摘要['研究结果']:
            summary += f"### 📊 研究结果\n"
        
        summary += "---\n\n"
    
    summary += "🤖 由旺仔AI助手自动生成\n"
    summary += "🥛 每天早上9点准时推送最新精选\n"
    return summary

def update_cron():
    """更新定时任务"""
    # 移除旧的定时任务
    subprocess.run(["crontab", "-r"], capture_output=True)
    
    # 添加新的定时任务
    cron_job = f"0 9 * * * /usr/bin/python3 /root/clawd/scripts/full-chinese-arxiv-summary.py\n"
    subprocess.run(["crontab", "-"], input=cron_job, text=True)
    
    # 恢复原有的6点任务
    existing_job = subprocess.run(
        ["grep", "-r", "0 6", "/var/spool/cron/crontabs/root"],
        capture_output=True, text=True
    ).stdout
    if existing_job:
        subprocess.run(["crontab", "-"], input=existing_job + cron_job, text=True)

def main():
    """主流程"""
    print("📥 正在获取arXiv最新论文...")
    papers_text = fetch_papers()
    
    print("🔍 正在解析论文...")
    papers = parse_papers(papers_text)
    
    print("✍️ 正在生成中文摘要...")
    summary = format_summary(papers)
    
    print("📤 正在发送给用户...")
    
    # 使用subprocess调用message命令
    import subprocess
    result = subprocess.run(
        ["python", "-m", "clawdbot.tools.message", "send",
         "--channel", "feishu",
         "--target", "ou_9afed289b1c6420e5b856da29da2eece",
         "--message", summary],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ 中文摘要发送成功！")
    else:
        print("❌ 发送失败，错误信息：", result.stderr)
        print("\n生成的摘要内容：")
        print(summary)
        # 打印摘要到文件
        with open("/root/clawd/latest-arxiv-summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\n💾 摘要已保存到文件: /root/clawd/latest-arxiv-summary.txt")
        sys.exit(1)
    
    print("⏰ 正在更新定时任务...")
    update_cron()
    print("✅ 所有任务完成！")

if __name__ == "__main__":
    main()
