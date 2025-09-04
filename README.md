# 北京交通大学课表日历生成器 Web版

![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fymzhang-cs%2FBJTU-iCalendar-Generator-Web&countColor=%23263759)

将教务系统的课程表导出为 iCalendar 文件，并提供 CalDAV 服务，方便导入到各种日历软件中。

## 功能特性

- ✅ **智能解析**: 自动识别课表HTML文件中的课程信息
- ✅ **标准格式**: 生成标准iCalendar格式文件，兼容所有主流日历应用
- ✅ **CalDAV支持**: 集成Radicale服务，支持日历同步和共享
- ✅ **Web界面**: 现代化的Web界面，支持拖拽上传
- ✅ **Docker部署**: 一键部署，包含所有必要服务
- ✅ **移动端支持**: 提供iOS和Android设备的详细设置指南

## 快速开始

### 使用Docker Compose（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/ymzhang-cs/BJTU-iCalendar-Generator-Web.git
   cd BJTU-iCalendar-Generator-Web
   ```

2. **启动服务**
   ```bash
   # Linux/macOS
   chmod +x start.sh
   ./start.sh
   
   # Windows
   docker-compose up -d
   ```

3. **访问应用**
   - Web应用: http://localhost:5000
   - CalDAV服务: http://localhost:5232

### 手动部署

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动Radicale服务**
   ```bash
   docker run -d --name radicale \
     -p 5232:5232 \
     -v $(pwd)/radicale_data:/data \
     -v $(pwd)/radicale_config:/config \
     tomsquest/docker-radicale:latest
   ```

3. **启动Web应用**
   ```bash
   python app.py
   ```

## 使用方法

### 1. 获取课表HTML文件

1. 登录北京交通大学教务系统
2. 进入课表页面
3. 使用 `Ctrl + S` 保存页面，选择"网页，仅HTML"格式

### 2. 上传并生成日历

1. 访问 http://localhost:5000
2. 拖拽或选择HTML文件上传
3. 等待系统解析并生成ICS文件
4. 下载ICS文件或创建CalDAV账户

### 3. 导入到日历应用

#### 下载ICS文件方式
- **iOS**: 通过邮件发送ICS文件，在邮件应用中打开并添加到日历
- **Android**: 使用日历应用导入ICS文件
- **Outlook**: 文件 → 打开和导出 → 导入/导出 → 导入iCalendar文件
- **Google Calendar**: 设置 → 导入和导出 → 导入

#### CalDAV账户方式
1. 点击"创建CalDAV账户"按钮
2. 保存账户信息
3. 在日历应用中添加CalDAV账户：
   - **iOS**: 设置 → 日历 → 账户 → 添加账户 → 其他 → CalDAV账户
   - **Android**: 日历应用 → 添加账户 → CalDAV

## 技术架构

- **后端**: Flask + Python
- **前端**: Bootstrap 5 + JavaScript
- **CalDAV服务**: Radicale
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx（可选）

## 项目结构

```
├── app.py                 # Flask主应用
├── calendar_generator.py  # 日历生成器核心逻辑
├── caldav_integration.py  # CalDAV服务集成
├── templates/            # HTML模板
├── static/              # 静态资源
├── docker-compose.yml   # Docker Compose配置
├── Dockerfile          # Docker镜像配置
├── nginx.conf          # Nginx配置
└── requirements.txt    # Python依赖
```

## 配置说明

### 环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-in-production

# Radicale配置
RADICALE_SERVER_URL=http://localhost:5232
```

### 端口配置

- **5000**: Web应用端口
- **5232**: CalDAV服务端口
- **80/443**: Nginx反向代理端口（可选）

## 开发指南

### 本地开发

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动开发服务器**
   ```bash
   export FLASK_ENV=development
   python app.py
   ```

3. **启动Radicale服务**
   ```bash
   docker run -d --name radicale-dev \
     -p 5232:5232 \
     -v $(pwd)/radicale_data:/data \
     tomsquest/docker-radicale:latest
   ```

### 测试

```bash
# 运行测试
python -m pytest tests/

# 健康检查
curl http://localhost:5000/api/health
```

## 故障排除

### 常见问题

1. **文件上传失败**
   - 检查文件格式是否为HTML
   - 确认文件大小不超过16MB

2. **CalDAV连接失败**
   - 确认Radicale服务正在运行
   - 检查防火墙设置
   - 验证服务器地址和端口

3. **课程解析错误**
   - 确认HTML文件来自教务系统课表页面
   - 检查文件是否完整保存

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f radicale
```

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- 原始项目: [BJTU-iCalendar-Generator](https://github.com/ymzhang-cs/BJTU-iCalendar-Generator)
- Radicale: [CalDAV服务器](https://radicale.org/)
- Flask: [Web框架](https://flask.palletsprojects.com/)

## 更新日志

### v1.0.0
- 初始版本发布
- 支持HTML文件上传和ICS生成
- 集成Radicale CalDAV服务
- 提供Web界面和Docker部署