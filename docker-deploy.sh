#!/bin/bash

# --- 脚本配置 ---
CONTAINER_NAME="threat-intel-hub-db"
MYSQL_IMAGE="mysql:8.0"
APP_CONTAINER_NAME="threat-intel-hub-app" # 请替换为您的应用容器名称

# --- 1. 检查 .env 文件是否存在 ---
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "错误：找不到 $ENV_FILE 文件。请确保该文件存在于当前目录下。"
    exit 1
fi

# --- 2. 从 .env 文件加载 MySQL 配置 ---
echo "--- 1. 正在从 $ENV_FILE 文件加载配置参数..."

# 使用 grep 和 sed 提取参数
DB_TYPE=$(grep ^DB_TYPE= "$ENV_FILE" | cut -d '=' -f 2)
MYSQL_HOST=$(grep ^MYSQL_HOST= "$ENV_FILE" | cut -d '=' -f 2)
MYSQL_PORT=$(grep ^MYSQL_PORT= "$ENV_FILE" | cut -d '=' -f 2)
MYSQL_USER=$(grep ^MYSQL_USER= "$ENV_FILE" | cut -d '=' -f 2)
MYSQL_PASSWORD=$(grep ^MYSQL_PASSWORD= "$ENV_FILE" | cut -d '=' -f 2)
MYSQL_NAME=$(grep ^MYSQL_NAME= "$ENV_FILE" | cut -d '=' -f 2)

# 检查关键参数是否为空
if [ -z "$MYSQL_PASSWORD" ] || [ -z "$MYSQL_NAME" ] || [ -z "$MYSQL_PORT" ]; then
    echo "错误：.env 文件中缺少 MYSQL_PASSWORD, MYSQL_NAME 或 MYSQL_PORT 等关键配置。"
    exit 1
fi

echo "   - 数据库类型: $DB_TYPE"
echo "   - 数据库名称: $MYSQL_NAME"
echo "   - 容器端口: $MYSQL_PORT"
echo "   - 用户: $MYSQL_USER"
echo "-------------------------------------"


# --- 3. 停止并删除同名旧容器 (如果存在) ---
echo "--- 2. 正在检查并停止/删除旧的 MySQL 容器 ($CONTAINER_NAME)..."
docker stop $CONTAINER_NAME > /dev/null 2>&1
docker rm $CONTAINER_NAME > /dev/null 2>&1
echo "   - 旧容器清理完成。"


# --- 4. 部署并启动 MySQL 容器 ---
echo "--- 3. 正在拉取和启动 MySQL 容器 ($CONTAINER_NAME)..."

# 使用 docker run 启动 MySQL 容器
docker run -d \
    --name $CONTAINER_NAME \
    -p $MYSQL_PORT:3306 \
    -e MYSQL_ROOT_PASSWORD=$MYSQL_PASSWORD \
    -e MYSQL_DATABASE=$MYSQL_NAME \
    -e MYSQL_USER=$MYSQL_USER \
    -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
    --restart unless-stopped \
    $MYSQL_IMAGE

if [ $? -eq 0 ]; then
    echo "   - MySQL 容器启动成功！"
    echo "   - 容器ID: $(docker ps -q -f name=$CONTAINER_NAME)"
else
    echo "错误：MySQL 容器启动失败，请检查 Docker 日志。"
    exit 1
fi

# --- 5. 检查并启动应用容器 ---
echo "--- 4. 正在检查并启动应用容器 ($APP_CONTAINER_NAME)..."

# 简单等待 MySQL 启动，避免应用连接失败
echo "   - 等待 MySQL 启动 (15秒)..."
sleep 15 

# 检查应用容器是否存在
if docker ps -a --format '{{.Names}}' | grep -q "$APP_CONTAINER_NAME"; then
    echo "   - 发现应用容器，正在尝试启动..."
    docker start $APP_CONTAINER_NAME
    if [ $? -eq 0 ]; then
        echo "   - 应用容器 ($APP_CONTAINER_NAME) 后台启动成功！"
    else
        echo "警告：应用容器启动失败。"
    fi
else
    echo "警告：未找到应用容器 ($APP_CONTAINER_NAME)。请手动启动应用。"
fi

echo "--- 部署脚本执行完毕 ---"