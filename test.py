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
import requests
from bs4 import BeautifulSoup
from datetime import datetime
# -----------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',filename=os.getenv('file_log'), filemode='a', encoding='utf-8')

app = Flask(__name__)
app.register_blueprint(api_bp)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
def crawl() -> list:
    url = 'https://avd.aliyun.com/'
    resp = requests.get(url,headers=headers, timeout=10)
    # print(resp.text)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []

    # 简单解析页面漏洞列表行
    rows = soup.select('table.table tbody tr')
    # print(rows)
    for tr in rows:
        tds = tr.find_all('td')
        cve_id_tag = tds[0].find('a')
        cve_id = cve_id_tag.text.strip() if cve_id_tag else ''
        title = tds[1].text.strip()
        published = tds[3].text.strip()
        source = "Aliyun AVD"
        severity = tds[4].text.strip() if len(tds) > 4 else ""
        url_detail = "https://avd.aliyun.com" + (cve_id_tag.get('href') if cve_id_tag else "")

        items.append({
            "cve_id": cve_id,
            "title": title,
            "published": datetime.strptime(published, "%Y-%m-%d").date() if published else None,
            "source": source,
            "severity": severity,
            "url": url_detail,
            "description": "",  # 可扩展后面爬详情页
        })


if __name__ == '__main__':
    crawl()  # 直接运行爬虫任务



