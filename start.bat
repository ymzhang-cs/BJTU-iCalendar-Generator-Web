@echo off
echo 启动北京交通大学课表日历生成器服务...

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 创建必要的目录
if not exist uploads mkdir uploads
if not exist outputs mkdir outputs
if not exist radicale_config mkdir radicale_config
if not exist ssl mkdir ssl

REM 复制环境变量文件
if not exist .env (
    copy .env.example .env
    echo 已创建.env文件，请根据需要修改配置
)

REM 启动服务
echo 启动Docker Compose服务...
docker-compose up -d

echo.
echo 服务启动完成！
echo Web应用: http://localhost:5000
echo CalDAV服务: http://localhost:5232
echo.
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo.
pause
