#!/bin/bash

# 设置工作目录
cd "$(dirname "$0")"

# 获取当前目录
CURRENT_DIR="$(pwd)"
PROJECT_ROOT="$(dirname "$CURRENT_DIR")"

# 添加到 Python 路径
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 安装依赖
echo "正在安装依赖..."
pip install -r "$CURRENT_DIR/backend/requirements.txt"

# 启动服务器
echo "正在启动智能体网络搜索服务..."
cd "$CURRENT_DIR/backend"
python main.py 