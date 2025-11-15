# AI应用需求调研系统 - 快速启动指南

> 📖 **文档导航**
> - 🚀 本文档: 本地开发快速启动
> - 🐳 [DEPLOY.md](DEPLOY.md): **服务器Docker部署完整指南** ⭐
> - ✅ [CHECKLIST.md](CHECKLIST.md): **部署检查清单（逐步核对）** ⭐
> - ⚡ [QUICK_REFERENCE.md](QUICK_REFERENCE.md): 常用命令速查表
> - 📂 [FILES.md](FILES.md): 项目文件说明

## 📦 一、准备工作（5分钟）

### 1. Supabase配置
1. 登录 https://supabase.com
2. 进入项目 → Settings → API
3. 复制：
   - `URL`: `https://xxxxx.supabase.co`
   - `service_role` secret key

### 2. 执行数据库脚本
1. 打开 Supabase SQL Editor
2. 粘贴 `问卷/database_setup_fixed.sql` 内容
3. 点击 RUN
4. 看到成功提示

---

## 🚀 二、启动后端（3分钟）

```bash
# 1. 进入后端目录
cd 问卷/backend

# 2. 创建虚拟环境（第一次需要）
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate    # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 4. 安装依赖（第一次需要）
pip install -r requirements.txt

# 5. 创建配置文件
cat > .env << 'EOF'
SUPABASE_URL=https://你的项目.supabase.co
SUPABASE_SERVICE_KEY=你的service-role-key
SESSION_ID=SJTU_SAIF_20251114
CORS_ORIGINS=*
PORT=8000
EOF

# 6. 编辑.env，填入真实配置
nano .env

# 7. 启动服务
python main.py
```

看到以下输出表示成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## 📱 三、配置前端（2分钟）

### 1. 修改问卷页配置
打开 `问卷/frontend/questionnaire.html`，找到第26-30行：

```javascript
const CONFIG = {
    SUPABASE_URL: 'https://你的项目.supabase.co',
    SUPABASE_ANON_KEY: '你的anon-key',  // 注意是anon key不是service key
    SESSION_ID: 'SJTU_SAIF_20251114',
    API_BASE_URL: 'http://localhost:8000'
};
```

### 2. 修改管理后台配置
打开 `问卷/frontend/dashboard.html`，找到第12-16行，修改同样内容。

---

## ✅ 四、测试（2分钟）

### 1. 测试后端
```bash
curl http://localhost:8000/
# 应该返回API信息
```

### 2. 测试问卷提交
1. 用浏览器打开：`file:///你的路径/问卷/frontend/questionnaire.html`
2. 填写问卷并提交
3. 应该显示"提交成功"

### 3. 测试管理后台
1. 用浏览器打开：`file:///你的路径/问卷/frontend/dashboard.html`
2. 应该能看到刚才提交的数据

---

## 🔧 常见问题

### Q1: 启动时报错 `ModuleNotFoundError: No module named 'supabase'`
**A**: 没有激活虚拟环境或依赖没装好
```bash
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Q2: 报错 `缺少SUPABASE_URL或SUPABASE_SERVICE_KEY环境变量`
**A**: 没有创建.env文件或配置错误
```bash
# 检查.env文件是否存在
ls -la .env

# 如果不存在，按"二、第5步"创建
```

### Q3: 前端提交后报错 `CORS error`
**A**: 后端没启动，或.env中CORS_ORIGINS配置错误
```bash
# 确保.env中有
CORS_ORIGINS=*
```

### Q4: 启动时报错 `TypeError: Client.__init__() got an unexpected keyword argument 'proxy'`
**A**: 依赖版本冲突，需要升级supabase到最新版本
```bash
source venv/bin/activate
pip uninstall supabase gotrue httpx -y
pip install --upgrade supabase
pip uninstall supafunc -y  # 如果存在的话
python main.py
```

### Q5: 启动时报错 `ModuleNotFoundError: No module named 'websockets.asyncio'`
**A**: websockets版本太旧，需要升级到15.0+
```bash
source venv/bin/activate
pip install --upgrade websockets
python main.py
```

### Q6: 前端提交后报错 `409 重复提交`
**A**: 这是正常的防重复机制，清除浏览器LocalStorage或换浏览器测试

---

## 📂 项目结构

```
问卷/
├── backend/                    # 后端代码
│   ├── main.py                # API主应用 ⭐ 启动这个
│   ├── database.py            # 数据库操作
│   ├── models.py              # 数据模型
│   ├── requirements.txt       # Python依赖
│   ├── .env                   # 配置文件（需自己创建）
│   └── venv/                  # 虚拟环境（自动生成）
│
├── frontend/                   # 前端页面
│   ├── questionnaire.html     # 问卷页（手机端）
│   └── dashboard.html         # 管理后台（电脑端）
│
└── database_setup_fixed.sql   # 数据库脚本
```

---

## 🎯 日常使用

### 启动服务（推荐）⭐
```bash
cd /Users/weidongdong/Downloads/课程/问卷/backend
./start.sh
```

**脚本会自动：**
- 🔍 检测并停止旧进程（避免端口冲突）
- ✅ 检查虚拟环境和配置文件
- 📦 验证依赖版本（必要时自动升级）
- 🚀 启动服务

### 停止服务

**方式1：使用停止脚本（推荐）**
```bash
cd /Users/weidongdong/Downloads/课程/问卷/backend
./stop.sh
```

**方式2：手动停止**
- 如果在前台运行：按 `Ctrl + C`
- 如果在后台运行：`lsof -ti:8000 | xargs kill`

### 手动启动（不推荐）
```bash
cd /Users/weidongdong/Downloads/课程/问卷/backend
source venv/bin/activate
python main.py
```

### 退出虚拟环境
```bash
deactivate
```

---

## 🐳 Docker部署（推荐用于生产环境）

### 快速部署到服务器

```bash
# 1. 上传项目到服务器
scp -r 问卷/ username@your-server:/home/username/

# 2. SSH登录服务器
ssh username@your-server

# 3. 配置环境变量
cd 问卷
cp backend/env.template backend/.env
nano backend/.env  # 填入Supabase配置

# 4. 一键部署
./deploy.sh
```

**部署后服务自动：**
- 🔄 重启后自动恢复
- 📊 健康检查
- 📝 日志持久化

### Docker常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重启服务
docker compose restart
```

**📖 详细部署文档**: 查看 [DEPLOY.md](DEPLOY.md)

---

## 📞 获取帮助

如果遇到问题，检查：
1. ✅ 虚拟环境是否激活（看到 `(venv)` 前缀）
2. ✅ .env文件是否存在且配置正确
3. ✅ Supabase数据库脚本是否执行成功
4. ✅ 后端是否成功启动（看到 `Uvicorn running`）
5. ✅ 前端配置是否正确（URL和KEY）

**Docker部署问题**: 参考 [DEPLOY.md](DEPLOY.md) 故障排查章节

