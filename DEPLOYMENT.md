# 部署指南

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 1GB 可用磁盘空间

## 快速部署

### Windows

1. 确保已安装 Docker Desktop
2. 双击运行 `start.bat`
3. 等待服务启动完成
4. 访问 http://localhost:5000

### Linux/macOS

1. 确保已安装 Docker 和 Docker Compose
2. 运行启动脚本：
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
3. 访问 http://localhost:5000

## 手动部署

### 1. 克隆项目

```bash
git clone https://github.com/ymzhang-cs/BJTU-iCalendar-Generator-Web.git
cd BJTU-iCalendar-Generator-Web
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，修改必要的配置
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 健康检查
curl http://localhost:5000/api/health
```

## 生产环境部署

### 1. 安全配置

- 修改 `.env` 中的 `SECRET_KEY`
- 配置 HTTPS 证书
- 设置防火墙规则

### 2. 域名配置

修改 `nginx.conf` 中的 `server_name`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    # ...
}
```

### 3. SSL 证书

将 SSL 证书文件放置在 `ssl/` 目录下，并取消注释 `nginx.conf` 中的 HTTPS 配置。

### 4. 数据持久化

确保以下目录已正确挂载：

- `radicale_data/`: CalDAV 数据存储
- `uploads/`: 临时上传文件
- `outputs/`: 生成的 ICS 文件

## 监控和维护

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f radicale
```

### 备份数据

```bash
# 备份 CalDAV 数据
docker-compose exec radicale tar -czf /backup/radicale_data.tar.gz /data

# 备份配置文件
tar -czf config_backup.tar.gz radicale_config/ .env
```

### 更新服务

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

## 故障排除

### 常见问题

1. **端口冲突**
   - 检查 5000 和 5232 端口是否被占用
   - 修改 `docker-compose.yml` 中的端口映射

2. **权限问题**
   - 确保 Docker 有权限访问项目目录
   - 检查文件权限设置

3. **内存不足**
   - 增加 Docker 内存限制
   - 优化服务配置

### 性能优化

1. **增加工作进程**
   ```yaml
   # 在 docker-compose.yml 中修改
   command: ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "app:app"]
   ```

2. **启用缓存**
   - 配置 Redis 缓存
   - 使用 CDN 加速静态资源

3. **数据库优化**
   - 使用 PostgreSQL 替代 SQLite
   - 配置连接池

## 安全建议

1. **定期更新**
   - 保持 Docker 镜像最新
   - 及时应用安全补丁

2. **访问控制**
   - 配置防火墙规则
   - 使用 VPN 或内网访问

3. **数据保护**
   - 定期备份数据
   - 加密敏感信息

4. **监控告警**
   - 配置服务监控
   - 设置异常告警
