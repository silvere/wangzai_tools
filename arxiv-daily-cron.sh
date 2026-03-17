#!/bin/bash

# 运行arXiv论文获取和摘要生成
cd /root/clawd/skills/arxiv-paper-reader
python scripts/fetch-arxiv-papers.py --categories cs.AI cs.CL cs.LG --days 3 --max-results 10 > /tmp/arxiv-papers.txt

# 生成摘要
SUMMARY="📚 arXiv每日AI研究摘要\n\n$(date +"%Y-%m-%d %H:%M")\n\n"
SUMMARY+="$(cat /tmp/arxiv-papers.txt)"

# 发送到飞书
clawdbot message send --channel feishu --target ou_9afed289b1c6420e5b856da29da2eece --message "$SUMMARY"

# 清理临时文件
rm /tmp/arxiv-papers.txt
