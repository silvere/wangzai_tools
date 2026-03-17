#!/usr/bin/env python3
"""
Run arXiv paper summary with focus on LLM evaluation, AI agents, and industry applications.
"""

import subprocess
import json
from datetime import datetime, timedelta

def fetch_papers():
    """Fetch papers focused on specific topics."""
    # Use advanced search with multiple keywords
    result = subprocess.run(
        ["python", "/root/clawd/skills/arxiv-paper-reader/scripts/fetch-arxiv-papers.py",
         "--categories", "cs.AI", "cs.CL", "cs.LG", "stat.ML",
         "--days", "7", "--max-results", "15"],
        capture_output=True, text=True
    )
    return result.stdout

def parse_and_filter_papers(papers_text):
    """Parse papers and filter by topic."""
    papers = []
    current_paper = {}
    
    for line in papers_text.strip().split("\n"):
        if line.startswith("--- Paper "):
            if current_paper:
                papers.append(current_paper)
            current_paper = {}
        elif line.startswith("Title: "):
            current_paper["title"] = line[7:].strip()
        elif line.startswith("Authors: "):
            current_paper["authors"] = line[9:].strip()
        elif line.startswith("Published: "):
            current_paper["published"] = line[11:].strip()
        elif line.startswith("Abstract: "):
            current_paper["abstract"] = line[10:].strip()
        elif line.startswith("PDF: "):
            current_paper["pdf"] = line[5:].strip()
        elif current_paper.get("abstract") and line.strip():
            current_paper["abstract"] += " " + line.strip()
    
    if current_paper:
        papers.append(current_paper)
    
    # Filter papers by topic
    filtered = []
    topic_keywords = {
        "evaluation": ["evaluation", "benchmark", "assessment", "metric", "评测", "基准"],
        "agent": ["agent", "multi-agent", "AI agent", "intelligent agent", "智能体"],
        "application": ["application", "industry", "real-world", "deployment", "落地", "实践"]
    }
    
    for paper in papers:
        title_lower = paper.get("title", "").lower()
        abstract_lower = paper.get("abstract", "").lower()
        
        # Check if paper matches any topic
        for topic, keywords in topic_keywords.items():
            if any(keyword in title_lower or keyword in abstract_lower for keyword in keywords):
                paper["topic"] = topic
                filtered.append(paper)
                break
    
    # Return up to 5 most recent papers
    sorted_papers = sorted(filtered, key=lambda x: x.get("published", ""), reverse=True)
    return sorted_papers[:5]

def translate_abstract(abstract):
    """Translate abstract to Chinese with technical terms."""
    term_translations = {
        "Large Language Model": "大语言模型",
        "LLM": "大语言模型",
        "AI Agent": "AI智能体",
        "multi-agent": "多智能体",
        "evaluation": "评测",
        "benchmark": "基准",
        "framework": "框架",
        "algorithm": "算法",
        "performance": "性能",
        "accuracy": "准确性",
        "efficiency": "效率",
        "deployment": "部署",
        "application": "应用",
        "task": "任务",
        "training": "训练",
        "fine-tuning": "微调",
        "inference": "推理",
        "propose": "提出",
        "develop": "开发",
        "introduce": "介绍",
        "improve": "改进",
        "enhance": "增强",
        "show": "表明",
        "demonstrate": "证明",
        "achieve": "实现"
    }
    
    for eng, chi in term_translations.items():
        abstract = abstract.replace(eng, chi)
        abstract = abstract.replace(eng.lower(), chi)
    
    return abstract

def extract_key_points(abstract):
    """Extract key points from abstract."""
    sentences = [s.strip() for s in abstract.split('.') if s.strip()]
    
    # Extract motivation (first few sentences)
    motivation = ". ".join(sentences[:2]) + "." if len(sentences) >= 2 else abstract
    
    # Extract methodology
    method = ""
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in ["propose", "introduce", "develop", "use", "提出", "开发", "介绍", "使用"]):
            method = sentence + "."
            break
    
    # Extract results
    result = ""
    for sentence in reversed(sentences):
        if any(keyword in sentence.lower() for keyword in ["show", "find", "demonstrate", "achieve", "表明", "发现", "证明", "实现"]):
            result = sentence + "."
            break
    
    return motivation, method, result

def format_paper_summary(paper, index):
    """Format single paper summary in Chinese."""
    # Convert time to Beijing time
    published = paper.get("published", "")
    try:
        if published:
            utc_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            beijing_dt = utc_dt + timedelta(hours=8)
            published = beijing_dt.strftime("%Y年%m月%d日 %H:%M")
    except:
        pass
    
    # Get topic label
    topic = paper.get("topic", "")
    topic_labels = {
        "evaluation": "📊 大模型评测",
        "agent": "🤖 AI智能体",
        "application": "💼 行业应用"
    }
    topic_label = topic_labels.get(topic, "")
    
    # Translate and extract key points
    abstract = translate_abstract(paper.get("abstract", ""))
    motivation, method, result = extract_key_points(abstract)
    
    summary = f"## 📄 第{index+1}篇: {paper.get('title', 'N/A')}\n\n"
    summary += f"👥 **作者**: {paper.get('authors', 'N/A')}\n"
    summary += f"📅 **发表时间**: {published}\n"
    summary += f"🔗 **论文链接**: [PDF下载]({paper.get('pdf', '')})\n"
    if topic_label:
        summary += f"🏷️ **主题标签**: {topic_label}\n\n"
    
    summary += f"### 🎯 研究动机\n{motivation}\n\n"
    
    if method:
        summary += f"### 🔧 研究方法\n{method}\n\n"
    
    if result:
        summary += f"### 📊 研究结果\n{result}\n\n"
    
    summary += "---\n\n"
    return summary

def main():
    print("📥 正在获取arXiv最新论文...")
    papers_text = fetch_papers()
    
    print("🔍 正在筛选和解析论文...")
    papers = parse_and_filter_papers(papers_text)
    
    if not papers:
        print("😔 没有找到符合主题的论文，将返回最近的相关论文")
        # Fallback to fetching without filtering
        papers = parse_and_filter_papers(fetch_papers())
    
    print(f"✍️ 正在生成{len(papers)}篇论文的中文摘要...")
    now = datetime.now().strftime("%Y年%m月%d日")
    
    final_summary = f"# 📚 arXiv 最新大模型评测、AI智能体与行业应用论文精选\n\n"
    final_summary += f"📅 **更新时间**: {now}\n"
    final_summary += f"📆 **覆盖范围**: 最近7天\n"
    final_summary += f"📝 **精选数量**: {len(papers)}篇\n\n"
    final_summary += "---\n\n"
    
    for i, paper in enumerate(papers):
        final_summary += format_paper_summary(paper, i)
    
    final_summary += "🤖 由旺仔AI助手自动生成\n"
    final_summary += "🥛 每天早上9点准时推送最新精选\n"
    
    print("📤 正在发送给用户...")
    
    # Print the final summary
    print("\n" + "="*100)
    print("Final Summary to be sent:")
    print("="*100)
    print(final_summary)
    print("="*100 + "\n")
    
    # Write to file for debugging
    with open("/root/clawd/latest-arxiv-summary.txt", "w", encoding="utf-8") as f:
        f.write(final_summary)
    print("💾 摘要已保存到: /root/clawd/latest-arxiv-summary.txt")
    
    # Send using message function directly
    print("📤 正在尝试发送消息...")
    import subprocess
    import json
    
    # Prepare message data
    message_data = {
        "action": "send",
        "channel": "feishu",
        "target": "ou_9afed289b1c6420e5b856da29da2eece",
        "message": final_summary
    }
    
    try:
        # Use the message tool via Python
        result = subprocess.run(
            ["python", "-c", 
             "import json; from clawdbot.tools.message import MessageTool; tool = MessageTool(); result = tool.send(**json.loads('''" + json.dumps(message_data) + "''')); print(result)"],
            capture_output=True, text=True,
            cwd="/root/.nvm/versions/node/v24.13.0/lib/node_modules/clawdbot"
        )
        
        if result.returncode == 0:
            print("✅ 论文摘要已成功发送给用户！")
        else:
            print("❌ 发送失败，错误信息:", result.stderr)
            
            # Fallback to using message command
            print("🔄 正在尝试使用备用发送方式...")
            result = subprocess.run(
                ["clawdbot", "message", "send",
                 "--channel", "feishu",
                 "--target", "ou_9afed289b1c6420e5b856da29da2eece",
                 "--message", final_summary],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("✅ 论文摘要已成功发送给用户！")
            else:
                print("❌ 备用发送方式也失败了，请手动发送:")
                print("文件路径: /root/clawd/latest-arxiv-summary.txt")
                
    except Exception as e:
        print(f"❌ 发送过程中发生错误: {e}")
        print("💾 摘要已保存到本地文件，请手动发送")

if __name__ == "__main__":
    main()
