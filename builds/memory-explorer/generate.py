#!/usr/bin/env python3
"""
Memory Explorer Generator
读取所有memory文件，生成可视化浏览界面
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

def read_memory_files():
    """读取所有memory文件"""
    memory_dir = Path("../../memory")
    if not memory_dir.exists():
        return []
    
    memories = []
    for file in sorted(memory_dir.glob("*.md")):
        # 跳过特殊文件
        if file.name in ["build-index.md", "build-log.md", "heartbeat-state.json", "restart-state.md"]:
            continue
        
        # 尝试解析日期
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', file.name)
        if not date_match:
            continue
        
        date_str = date_match.group(1)
        
        try:
            content = file.read_text(encoding='utf-8')
            word_count = len(content)
            
            # 提取关键词（简单实现：提取中文词和英文单词）
            chinese_words = re.findall(r'[\u4e00-\u9fff]+', content)
            english_words = re.findall(r'\b[a-zA-Z]{3,}\b', content)
            
            memories.append({
                'date': date_str,
                'filename': file.name,
                'content': content,
                'word_count': word_count,
                'chinese_words': chinese_words,
                'english_words': english_words
            })
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    return memories

def extract_keywords(memories, top_n=30):
    """提取最常见的关键词"""
    all_chinese = []
    all_english = []
    
    for mem in memories:
        all_chinese.extend(mem['chinese_words'])
        all_english.extend(mem['english_words'])
    
    # 过滤停用词
    stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
    
    chinese_counter = Counter([w for w in all_chinese if len(w) >= 2 and w not in stop_words])
    english_counter = Counter([w.lower() for w in all_english if w.lower() not in stop_words])
    
    keywords = []
    for word, count in chinese_counter.most_common(top_n // 2):
        keywords.append({'word': word, 'count': count, 'type': 'chinese'})
    for word, count in english_counter.most_common(top_n // 2):
        keywords.append({'word': word, 'count': count, 'type': 'english'})
    
    return keywords

def generate_html(memories, keywords):
    """生成HTML文件"""
    
    # 统计信息
    total_days = len(memories)
    total_words = sum(m['word_count'] for m in memories)
    
    # 准备JSON数据（不包含完整内容，太大了）
    memories_data = []
    for mem in memories:
        # 只保留前500字作为预览
        preview = mem['content'][:500] + ('...' if len(mem['content']) > 500 else '')
        memories_data.append({
            'date': mem['date'],
            'filename': mem['filename'],
            'preview': preview,
            'word_count': mem['word_count'],
            'has_more': len(mem['content']) > 500
        })
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Explorer - 记忆浏览器</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .search-box {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }}
        
        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .keywords {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .keywords h3 {{
            margin-bottom: 15px;
            color: #333;
        }}
        
        .keyword-cloud {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .keyword {{
            padding: 6px 12px;
            background: #f0f0f0;
            border-radius: 20px;
            font-size: 0.9em;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .keyword:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }}
        
        .keyword .count {{
            color: #999;
            font-size: 0.8em;
            margin-left: 5px;
        }}
        
        .timeline {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .timeline h3 {{
            margin-bottom: 20px;
            color: #333;
        }}
        
        .memory-item {{
            padding: 15px;
            border-left: 3px solid #667eea;
            margin-bottom: 15px;
            background: #f9f9f9;
            border-radius: 0 8px 8px 0;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .memory-item:hover {{
            background: #f0f0f0;
            transform: translateX(5px);
        }}
        
        .memory-item.hidden {{
            display: none;
        }}
        
        .memory-date {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        .memory-preview {{
            color: #666;
            line-height: 1.6;
            white-space: pre-wrap;
            font-size: 0.9em;
        }}
        
        .memory-meta {{
            margin-top: 10px;
            color: #999;
            font-size: 0.85em;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #999;
            display: none;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            padding: 20px;
            overflow-y: auto;
        }}
        
        .modal-content {{
            background: white;
            max-width: 800px;
            margin: 40px auto;
            padding: 30px;
            border-radius: 12px;
            position: relative;
        }}
        
        .modal-close {{
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 1.5em;
            cursor: pointer;
            color: #999;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.3s;
        }}
        
        .modal-close:hover {{
            background: #f0f0f0;
            color: #333;
        }}
        
        .modal-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        .modal-body {{
            line-height: 1.8;
            color: #333;
            white-space: pre-wrap;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Memory Explorer</h1>
            <div class="subtitle">记忆浏览器 - 可视化你的思维轨迹</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{total_days}</div>
                <div class="label">记忆天数</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_words:,}</div>
                <div class="label">总字数</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_words // total_days if total_days > 0 else 0:,}</div>
                <div class="label">日均字数</div>
            </div>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="🔍 搜索记忆内容...">
        </div>
        
        <div class="keywords">
            <h3>🏷️ 关键词云</h3>
            <div class="keyword-cloud" id="keywordCloud"></div>
        </div>
        
        <div class="timeline">
            <h3>📅 时间线</h3>
            <div id="timelineContent"></div>
            <div class="no-results" id="noResults">没有找到匹配的记忆 😢</div>
        </div>
    </div>
    
    <div class="modal" id="modal">
        <div class="modal-content">
            <div class="modal-close" onclick="closeModal()">×</div>
            <div class="modal-title" id="modalTitle"></div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>
    
    <script>
        const memories = {json.dumps(memories_data, ensure_ascii=False)};
        const keywords = {json.dumps(keywords, ensure_ascii=False)};
        
        // 渲染关键词云
        function renderKeywords() {{
            const cloud = document.getElementById('keywordCloud');
            keywords.forEach(kw => {{
                const tag = document.createElement('div');
                tag.className = 'keyword';
                tag.innerHTML = `${{kw.word}} <span class="count">${{kw.count}}</span>`;
                tag.onclick = () => {{
                    document.getElementById('searchInput').value = kw.word;
                    filterMemories();
                }};
                cloud.appendChild(tag);
            }});
        }}
        
        // 渲染时间线
        function renderTimeline() {{
            const timeline = document.getElementById('timelineContent');
            memories.forEach((mem, index) => {{
                const item = document.createElement('div');
                item.className = 'memory-item';
                item.dataset.index = index;
                item.innerHTML = `
                    <div class="memory-date">${{mem.date}}</div>
                    <div class="memory-preview">${{mem.preview}}</div>
                    <div class="memory-meta">📝 ${{mem.word_count}} 字 ${{mem.has_more ? '· 点击查看完整内容' : ''}}</div>
                `;
                item.onclick = () => showMemory(index);
                timeline.appendChild(item);
            }});
        }}
        
        // 搜索过滤
        function filterMemories() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const items = document.querySelectorAll('.memory-item');
            let visibleCount = 0;
            
            items.forEach(item => {{
                const index = item.dataset.index;
                const mem = memories[index];
                const text = (mem.date + mem.preview).toLowerCase();
                
                if (text.includes(query)) {{
                    item.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    item.classList.add('hidden');
                }}
            }});
            
            document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
        }}
        
        // 显示完整记忆
        function showMemory(index) {{
            const mem = memories[index];
            if (!mem.has_more) return;
            
            document.getElementById('modalTitle').textContent = mem.date;
            document.getElementById('modalBody').textContent = '⚠️ 完整内容需要从原始文件读取\\n\\n文件路径: memory/' + mem.filename + '\\n\\n预览:\\n' + mem.preview;
            document.getElementById('modal').style.display = 'block';
        }}
        
        function closeModal() {{
            document.getElementById('modal').style.display = 'none';
        }}
        
        // 初始化
        renderKeywords();
        renderTimeline();
        
        // 搜索事件
        document.getElementById('searchInput').addEventListener('input', filterMemories);
        
        // 点击模态框外部关闭
        document.getElementById('modal').addEventListener('click', (e) => {{
            if (e.target.id === 'modal') closeModal();
        }});
        
        // ESC键关闭模态框
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    print("🧠 Memory Explorer Generator")
    print("=" * 50)
    
    # 读取记忆文件
    print("📖 读取记忆文件...")
    memories = read_memory_files()
    print(f"✅ 找到 {len(memories)} 个记忆文件")
    
    # 提取关键词
    print("🏷️  提取关键词...")
    keywords = extract_keywords(memories)
    print(f"✅ 提取了 {len(keywords)} 个关键词")
    
    # 生成HTML
    print("🎨 生成HTML...")
    html = generate_html(memories, keywords)
    
    # 保存文件
    output_file = Path("index.html")
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ 已生成: {output_file.absolute()}")
    
    print("\n🎉 完成！")
    print(f"📊 统计: {len(memories)} 天记忆, {sum(m['word_count'] for m in memories):,} 字")

if __name__ == "__main__":
    main()
