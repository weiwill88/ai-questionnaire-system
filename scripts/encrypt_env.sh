#!/bin/bash
# 加密.env文件以便安全上传到私有仓库

echo "🔐 加密环境变量文件"
echo "===================="

# 检查.env文件是否存在
if [ ! -f "backend/.env" ]; then
    echo "❌ 错误: backend/.env 文件不存在"
    exit 1
fi

# 提示输入密码
echo "请输入加密密码（请记住此密码，解密时需要）:"
read -s PASSWORD

# 使用openssl加密
openssl enc -aes-256-cbc -salt -in backend/.env -out backend/.env.encrypted -k "$PASSWORD"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 加密成功！"
    echo ""
    echo "生成文件: backend/.env.encrypted"
    echo ""
    echo "现在可以安全地上传 .env.encrypted 到GitHub"
    echo "⚠️  请牢记您的加密密码！"
else
    echo ""
    echo "❌ 加密失败"
    exit 1
fi

