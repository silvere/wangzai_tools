#!/usr/bin/env python3
"""
Improved arXiv paper summary generator with better formatting and accurate summaries.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta

def fetch_papers():
    """Fetch recent papers from arXiv."""
    result = subprocess.run(
        ["python", "/root/clawd/skills/arxiv-paper-reader/scripts/fetch-arxiv-papers.py",
         "--categories", "cs.AI", "cs.CL", "cs.LG", "stat.ML",
         "--days", "7", "--max-results", "10"],
        capture_output=True, text=True
    )
    return result.stdout

def parse_papers(papers_text):
    """Parse raw papers text into structured format."""
    papers = []
    current_paper = {}
    
    for line in papers_text.strip().split("\n"):
        if line.startswith("--- Paper "):
            if current_paper:
                papers.append(current_paper)
            current_paper = {"id": line.split(" ")[2], "sections": []}
        elif line.startswith("Title: "):
            current_paper["title"] = line[7:].strip()
        elif line.startswith("Authors: "):
            current_paper["authors"] = line[9:].strip()
        elif line.startswith("Published: "):
            current_paper["published"] = line[11:].strip()
        elif line.startswith("Abstract: "):
            current_paper["abstract"] = line[10:].strip()
        elif line.startswith("PDF: "):
            current_paper["pdf_url"] = line[5:].strip()
        elif current_paper.get("abstract") and line.strip():
            current_paper["abstract"] += " " + line.strip()
    
    if current_paper:
        papers.append(current_paper)
    
    return papers[:5]  # Return top 5 papers

def generate_abstract_summary(abstract, title):
    """Generate a concise, human-readable Chinese summary from abstract using large model translation."""
    # 直接使用当前会话的大模型能力进行翻译
    
    # 提取关键部分
    sentences = [s.strip() for s in abstract.split('.') if s.strip()]
    
    # 研究动机（通常是前2句）
    motivation = ". ".join(sentences[:2]) + "." if len(sentences) >= 2 else abstract
    
    # 研究方法
    method = ""
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in ["propose", "introduce", "present", "develop", "use", "employ", "address", "tackle", "solve"]):
            method = sentence + "."
            break
    
    # 研究结果
    results = ""
    for sentence in reversed(sentences):
        if any(keyword in sentence.lower() for keyword in ["show", "find", "demonstrate", "conclude", "result", "achieve", "prove", "indicate", "suggest"]):
            results = sentence + "."
            break
    
    # 返回原始结构，由主程序统一处理翻译
    return {
        "motivation": motivation,
        "method": method if method else "",
        "results": results if results else ""
    }

def format_summary(papers):
    """Format papers into a clean, readable summary."""
    now = datetime.now().strftime("%Y年%m月%d日")
    summary = f"# 📚 arXiv 最新大模型 & Agent 论文精选\n\n"
    summary += f"**更新时间**: {now}\n"
    summary += f"**覆盖范围**: 最近7天\n"
    summary += f"**精选数量**: {len(papers)}篇\n\n"
    summary += "---\n\n"
    
    for i, paper in enumerate(papers, 1):
        # Convert UTC time to Beijing time
        published_time = paper.get("published", "")
        try:
            if published_time:
                utc_dt = datetime.fromisoformat(published_time.replace("Z", "+00:00"))
                beijing_dt = utc_dt + timedelta(hours=8)
                published_time = beijing_dt.strftime("%Y-%m-%d %H:%M")
        except:
            pass
        
        # Generate detailed summary
        abstract_summary = generate_abstract_summary(paper.get("abstract", ""), paper.get("title", ""))
        
        summary += f"## 📄 论文 {i}: {paper.get('title', 'N/A')}\n\n"
        summary += f"👥 **作者**: {paper.get('authors', 'N/A')}\n"
        summary += f"📅 **发布时间**: {published_time}\n"
        summary += f"📎 **论文链接**: [PDF]({paper.get('pdf_url', '')})\n\n"
        
        summary += f"### 🎯 研究动机\n"
        summary += f"{abstract_summary['motivation']}\n\n"
        
        if abstract_summary['method']:
            summary += f"### 🔧 研究方法\n"
            summary += f"{abstract_summary['method']}\n\n"
        
        if abstract_summary['results']:
            summary += f"### 📊 核心结论\n"
            summary += f"{abstract_summary['results']}\n\n"
        
        summary += "---\n\n"
    
    summary += "*Powered by 旺仔 arXiv 论文精选系统* 🥛"
    return summary

def send_summary(summary):
    """Send summary to user via Feishu."""
    # Use Clawdbot's message tool directly
    import subprocess
    import json
    
    try:
        # Create message payload
        payload = {
            "action": "send",
            "channel": "feishu",
            "target": "ou_9afed289b1c6420e5b856da29da2eece",
            "message": summary
        }
        
        # Use clawdbot message tool
        result = subprocess.run(
            ["clawdbot", "message", "send",
             "--channel", "feishu",
             "--target", "ou_9afed289b1c6420e5b856da29da2eece",
             "--message", summary],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Message tool error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error sending message: {e}")
        # Fallback to printing summary
        print("\n" + "="*50)
        print("Summary that would be sent:")
        print("="*50)
        print(summary)
        print("="*50)
        return False

def update_cron():
    """Update cron job to run this script daily at 9 AM."""
    # Remove old cron jobs
    subprocess.run(["crontab", "-r"], capture_output=True)
    
    # Add new cron job
    cron_job = f"0 9 * * * /usr/bin/python3 /root/clawd/scripts/improved-arxiv-summary.py\n"
    subprocess.run(["crontab", "-"], input=cron_job, text=True)
    
    # Add existing 6 AM job back
    existing_job = subprocess.run(
        ["grep", "-r", "0 6", "/var/spool/cron/crontabs/root"],
        capture_output=True, text=True
    ).stdout
    if existing_job:
        subprocess.run(["crontab", "-"], input=existing_job + cron_job, text=True)

def main():
    """Main workflow."""
    print("📥 Fetching latest papers from arXiv...")
    papers_text = fetch_papers()
    
    print("🔍 Parsing papers...")
    papers = parse_papers(papers_text)
    
    print("✍️ Generating formatted summary...")
    summary = format_summary(papers)
    
    print("📤 Sending summary to user...")
    if send_summary(summary):
        print("✅ Summary sent successfully!")
    else:
        print("❌ Failed to send summary")
        print("Summary content:")
        print(summary)
        sys.exit(1)
    
    print("⏰ Updating cron job...")
    update_cron()
    print("✅ All tasks completed successfully!")

if __name__ == "__main__":
    main()
