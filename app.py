#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : Haoyu

from flask import Flask, jsonify, request, send_from_directory, g
from apscheduler.schedulers.background import BackgroundScheduler
from data.db_init import create_database_and_tables
from src.api import api_bp
from src.routes.cve.tenable import TenableCrawler
from src.routes.cve.alicloud import AliyunAVDCrawler
from src.routes.waf.save_log import fetch_and_save_blocked_ips, fetch_and_save_ip_request_frequency
from src.routes.waf.protected_ip import protected_ip_task
import logging, os, jwt
from dotenv import load_dotenv
from flask_cors import CORS
import atexit
import datetime
from src.api.phishing_email import phishing_bp, init_phishing

# casbin 相关 - 只导入函数，不立即初始化
from src.utils.casbin_init import init_casbin
from src.utils.casbin_adapter import DatabaseAdapter

load_dotenv()

# -----------------------------------------------------------
# 日志配置
# -----------------------------------------------------------
handlers = [
    logging.FileHandler(os.getenv('file_log', 'app.log'), encoding="utf-8"),
    logging.StreamHandler()
]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=handlers
)

app = Flask(__name__, static_folder='src/static', static_url_path='/')

# CORS
CORS(app,
     resources={r"/api/*": {"origins": "http://localhost:5173"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# -----------------------------------------------------------
# Casbin 初始化 - 延迟到数据库初始化之后
# -----------------------------------------------------------
casbin_enforcer = None  # 先设为None
db_adapter = None


# -----------------------------------------------------------
# Casbin 自定义中间件（最新版推荐写法）
# -----------------------------------------------------------
@app.before_request
def casbin_auth_middleware():
    # 如果Casbin还未初始化，跳过权限检查
    if casbin_enforcer is None or db_adapter is None:
        return
        
    path = request.path
    method = request.method

    # 白名单直接放行
    if any(path.startswith(w) for w in db_adapter.get_permission_white_list()):
        return

    # 解析 token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_role = "anonymous"

    if token:
        try:
            SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})
            user_role = payload.get("role", "user")
            g.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"code": 401, "msg": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"code": 401, "msg": "Invalid Token"}), 401

    # 从数据库解析接口对应权限 key
    permission_key = db_adapter.get_permission_key_by_route(path, method)
    if not permission_key:
        return jsonify({"code": 403, "msg": "此接口未设置权限，拒绝访问"}), 403

    # Casbin 校验
    allowed = casbin_enforcer.enforce(user_role, permission_key, method)
    if not allowed:
        return jsonify({"code": 403, "msg": "权限不足"}), 403


# -----------------------------------------------------------
# 蓝图注册
# -----------------------------------------------------------
app.register_blueprint(api_bp)
app.register_blueprint(phishing_bp)


# -----------------------------------------------------------
# 各类错误处理
# -----------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": request.url}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed"}), 405


@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception(e)
    return jsonify({"error": "Internal Error"}), 500


# -----------------------------------------------------------
# 静态页面
# -----------------------------------------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # API路由不处理，交给蓝图
    if path.startswith('api/'):
        return jsonify({"error": "Not Found"}), 404
    
    # 静态资源直接返回
    if path and '.' in path:
        return send_from_directory(app.static_folder, path)
    
    # 其他所有路由返回 index.html（前端路由）
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})



# -----------------------------------------------------------
# 定时任务封装
# -----------------------------------------------------------
def run_cve_in_context():
    with app.app_context():
        try:
            crawler = AliyunAVDCrawler()
            results = crawler.crawl()
            logging.info(f"阿里云 AVD 数量: {len(results)}")
        except Exception as e:
            logging.error(f"CVE 抓取失败: {e}")


def fetch_and_save_blocked_ips_in_context():
    with app.app_context():
        fetch_and_save_blocked_ips()


def fetch_and_save_ip_request_frequency_in_context():
    with app.app_context():
        fetch_and_save_ip_request_frequency()


def protected_ip_task_in_context():
    with app.app_context():
        protected_ip_task()


# -----------------------------------------------------------
# 主入口
# -----------------------------------------------------------
if __name__ == '__main__':
    scheduler = None
    
    # 1. 先初始化数据库
    logging.info("开始初始化数据库...")
    create_database_and_tables()
    logging.info("✓ 数据库初始化完成")

    # 2. 再初始化 Casbin（现在表已存在）
    logging.info("开始初始化 Casbin...")
    casbin_enforcer = init_casbin()
    db_adapter = DatabaseAdapter()
    logging.info("✓ Casbin 初始化完成")

    # 3. 初始化钓鱼邮件模块
    init_phishing()

    try:
        with app.app_context():
            run_cve_in_context()
            fetch_and_save_blocked_ips_in_context()
            fetch_and_save_ip_request_frequency_in_context()
            protected_ip_task_in_context()

        scheduler = BackgroundScheduler()
        scheduler.add_job(run_cve_in_context, 'interval', hours=3)
        scheduler.add_job(fetch_and_save_blocked_ips_in_context, 'interval', minutes=15)
        scheduler.add_job(fetch_and_save_ip_request_frequency_in_context, 'interval', minutes=1)
        scheduler.add_job(protected_ip_task_in_context, 'interval', minutes=1)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

    except Exception as e:
        logging.error("调度器启动失败: %s", e)

    logging.info("启动 Flask 应用（Casbin 权限控制已启用）")
    app.run(debug=True, host='0.0.0.0', port=8891, threaded=True)