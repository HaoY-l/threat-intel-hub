#!/bin/bash

set -e  # 出错就终止脚本
echo "🚀 开始部署 Threat-Intel-Hub 项目..."

# === 1. 创建 Python 虚拟环境 ===
if [ ! -d "venv" ]; then
  echo "📦 创建 Python 虚拟环境 venv..."
  python3 -m venv venv
fi

echo "🐍 激活虚拟环境..."
source venv/bin/activate

# === 2. 安装 Python 依赖 ===
echo "📦 安装 Python 后端依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# === 3. 构建前端 ===
echo "🔨 构建前端项目..."
cd threat_intel_front
npm install
npm run build
cd ..

# === 4. 拷贝前端构建结果到 Flask 静态目录 ===
echo "📁 拷贝前端构建结果到 Flask 静态目录..."
mkdir -p src/static
rm -rf src/static/*
cp -r threat_intel_front/dist/* src/static/

# === 5. 启动 Flask 后端 ===
echo "🚀 启动 Flask 服务..."
export FLASK_APP=app.py
export FLASK_ENV=production
venv/bin/flask run --host=0.0.0.0 --port=8891
echo "✅ 部署完成！项目已启动在 http://localhost:8891"
