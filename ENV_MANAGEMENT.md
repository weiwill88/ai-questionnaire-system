# 🔐 环境变量配置管理指南

> **核心问题**: .env文件是否应该上传到GitHub私有仓库？

---

## ❓ 您的疑问

**问题**：我在上传到GitHub的时候，这个.env文件里面的配置不需要上传吗？因为里面有我的密钥，既然是私有仓库是否可以上传？因为等一下我不是要从服务器上下载这个仓库吗？难道我要下载到我的服务器上面之后再去配置密钥吗？

**答案**：❌ **建议不要直接上传.env**，即使是私有仓库。但我们提供了3种更好的方案！

---

## 🎯 推荐方案对比

| 方案 | 安全性 | 便捷性 | 适用场景 |
|------|--------|--------|---------|
| **方案1: 加密上传** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **推荐！只有您一个人使用** |
| **方案2: 快速配置脚本** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 配置简单，适合快速部署 |
| **方案3: 直接上传** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 仅限紧急情况 |

---

## 🔐 方案1：加密上传（最推荐）

### ✅ 优点
- 配置文件在GitHub上，不用每次手动输入
- 即使GitHub账号泄露，没有密码也无法使用
- 符合安全最佳实践

### 📝 使用步骤

#### 第1步：在本地加密配置文件

```bash
cd /Users/weidongdong/Downloads/课程/问卷

# 添加执行权限
chmod +x scripts/*.sh

# 加密.env文件
./scripts/encrypt_env.sh

# 提示输入密码（比如: MySecretPass123）
# ⚠️ 请务必记住这个密码！
```

**结果**：生成 `backend/.env.encrypted` 文件

#### 第2步：上传加密文件到GitHub

```bash
# .env.encrypted 可以安全上传
git add backend/.env.encrypted
git add scripts/
git commit -m "Add encrypted environment config"
git push origin main
```

#### 第3步：在服务器上解密

```bash
# SSH登录服务器
ssh root@YOUR_SERVER_IP

# 克隆仓库
git clone git@github.com:YOUR_USERNAME/ai-questionnaire-system.git
cd ai-questionnaire-system

# 添加执行权限
chmod +x scripts/*.sh

# 解密配置文件
./scripts/decrypt_env.sh
# 输入您之前设置的密码: MySecretPass123

# 启动服务
docker-compose up -d --build
```

### 🔑 密码管理建议
- 使用密码管理器（1Password、LastPass）保存密码
- 或写在安全的地方（不是GitHub）

---

## ⚡ 方案2：快速配置脚本（次推荐）

### ✅ 优点
- 不需要记密码
- 交互式配置，不容易出错
- 配置过程清晰

### 📝 使用步骤

#### 在服务器上一键配置

```bash
# SSH登录服务器
ssh root@YOUR_SERVER_IP

# 克隆仓库（不包含.env）
git clone git@github.com:YOUR_USERNAME/ai-questionnaire-system.git
cd ai-questionnaire-system

# 添加执行权限
chmod +x scripts/*.sh

# 运行快速配置脚本
./scripts/quick_setup.sh
```

**配置过程**：
```
⚡ 快速配置环境变量
====================

📝 请输入以下配置信息：

Supabase URL: https://rnidqivrrsbcemywpryk.supabase.co
Supabase Service Key: eyJhbGci...
OpenRouter API Key: sk-or-...
OpenRouter Model (默认: minimax/minimax-m2): [直接回车]
Session ID (默认: SJTU_SAIF_20251114): [直接回车]
端口 (默认: 8000): [直接回车]
CORS来源 (默认: *): [直接回车]

✅ 配置完成！
```

### 💡 提示
您可以把配置信息保存在手机备忘录或密码管理器中，配置时复制粘贴即可。

---

## 📋 方案3：手动复制粘贴（传统方法）

### 📝 步骤

```bash
# 1. SSH登录服务器
ssh root@YOUR_SERVER_IP

# 2. 克隆仓库
git clone git@github.com:YOUR_USERNAME/ai-questionnaire-system.git
cd ai-questionnaire-system

# 3. 复制模板
cp backend/env.example backend/.env

# 4. 编辑配置
nano backend/.env
# 或
vim backend/.env

# 5. 手动填入所有配置项
# 复制粘贴您的Supabase URL、密钥等

# 6. 保存退出
# nano: Ctrl+X, Y, Enter
# vim: :wq

# 7. 启动服务
docker-compose up -d --build
```

---

## ⚠️ 如果您确实要直接上传.env（不推荐）

### 前提条件
- ✅ 确认仓库是**私有的**
- ✅ **永远不会**改成公开仓库
- ✅ **不会**添加其他协作者
- ✅ 了解Git历史会永久保存密钥的风险

### 操作步骤

#### 1. 修改 .gitignore

```bash
# 编辑 .gitignore
nano .gitignore

# 注释掉以下行：
# .env
# *.env

# 或者特别允许backend/.env：
!backend/.env
```

#### 2. 强制添加.env

```bash
# 即使.gitignore排除了，也强制添加
git add -f backend/.env

# 提交
git commit -m "Add production .env (PRIVATE REPO ONLY)"

# 推送
git push origin main
```

#### 3. 在服务器上

```bash
# 克隆后直接启动，无需配置
git clone git@github.com:YOUR_USERNAME/ai-questionnaire-system.git
cd ai-questionnaire-system
docker-compose up -d --build
```

### ⚠️ 重要警告

如果您选择此方案：
1. 🚫 **永远不要**把仓库改成公开
2. 🚫 **永远不要**在公开场合分享仓库链接
3. 🚫 添加协作者前先移除.env
4. 📝 记录密钥在哪些地方出现过
5. 🔄 定期轮换密钥

---

## 🎯 我的建议

### 对于您的情况（个人使用）

**推荐组合**：

1. **开发阶段**：使用方案2（快速配置脚本）
   - 方便调试
   - 配置灵活

2. **正式部署**：使用方案1（加密上传）
   - 一次配置，到处使用
   - 安全性高
   - 重新部署时不用重复输入

---

## 📊 三种方案对比示例

### 场景：需要在3台服务器上部署

| 方案 | 第1台耗时 | 第2台耗时 | 第3台耗时 | 安全性 |
|------|----------|----------|----------|--------|
| 方案1（加密） | 5分钟 | 2分钟 | 2分钟 | ⭐⭐⭐⭐⭐ |
| 方案2（脚本） | 3分钟 | 3分钟 | 3分钟 | ⭐⭐⭐⭐ |
| 方案3（手动） | 5分钟 | 5分钟 | 5分钟 | ⭐⭐⭐ |
| 直接上传.env | 1分钟 | 1分钟 | 1分钟 | ⚠️ ⭐⭐ |

---

## 🔧 实用技巧

### 技巧1：配置备份

无论用哪种方案，都建议本地保存一份配置清单：

```bash
# 在本地创建配置清单（不上传到Git）
cat > ~/questionnaire_config.txt << 'EOF'
SUPABASE_URL=https://rnidqivrrsbcemywpryk.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=minimax/minimax-m2
SESSION_ID=SJTU_SAIF_20251114
EOF

# 保存到安全位置（不是项目目录）
```

### 技巧2：环境变量检查脚本

```bash
#!/bin/bash
# 检查.env配置是否完整

echo "🔍 检查环境变量配置"

if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env 不存在"
    exit 1
fi

# 检查必需的配置项
required_vars=("SUPABASE_URL" "SUPABASE_SERVICE_KEY" "OPENROUTER_API_KEY")

for var in "${required_vars[@]}"; do
    if grep -q "^${var}=" backend/.env; then
        value=$(grep "^${var}=" backend/.env | cut -d'=' -f2)
        if [ -z "$value" ] || [ "$value" == "your-" ]; then
            echo "⚠️  ${var} 未配置或使用默认值"
        else
            echo "✅ ${var} 已配置"
        fi
    else
        echo "❌ ${var} 缺失"
    fi
done
```

---

## 🎓 最佳实践总结

1. ✅ **永远不要直接提交明文.env**（即使是私有仓库）
2. ✅ **使用加密或配置脚本**
3. ✅ **不同环境使用不同配置**
4. ✅ **定期轮换密钥**
5. ✅ **使用密码管理器保存配置信息**
6. ✅ **审查Git历史，确保没有意外提交密钥**

---

## 🆘 如果密钥已经泄露

```bash
# 1. 立即在Supabase更换Service Key
# 2. 立即在OpenRouter更换API Key

# 3. 从Git历史中彻底删除（谨慎操作）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# 4. 强制推送（会改写历史）
git push origin --force --all
```

---

## ❓ 常见问题

### Q1: 加密密码忘记了怎么办？
**A**: 无法解密，需要重新配置。建议密码保存在密码管理器中。

### Q2: 可以用更简单的加密方法吗？
**A**: 可以用base64编码（不安全但总比明文好）：
```bash
# 编码
cat backend/.env | base64 > backend/.env.b64

# 解码
cat backend/.env.b64 | base64 -d > backend/.env
```

### Q3: Docker容器内如何查看环境变量？
**A**: 
```bash
docker exec questionnaire-backend env | grep SUPABASE
```

### Q4: 私有仓库会被GitHub员工看到吗？
**A**: GitHub声明不会主动查看私有仓库内容，但技术上他们有能力访问。这就是为什么建议加密。

---

## 📞 需要帮助？

- 查看部署指南: [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
- 查看主文档: [README.md](README.md)

---

**结论**：虽然私有仓库相对安全，但使用**加密上传**或**配置脚本**是更专业、更安全的做法，长远来看也更方便！🎯

