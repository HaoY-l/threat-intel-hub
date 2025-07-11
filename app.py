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
    print(f"抓取到 {len(alicloud_results)} 条漏洞数据")

    # 这里可以继续抓取其它爬虫
    # tenable_crawler = TenableCrawler()
    # tenable_results = tenable_crawler.crawl()
    # for item in tenable_results:
    #     print(f"{item['cve_id']} | {item['title']} | {item['published']}")


def run_threat():
    virustotal_threat = VirusTotalCollector()
    # 抓取 VirusTotal IP威胁情报数据
    ip = virustotal_threat.query_ip("87.236.176.190")
    virustotal_threat.save_to_db(ip)

    # 抓取 VirusTotal URL威胁情报数据
    url = virustotal_threat.query_url("http://truewarstoriespodcast.com/")
    virustotal_threat.save_to_db(url)

    # 抓取 VirusTotal File威胁情报数据
    file = virustotal_threat.query_file("1fcfdbc8ec322580f0c293aa35e414d4a0668f827fe61237049be1845ad33fbd")
    virustotal_threat.save_to_db(file)
    pass



# ---------------- 启动定时任务调度器 ---------------- #
scheduler = BackgroundScheduler()
scheduler.add_job(run_cve, 'interval', hours=3, id='cve_task')
scheduler.start()


@app.route('/')
def index():
    
    return jsonify({'message': 'Threat API is up and running'})

if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=5001)
