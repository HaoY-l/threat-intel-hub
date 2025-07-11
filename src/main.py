#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : Haoyu
# @Time   : 2025/07/10 15:18
# @File   : main.py
# -----------------------------------------------
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apscheduler.schedulers.blocking import BlockingScheduler
from data.db_init import create_database_and_tables
from routes.cve.tenable import TenableCrawler 
from routes.cve.alicloud import AliyunAVDCrawler 

from routes.threat._BaseThreat import ThreatIntelCollector
from routes.threat.virustotal import VirusTotalCollector
# -----------------------------------------------


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

if __name__ == '__main__':
    create_database_and_tables()  # 启动时检查并初始化数据库表结构
    # # 启动cve定时任务
    # scheduler = BlockingScheduler()
    # scheduler.add_job(run_cve, 'interval', hours=3)  # 每3小时执行一次
    # print("定时任务启动，每3小时执行一次run()")
    # run_cve()  # 启动时先执行一次
    # scheduler.start()

    # 启动threat定时任务
    # run_threat()
    # run_cve()
    pass
