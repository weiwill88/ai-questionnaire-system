#!/bin/bash
# 在服务器上解密.env文件

echo "🔓 解密环境变量文件"
echo "===================="

# 检查加密文件是否存在
if [ ! -f "backend/.env.encrypted" ]; then
    echo "❌ 错误: backend/.env.encrypted 文件不存在"
    exit 1
fi

# 提示输入密码
echo "请输入解密密码:"
read -s PASSWORD

# 使用openssl解密
openssl enc -aes-256-cbc -d -in backend/.env.encrypted -out backend/.env -k "$PASSWORD"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 解密成功！"
    echo ""
    echo "生成文件: backend/.env"
    echo "现在可以启动服务了: docker-compose up -d"
else
    echo ""
    echo "❌ 解密失败（密码可能错误）"
    exit 1
fi

