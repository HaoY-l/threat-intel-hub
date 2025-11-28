#!/bin/bash

# --- 脚本配置 ---
CONTAINER_NAME="threat-intel-hub-db"
MYSQL_IMAGE="mysql:latest" 

# --- 1. 检查文件是否存在 ---
ENV_FILE=".env"

# 检查 docker compose 文件是否存在并确定文件名
if [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
elif [ -f "compose.yml" ]; then
    COMPOSE_FILE="compose.yml"
else
    echo "错误：找不到 docker-compose.yml 或 compose.yml 文件。请确保存在其中之一。"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "错误：找不到 $ENV_FILE 文件。请确保该文件存在于当前目录下。"
    exit 1
fi

# --- 2. 从 .env 文件加载 MySQL 配置 (略) ---
echo "--- 1. 正在从 $ENV_FILE 文件加载配置参数..."

# 定义一个函数来安全地提取变量值
safe_load_var() {
    local VAR_NAME=$1
    # 查找变量行 -> 移除注释及其后的内容 -> 提取等号后的值 -> 移除前后空格
    local VAR_VALUE=$(grep "^${VAR_NAME}=" "$ENV_FILE" | sed 's/#.*//' | awk -F'=' '{print $2}' | tr -d '[:space:]')
    echo "$VAR_VALUE"
}

DB_TYPE=$(safe_load_var DB_TYPE)
MYSQL_HOST=$(safe_load_var MYSQL_HOST)
MYSQL_PORT=$(safe_load_var MYSQL_PORT)
MYSQL_USER=$(safe_load_var MYSQL_USER)
MYSQL_PASSWORD=$(safe_load_var MYSQL_PASSWORD)
MYSQL_NAME=$(safe_load_var MYSQL_NAME)

if [ -z "$MYSQL_PASSWORD" ] || [ -z "$MYSQL_NAME" ] || [ -z "$MYSQL_PORT" ]; then
    echo "错误：.env 文件中缺少 MYSQL_PASSWORD, MYSQL_NAME 或 MYSQL_PORT 等关键配置。"
    exit 1
fi

echo "   - 数据库类型: $DB_TYPE"
echo "   - 数据库名称: $MYSQL_NAME"
echo "   - 容器端口: $MYSQL_PORT"
echo "   - 用户: $MYSQL_USER"
echo "-------------------------------------"


# --- 3. 停止并删除同名旧的独立 MySQL 容器 ---
echo "--- 2. 正在检查并停止/删除旧的独立 MySQL 容器 ($CONTAINER_NAME)..."
docker stop "$CONTAINER_NAME" > /dev/null 2>&1
docker rm "$CONTAINER_NAME" > /dev/null 2>&1
echo "   - 旧容器清理完成。"


# --- 4. 部署并启动新的独立 MySQL 容器 ---
echo "--- 3. 正在拉取和启动 MySQL 容器 ($CONTAINER_NAME)..."

# 注意：这里我们移除 MYSQL_USER，解决与 MYSQL_ROOT_PASSWORD 的冲突
# 但保留 MYSQL_PASSWORD，用于设置 root 密码，因为 .env 中 MYSQL_USER=root
docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$MYSQL_PORT":3306 \
    -e MYSQL_ROOT_PASSWORD="$MYSQL_PASSWORD" \
    -e MYSQL_DATABASE="$MYSQL_NAME" \
    --restart unless-stopped \
    "$MYSQL_IMAGE" \
    # --default-authentication-plugin=mysql_native_password

if [ $? -eq 0 ]; then
    echo "   - MySQL 容器启动成功！"
else
    echo "错误：MySQL 容器启动失败，请检查 Docker 日志。"
    exit 1
fi

# --- 5. 启动应用容器 (使用 docker compose) ---
echo "--- 4. 等待 MySQL 启动 (15秒)..."
sleep 15 
echo "--- 5. 正在通过 docker compose 启动应用服务..."

# 检查 Compose 命令
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif command -v docker compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "致命错误：未找到 'docker-compose' 或 'docker compose' 命令。请先安装 Docker Compose 工具。"
    exit 1
fi

# 增加的步骤：清理旧的 Compose 服务
echo "   - 正在清理旧的 Compose 服务（停止并移除容器/网络/卷）..."
# 使用 -v 移除数据卷，确保全新部署，但请注意这会清除之前的数据卷数据！
$COMPOSE_CMD -f "$COMPOSE_FILE" down -v

# 启动服务
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d

if [ $? -eq 0 ]; then
    echo "   - 应用服务已通过 $COMPOSE_CMD 后台启动成功！"
else
    echo "错误：应用服务启动失败。请检查 $COMPOSE_FILE 配置和 Docker 日志。"
fi

echo "--- 部署脚本执行完毕 ---"