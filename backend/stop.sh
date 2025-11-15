#!/bin/bash
# 问卷系统后端停止脚本

echo "🛑 正在停止问卷系统后端..."

# 查找占用8000端口的进程
PID=$(lsof -ti:8000 2>/dev/null)

if [ -z "$PID" ]; then
    echo "ℹ️  没有检测到运行中的服务（端口8000未被占用）"
    exit 0
fi

echo "📍 找到进程 PID: $PID"
echo "   正在优雅停止..."

# 尝试优雅停止
kill -TERM $PID 2>/dev/null
sleep 2

# 检查进程是否还在
if ps -p $PID > /dev/null 2>&1; then
    echo "   进程未响应，强制停止..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# 再次检查
if ! ps -p $PID > /dev/null 2>&1; then
    echo "✅ 服务已成功停止"
else
    echo "❌ 停止失败，请手动执行: kill -9 $PID"
    exit 1
fi

