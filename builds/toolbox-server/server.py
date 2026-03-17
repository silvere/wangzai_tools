#!/usr/bin/env python3
"""
OpenClaw 工具站静态文件服务器
提供所有已构建工具的HTTP访问服务
"""

import http.server
import socketserver
import os
import json
import time
from pathlib import Path

# 配置
PORT = 8000
BUILD_DIR = Path(__file__).parent.parent.resolve()
TOOLBOX_INDEX = BUILD_DIR / "toolbox" / "index.html"
BUILD_LOG = BUILD_DIR.parent / "memory" / "build-log.md"

class ToolboxHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BUILD_DIR, **kwargs)
    
    def end_headers(self):
        # 添加CORS头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理OPTIONS请求
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        # 根路径重定向到工具百宝箱首页
        if self.path == '/':
            self.path = '/toolbox/index.html'
        
        # API端点：获取工具列表
        elif self.path == '/api/tools':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            tools = self._scan_tools()
            self.wfile.write(json.dumps(tools, ensure_ascii=False, indent=2).encode('utf-8'))
            return
        
        # API端点：获取构建日志
        elif self.path == '/api/build-log':
            self.send_response(200)
            self.send_header('Content-Type', 'text/markdown; charset=utf-8')
            self.end_headers()
            
            if BUILD_LOG.exists():
                with open(BUILD_LOG, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.wfile.write(b'# Build Log\n\nNo build log found.')
            return
        
        super().do_GET()
    
    def _scan_tools(self):
        """扫描所有已构建的工具"""
        tools = []
        
        # 扫描build-*目录
        for build_dir in BUILD_DIR.glob("build-*"):
            if not build_dir.is_dir():
                continue
            
            index_file = build_dir / "index.html"
            if not index_file.exists():
                continue
            
            # 提取build编号和名称
            dir_name = build_dir.name
            build_num = dir_name.split('-')[1] if len(dir_name.split('-')) >= 2 else 'Unknown'
            
            # 尝试从build-log.md获取工具信息
            tool_info = self._get_tool_info_from_log(build_num)
            
            tools.append({
                "id": dir_name,
                "build_num": build_num,
                "name": tool_info.get("name", dir_name.replace("build-", "").replace("-", " ").title()),
                "description": tool_info.get("description", ""),
                "path": f"/{dir_name}/index.html",
                "local_path": str(index_file),
                "category": tool_info.get("category", "未分类"),
                "built_at": tool_info.get("date", ""),
                "icon": tool_info.get("icon", "🔧")
            })
        
        # 按build编号降序排列
        tools.sort(key=lambda x: int(x["build_num"]) if x["build_num"].isdigit() else 0, reverse=True)
        
        return tools
    
    def _get_tool_info_from_log(self, build_num):
        """从构建日志中获取工具信息"""
        if not BUILD_LOG.exists():
            return {}
        
        try:
            with open(BUILD_LOG, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找对应build的信息
            lines = content.split('\n')
            current_build = None
            info = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith(f"## Build #{build_num} — "):
                    # 提取名称和图标
                    title_part = line.split(f"## Build #{build_num} — ")[1].strip()
                    if " " in title_part:
                        # 分离图标和名称
                        info["icon"] = title_part.split(" ")[-1]
                        info["name"] = " ".join(title_part.split(" ")[:-1])
                    else:
                        info["name"] = title_part
                        info["icon"] = "🔧"
                    current_build = build_num
                elif current_build == build_num and line.startswith("- **日期**:"):
                    info["date"] = line.split("**日期**:")[1].strip()
                elif current_build == build_num and line.startswith("- **描述**:"):
                    info["description"] = line.split("**描述**:")[1].strip()
                elif current_build == build_num and line.startswith("- **技术栈**:"):
                    info["tech_stack"] = line.split("**技术栈**:")[1].strip()
                elif current_build == build_num and line.startswith("- **商业价值**:"):
                    info["value"] = line.split("**商业价值**:")[1].strip()
                elif current_build and line.startswith("## Build #"):
                    # 遇到下一个build，停止
                    break
            
            return info
        except Exception as e:
            print(f"Error parsing build log: {e}")
            return {}

def get_server_info():
    """获取服务器信息"""
    import socket
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    return {
        "port": PORT,
        "hostname": hostname,
        "ip_address": ip_address,
        "local_url": f"http://localhost:{PORT}",
        "lan_url": f"http://{ip_address}:{PORT}",
        "toolbox_url": f"http://{ip_address}:{PORT}/toolbox/index.html"
    }

def main():
    # 确保工具百宝箱首页存在
    if not TOOLBOX_INDEX.exists():
        print(f"Warning: Toolbox index not found at {TOOLBOX_INDEX}")
    
    # 启动服务器
    with socketserver.TCPServer(("", PORT), ToolboxHTTPRequestHandler) as httpd:
        info = get_server_info()
        
        print("\n🚀 OpenClaw 工具站服务已启动！")
        print("=" * 50)
        print(f"本地访问地址: {info['local_url']}")
        print(f"局域网访问地址: {info['lan_url']}")
        print(f"工具百宝箱首页: {info['toolbox_url']}")
        print(f"服务端口: {PORT}")
        print(f"服务目录: {BUILD_DIR}")
        print("=" * 50)
        print("按 Ctrl+C 停止服务\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ 服务已停止")
            httpd.shutdown()

if __name__ == "__main__":
    main()