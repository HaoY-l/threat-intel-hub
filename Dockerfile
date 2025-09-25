# ---- 基础镜像 ----
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（Python 扩展依赖）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端代码和前端静态文件
COPY app.py .
COPY src/ src/
COPY .env .
COPY data/ .

# 暴露端口
EXPOSE 8891

# 启动命令
CMD ["python", "app.py"]
