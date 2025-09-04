#!/bin/bash

# 启动脚本

echo "启动北京交通大学课表日历生成器服务..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
mkdir -p uploads outputs radicale_config ssl

# 复制环境变量文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建.env文件，请根据需要修改配置"
fi

# 启动服务
echo "启动Docker Compose服务..."
docker-compose up -d

echo "服务启动完成！"
echo "Web应用: http://localhost:5000"
echo "CalDAV服务: http://localhost:5232"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
