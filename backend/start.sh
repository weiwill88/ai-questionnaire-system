#!/bin/bash
# 问卷系统后端启动脚本

cd "$(dirname "$0")"

echo "🚀 正在启动问卷系统后端..."

# 检查并停止旧进程
OLD_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$OLD_PID" ]; then
    echo "🛑 检测到端口8000已被占用 (PID: $OLD_PID)"
    echo "   正在停止旧进程..."
    kill -TERM $OLD_PID 2>/dev/null
    sleep 2
    
    # 如果进程还在，强制杀掉
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "   强制停止..."
        kill -9 $OLD_PID 2>/dev/null
    fi
    echo "✅ 旧进程已停止"
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在！"
    echo "请先运行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ .env配置文件不存在！"
    echo "请先创建.env文件，参考README.md的步骤5"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 检查依赖是否最新
echo "📦 检查依赖版本..."
pip show supabase 2>/dev/null | grep "Version: 2.24" > /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  检测到旧版本依赖，正在升级..."
    pip install --upgrade supabase websockets -q
fi

echo "✨ 启动服务 (端口: 8000)..."
python main.py

