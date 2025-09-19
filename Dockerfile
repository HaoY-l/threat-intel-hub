# ========= 基础镜像 =========
FROM python:3.11-slim AS backend

# 设置工作目录
WORKDIR /app

# 安装系统依赖（构建前端需要 node）
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    git \
    npm \
    && rm -rf /var/lib/apt/lists/*

# ========= 安装 Python 依赖 =========
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ========= 构建前端 =========
COPY threat_intel_front ./threat_intel_front
WORKDIR /app/threat_intel_front
RUN npm install && npm run build

# ========= 拷贝前端静态资源 =========
WORKDIR /app
COPY . .
RUN mkdir -p src/static && rm -rf src/static/* \
    && cp -r threat_intel_front/dist/* src/static/

# ========= 启动命令 =========
EXPOSE 8891
CMD ["gunicorn", "-b", "0.0.0.0:8891", "app:app"]
