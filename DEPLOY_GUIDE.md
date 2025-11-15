# 🚀 服务器部署完整指南

> **适用场景**: 将问卷系统部署到您的Linux服务器（使用Docker）

---

## 📋 部署前准备清单

### 1️⃣ 服务器要求
- ✅ 操作系统: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- ✅ RAM: 至少 1GB
- ✅ 存储: 至少 10GB 可用空间
- ✅ 网络: 公网IP或域名
- ✅ 端口: 8000（后端API）、80/443（前端，可选）

### 2️⃣ 需要准备的信息
- [ ] Supabase URL
- [ ] Supabase Service Key
- [ ] OpenRouter API Key（用于AI分析）
- [ ] 服务器IP地址
- [ ] SSH登录凭证

---

## 🔐 方案选择：GitHub 私有仓库 vs 直接上传

### ⭐ 推荐：使用 GitHub 私有仓库（Private Repository）

#### ✅ 优点
- 版本控制，便于回滚
- 团队协作方便
- 自动备份
- 支持CI/CD自动部署
- **私有仓库完全安全**，只有您授权的人才能访问

#### 📌 私有仓库说明
```
✓ 私有仓库 (Private Repository)
  - 只有仓库所有者和授权的协作者可以访问
  - 代码、配置完全保密
  - 免费用户也可以创建无限数量的私有仓库
  - 推荐使用！

✗ 公开仓库 (Public Repository)
  - 任何人都可以查看代码
  - 不要使用！会暴露Supabase密钥等敏感信息
```

#### 🔒 安全注意事项
**重要**: 无论使用私有还是公开仓库，都要做到：
1. ❌ **绝不提交 `.env` 文件**（已在 `.gitignore` 中排除）
2. ❌ **绝不提交包含真实密钥的文件**
3. ✅ **只提交 `env.example` 模板文件**
4. ✅ **在服务器上单独配置 `.env`**

---

## 🎯 部署方式对比

| 方式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **GitHub私有仓库** | 推荐 | 版本控制、便于更新 | 需要配置SSH密钥 |
| **直接上传** | 快速测试 | 简单直接 | 难以管理更新 |
| **Docker Hub** | 团队共享 | 打包完整 | 需要额外配置 |

---

## 📦 方案A：使用 GitHub 私有仓库部署（推荐）

### Step 1: 创建 GitHub 私有仓库

```bash
# 1. 在本地初始化 Git（如果还没有）
cd /Users/weidongdong/Downloads/课程/问卷
git init

# 2. 添加所有文件到Git
git add .

# 3. 提交到本地仓库
git commit -m "Initial commit: AI问卷系统"

# 4. 在 GitHub 上创建私有仓库
#    访问: https://github.com/new
#    仓库名: ai-questionnaire-system
#    可见性: ✅ Private (私有)
#    不要勾选 "Initialize this repository with a README"

# 5. 关联远程仓库
git remote add origin git@github.com:YOUR_USERNAME/ai-questionnaire-system.git

# 6. 推送到 GitHub
git branch -M main
git push -u origin main
```

### Step 2: 在服务器上部署

#### 2.1 SSH 登录服务器

```bash
# 从本地连接到服务器
ssh root@YOUR_SERVER_IP
# 或
ssh username@YOUR_SERVER_IP
```

#### 2.2 安装 Docker 和 Docker Compose

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

#### 2.3 配置 SSH 密钥（用于拉取私有仓库）

```bash
# 1. 在服务器上生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"
# 一路回车（使用默认路径）

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 复制输出的公钥，然后在 GitHub 上添加：
#    GitHub > Settings > SSH and GPG keys > New SSH key
#    Title: 服务器部署密钥
#    Key: 粘贴刚才复制的公钥

# 4. 测试连接
ssh -T git@github.com
# 看到 "Hi username! You've successfully authenticated" 表示成功
```

#### 2.4 克隆仓库到服务器

```bash
# 1. 创建项目目录
mkdir -p ~/apps
cd ~/apps

# 2. 克隆私有仓库
git clone git@github.com:YOUR_USERNAME/ai-questionnaire-system.git questionnaire
cd questionnaire
```

#### 2.5 配置环境变量

```bash
# 1. 复制环境变量模板
cp backend/env.example backend/.env

# 2. 编辑配置文件
nano backend/.env
# 或
vim backend/.env

# 3. 填入真实的配置信息：
# SUPABASE_URL=https://rnidqivrrsbcemywpryk.supabase.co
# SUPABASE_SERVICE_KEY=你的真实密钥
# OPENROUTER_API_KEY=你的真实密钥
# OPENROUTER_MODEL=minimax/minimax-m2
# SESSION_ID=SJTU_SAIF_20251114
# PORT=8000
# CORS_ORIGINS=*

# 4. 保存并退出（nano: Ctrl+X, Y, Enter; vim: :wq）
```

#### 2.6 启动服务

```bash
# 1. 构建并启动 Docker 容器
docker-compose up -d --build

# 2. 查看日志
docker-compose logs -f backend

# 3. 查看容器状态
docker-compose ps

# 应该看到：
# Name                 State    Ports
# questionnaire-backend   Up      0.0.0.0:8000->8000/tcp
```

#### 2.7 测试服务

```bash
# 测试后端 API
curl http://localhost:8000/

# 测试统计数据
curl "http://localhost:8000/api/stats?session_id=SJTU_SAIF_20251114"
```

#### 2.8 配置防火墙（如果有）

```bash
# 允许 8000 端口
sudo ufw allow 8000/tcp

# 如果使用 firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

#### 2.9 访问系统

- 后端API: `http://YOUR_SERVER_IP:8000`
- Dashboard: `http://YOUR_SERVER_IP:8000/static/dashboard.html`（如果配置了静态文件服务）

---

## 📦 方案B：直接上传文件部署（快速测试）

### Step 1: 打包项目

```bash
# 在本地打包（排除不必要的文件）
cd /Users/weidongdong/Downloads/课程
tar -czf questionnaire.tar.gz \
    --exclude='问卷/backend/venv' \
    --exclude='问卷/backend/__pycache__' \
    --exclude='问卷/backend/*.pyc' \
    --exclude='问卷/.git' \
    问卷/
```

### Step 2: 上传到服务器

```bash
# 使用 scp 上传
scp questionnaire.tar.gz root@YOUR_SERVER_IP:~/

# 或使用 rsync（更快）
rsync -avz --exclude='venv' --exclude='__pycache__' \
    问卷/ root@YOUR_SERVER_IP:~/questionnaire/
```

### Step 3: 在服务器上解压并部署

```bash
# SSH 登录服务器
ssh root@YOUR_SERVER_IP

# 解压
tar -xzf questionnaire.tar.gz
cd 问卷

# 后续步骤同方案A的 2.5 ~ 2.9
```

---

## 🔄 日常维护命令

### 更新代码（GitHub方式）

```bash
cd ~/apps/questionnaire

# 1. 拉取最新代码
git pull origin main

# 2. 重新构建并重启
docker-compose down
docker-compose up -d --build
```

### 查看日志

```bash
# 实时查看日志
docker-compose logs -f backend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 只重启后端
docker-compose restart backend
```

### 停止服务

```bash
# 停止服务（保留数据）
docker-compose stop

# 停止并删除容器（不删除镜像）
docker-compose down

# 完全清理（包括镜像）
docker-compose down --rmi all
```

### 查看资源占用

```bash
# 查看容器资源
docker stats questionnaire-backend

# 查看磁盘使用
docker system df
```

---

## 🌐 配置域名（可选）

如果您有域名，可以使用 Nginx 反向代理：

### Step 1: 安装 Nginx

```bash
sudo apt install nginx -y
```

### Step 2: 配置反向代理

```bash
# 创建配置文件
sudo nano /etc/nginx/sites-available/questionnaire

# 添加以下内容：
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 前端静态文件
    location / {
        root /root/apps/questionnaire/frontend;
        index dashboard.html;
        try_files $uri $uri/ =404;
    }
}
```

### Step 3: 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/questionnaire /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### Step 4: 配置 HTTPS（推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取免费 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 🛠️ 故障排查

### 问题1: 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查环境变量
docker-compose config

# 重新构建
docker-compose build --no-cache backend
```

### 问题2: 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8000

# 杀死占用进程
sudo kill -9 PID
```

### 问题3: Supabase 连接失败

```bash
# 测试网络连接
curl -I https://rnidqivrrsbcemywpryk.supabase.co

# 检查环境变量
docker exec questionnaire-backend env | grep SUPABASE
```

### 问题4: 磁盘空间不足

```bash
# 清理 Docker 缓存
docker system prune -a

# 清理日志
sudo journalctl --vacuum-time=3d
```

---

## 📊 监控建议

### 使用 Docker 自带的健康检查

```bash
# 查看容器健康状态
docker ps
# STATUS列会显示 "healthy" 或 "unhealthy"
```

### 配置日志轮转（防止日志过大）

```bash
# 编辑 docker-compose.yml，添加日志配置：
```

```yaml
services:
  backend:
    # ... 其他配置 ...
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🔒 安全加固建议

1. **修改默认端口**（如果需要）
   ```yaml
   ports:
     - "18000:8000"  # 使用非标准端口
   ```

2. **限制CORS来源**（生产环境）
   ```bash
   # .env 文件中
   CORS_ORIGINS=https://your-domain.com
   ```

3. **配置防火墙**
   ```bash
   # 只允许特定IP访问
   sudo ufw allow from YOUR_IP to any port 8000
   ```

4. **定期备份**
   ```bash
   # 备份脚本
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   tar -czf ~/backups/questionnaire_$DATE.tar.gz ~/apps/questionnaire
   ```

---

## 📞 需要帮助？

- 查看完整文档: [README.md](README.md)
- 常见问题: [FAQ.md](FAQ.md)
- 问题反馈: 在GitHub仓库提交Issue

---

## 🎉 部署完成检查清单

- [ ] Docker 和 Docker Compose 安装成功
- [ ] 私有仓库创建并推送成功
- [ ] 服务器上成功克隆代码
- [ ] `.env` 配置文件正确填写
- [ ] Docker 容器成功启动（`docker-compose ps` 显示 "Up"）
- [ ] 后端API可以访问 `curl http://localhost:8000/`
- [ ] 统计数据接口正常 `curl http://localhost:8000/api/stats?session_id=SJTU_SAIF_20251114`
- [ ] 防火墙规则配置完成
- [ ] （可选）域名和HTTPS配置完成

**恭喜！🎊 您的问卷系统已成功部署！**

