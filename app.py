#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : Haoyu
# @Time   : 2025/07/11 14:10
# @File   : app.py
# -----------------------------------------------
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from data.db_init import create_database_and_tables
from src.api import api_bp
from src.routes.cve.tenable import TenableCrawler 
from src.routes.cve.alicloud import AliyunAVDCrawler 
from src.routes.threat.virustotal import VirusTotalCollector
import logging, os 
from dotenv import load_dotenv
from flask_cors import CORS
import atexit

# -----------------------------------------------
load_dotenv()

# 配置日志
log_file = os.getenv('file_log', 'app.log')
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

app = Flask(__name__)

# 更完整的CORS配置
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})

# 注册蓝图
app.register_blueprint(api_bp)

# 初始化数据库
try:
    create_database_and_tables()
    logging.info("数据库初始化成功")
except Exception as e:
    logging.error(f"数据库初始化失败: {e}")

def run_cve():
    """CVE数据抓取任务"""
    try:
        # 抓取阿里云 AVD 漏洞数据
        alicloud_crawler = AliyunAVDCrawler()
        alicloud_results = alicloud_crawler.crawl()
        logging.info(f"抓取到 {len(alicloud_results)} 条漏洞数据")

        # 这里可以继续抓取其它爬虫
        # tenable_crawler = TenableCrawler()
        # tenable_results = tenable_crawler.crawl()
        # for item in tenable_results:
        #     print(f"{item['cve_id']} | {item['title']} | {item['published']}")
        
    except Exception as e:
        logging.error(f"CVE爬取失败: {e}")

# 错误处理
@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal Server Error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error),
        'status': 'error'
    }), 500

@app.errorhandler(404)
def not_found(error):
    logging.error(f"Not Found: {request.url}")
    return jsonify({
        'error': 'Not Found',
        'message': f'请求的路径 {request.url} 不存在',
        'status': 'error'
    }), 404

@app.errorhandler(400)
def bad_request(error):
    logging.error(f"Bad Request: {error}")
    return jsonify({
        'error': 'Bad Request',
        'message': str(error),
        'status': 'error'
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    logging.error(f"Method Not Allowed: {request.method} {request.url}")
    return jsonify({
        'error': 'Method Not Allowed',
        'message': f'{request.method} 方法不被允许',
        'status': 'error'
    }), 405

# 处理CORS预检请求
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# 全局异常处理
@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception(f"未处理的异常: {e}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': '服务器内部错误',
        'status': 'error'
    }), 500

@app.route('/')
def index():
    return jsonify({
        'message': 'Threat Intelligence API is up and running',
        'status': 'success',
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    # 启动定时任务调度器
    scheduler = None
    try:
        run_cve()  # 启动时立即执行一次
        scheduler = BackgroundScheduler()
        scheduler.add_job(run_cve, 'interval', hours=3, id='cve_task')
        scheduler.start()
        logging.info("定时任务调度器启动成功")
        
        # 确保应用关闭时停止调度器
        atexit.register(lambda: scheduler.shutdown() if scheduler else None)
        
    except Exception as e:
        logging.error(f"调度器启动失败: {e}")
    
    # 启动Flask应用
    try:
        logging.info("启动Flask应用...")
        app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
    except Exception as e:
        logging.error(f"Flask应用启动失败: {e}")
        if scheduler:
            scheduler.shutdown()