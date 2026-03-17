#!/usr/bin/env python3
"""
Daily Report Generator
自动生成每日工作报告，汇总今天的所有任务、build、推送等
"""

import os
import json
from datetime import datetime
from pathlib import Path

def read_today_memory():
    """读取今天的memory文件"""
    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = Path(f"../../memory/{today}.md")
    
    if not memory_file.exists():
        return None, today
    
    content = memory_file.read_text(encoding='utf-8')
    return content, today

def parse_memory_content(content):
    """解析memory内容，提取关键信息"""
    if not content:
        return {
            'builds': [],
            'tasks': [],
            'highlights': []
        }
    
    builds = []
    tasks = []
    highlights = []
    
    lines = content.split('\n')
    current_section = None
    
    for line in lines:
        # 检测build
        if 'Build #' in line and '##' in line:
            builds.append(line.strip('# ').strip())
        
        # 检测任务
        if line.startswith('## ') and ':' in line:
            current_section = line.strip('# ').strip()
            if 'Build' not in current_section:
                tasks.append(current_section)
        
        # 检测完成标记
        if '✅' in line:
            highlights.append(line.strip('- ').strip())
    
    return {
        'builds': builds,
        'tasks': tasks,
        'highlights': highlights[:10]  # 最多10条
    }

def generate_html(date, data):
    """生成HTML报告"""
    
    builds_html = ''
    if data['builds']:
        builds_html = '<div class="section"><h3>🛠️ 今日构建</h3><ul>'
        for build in data['builds']:
            builds_html += f'<li>{build}</li>'
        builds_html += '</ul></div>'
    
    tasks_html = ''
    if data['tasks']:
        tasks_html = '<div class="section"><h3>📋 完成任务</h3><ul>'
        for task in data['tasks']:
            tasks_html += f'<li>{task}</li>'
        tasks_html += '</ul></div>'
    
    highlights_html = ''
    if data['highlights']:
        highlights_html = '<div class="section"><h3>✨ 今日亮点</h3><ul>'
        for highlight in data['highlights']:
            highlights_html += f'<li>{highlight}</li>'
        highlights_html += '</ul></div>'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日工作报告 - {date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .date {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section h3 {{
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .section ul {{
            list-style: none;
            padding: 0;
        }}
        
        .section li {{
            padding: 12px 0;
            padding-left: 30px;
            position: relative;
            line-height: 1.6;
            color: #333;
        }}
        
        .section li:before {{
            content: "▸";
            position: absolute;
            left: 10px;
            color: #667eea;
            font-weight: bold;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            font-size: 1em;
            opacity: 0.9;
        }}
        
        .footer {{
            background: #f9f9f9;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .empty {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 每日工作报告</h1>
            <div class="date">{date}</div>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat-card">
                    <div class="number">{len(data['builds'])}</div>
                    <div class="label">构建完成</div>
                </div>
                <div class="stat-card">
                    <div class="number">{len(data['tasks'])}</div>
                    <div class="label">任务完成</div>
                </div>
                <div class="stat-card">
                    <div class="number">{len(data['highlights'])}</div>
                    <div class="label">今日亮点</div>
                </div>
            </div>
            
            {builds_html if builds_html else '<div class="empty">今天还没有构建记录</div>'}
            {tasks_html if tasks_html else ''}
            {highlights_html if highlights_html else ''}
        </div>
        
        <div class="footer">
            生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 旺仔自动生成
        </div>
    </div>
</body>
</html>'''
    
    return html

def main():
    print("📊 Daily Report Generator")
    print("=" * 50)
    
    # 读取今天的memory
    print("📖 读取今天的memory文件...")
    content, date = read_today_memory()
    
    if not content:
        print(f"⚠️  未找到 {date} 的memory文件")
        data = {'builds': [], 'tasks': [], 'highlights': []}
    else:
        print(f"✅ 找到 {date} 的memory文件")
        
        # 解析内容
        print("🔍 解析memory内容...")
        data = parse_memory_content(content)
        print(f"✅ 找到 {len(data['builds'])} 个构建, {len(data['tasks'])} 个任务, {len(data['highlights'])} 条亮点")
    
    # 生成HTML
    print("🎨 生成HTML报告...")
    html = generate_html(date, data)
    
    # 保存文件
    output_file = Path(f"report-{date}.html")
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ 已生成: {output_file.absolute()}")
    
    print("\n🎉 完成！")
    print(f"📊 统计: {len(data['builds'])} 个构建, {len(data['tasks'])} 个任务")

if __name__ == "__main__":
    main()
