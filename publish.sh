#!/bin/bash
# 构建成长学习站，再走 briefing-site 的发布流程（它会把 growth-site/dist 复制为 growth/ 一起推送）
set -e
cd /workspace/growth-site && python3 build.py
bash /workspace/briefing-site/publish.sh
