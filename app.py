#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : Haoyu
# @Time   : 2025/07/11 14:10
# @File   : app.py
# -----------------------------------------------
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from data.db_init import create_database_and_tables
from src.api import api_bp
from src.routes.cve.tenable import TenableCrawler 
from src.routes.cve.alicloud import AliyunAVDCrawler 
from src.routes.threat.virustotal import VirusTotalCollector
import logging,os 
from dotenv import load_dotenv
# -----------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',filename=os.getenv('file_log'), filemode='a', encoding='utf-8')

app = Flask(__name__)
app.register_blueprint(api_bp)

# 初始化数据库

create_database_and_tables()
def run_cve():
    # 抓取阿里云 AVD 漏洞数据
    alicloud_crawler = AliyunAVDCrawler()
    alicloud_results = alicloud_crawler.crawl()
    logging.info(f"抓取到 {len(alicloud_results)} 条漏洞数据")

    # 这里可以继续抓取其它爬虫
    # tenable_crawler = TenableCrawler()
    # tenable_results = tenable_crawler.crawl()
    # for item in tenable_results:
    #     print(f"{item['cve_id']} | {item['title']} | {item['published']}")

# ---------------- 启动定时任务调度器 ---------------- #
run_cve()  # 启动时立即执行一次
scheduler = BackgroundScheduler()
scheduler.add_job(run_cve, 'interval', hours=3, id='cve_task')
scheduler.start()


@app.route('/')
def index():
    return jsonify({'message': 'Threat API is up and running'})

if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=5001)
