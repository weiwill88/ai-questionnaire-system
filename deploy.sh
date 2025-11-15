#!/bin/bash
# 问卷系统Docker部署脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署问卷系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装！请先安装Docker"
    echo "   安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose未安装！"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 检查.env文件是否存在
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env文件不存在！"
    echo "   请先创建配置文件:"
    echo "   cp backend/env.template backend/.env"
    echo "   然后编辑填入Supabase配置"
    exit 1
fi

echo "✅ 配置文件检查通过"

# 停止并删除旧容器
echo "🛑 停止旧容器..."
docker compose down 2>/dev/null || true

# 构建镜像
echo "🔨 构建Docker镜像..."
docker compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "✅ 部署成功！"
    echo ""
    echo "📊 服务状态:"
    docker compose ps
    echo ""
    echo "🌐 访问地址: http://你的服务器IP:8000"
    echo ""
    echo "📝 常用命令:"
    echo "   查看日志: docker compose logs -f"
    echo "   停止服务: docker compose down"
    echo "   重启服务: docker compose restart"
    echo "   查看状态: docker compose ps"
else
    echo "❌ 部署失败！查看日志:"
    docker compose logs
    exit 1
fi

