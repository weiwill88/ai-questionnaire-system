#!/bin/bash
# 快速配置.env文件（在服务器上使用）

echo "⚡ 快速配置环境变量"
echo "===================="
echo ""

# 检查env.example是否存在
if [ ! -f "backend/env.example" ]; then
    echo "❌ 错误: backend/env.example 文件不存在"
    exit 1
fi

# 如果.env已存在，询问是否覆盖
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env 已存在"
    read -p "是否覆盖？(y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "取消配置"
        exit 0
    fi
fi

# 复制模板
cp backend/env.example backend/.env

echo "📝 请输入以下配置信息："
echo ""

# 收集配置信息
read -p "Supabase URL: " SUPABASE_URL
read -p "Supabase Service Key: " SUPABASE_SERVICE_KEY
read -p "OpenRouter API Key: " OPENROUTER_API_KEY
read -p "OpenRouter Model (默认: minimax/minimax-m2): " OPENROUTER_MODEL
OPENROUTER_MODEL=${OPENROUTER_MODEL:-minimax/minimax-m2}
read -p "Session ID (默认: SJTU_SAIF_20251114): " SESSION_ID
SESSION_ID=${SESSION_ID:-SJTU_SAIF_20251114}
read -p "端口 (默认: 8000): " PORT
PORT=${PORT:-8000}
read -p "CORS来源 (默认: *): " CORS_ORIGINS
CORS_ORIGINS=${CORS_ORIGINS:-*}

# 写入配置
cat > backend/.env << EOF
# ============================================
# AI应用需求调研系统 - 环境变量配置
# 自动生成时间: $(date)
# ============================================

# Supabase配置
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY

# OpenRouter AI配置
OPENROUTER_API_KEY=$OPENROUTER_API_KEY
OPENROUTER_MODEL=$OPENROUTER_MODEL

# 会话配置
SESSION_ID=$SESSION_ID

# 服务器配置
PORT=$PORT
CORS_ORIGINS=$CORS_ORIGINS
EOF

echo ""
echo "✅ 配置完成！"
echo ""
echo "配置文件已生成: backend/.env"
echo ""
echo "下一步："
echo "  1. 检查配置: cat backend/.env"
echo "  2. 启动服务: docker-compose up -d --build"
echo "  3. 查看日志: docker-compose logs -f backend"

