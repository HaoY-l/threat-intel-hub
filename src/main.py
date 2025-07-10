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
# -----------------------------------------------


def run():
    # 抓取阿里云 AVD 漏洞数据
    create_database_and_tables()  # 启动时检查并初始化数据库表结构

    crawler = AliyunAVDCrawler()
    results = crawler.crawl()
    print(f"抓取到 {len(results)} 条漏洞数据")

    # 这里可以继续抓取其它爬虫
    # tenable_crawler = TenableCrawler()
    # tenable_results = tenable_crawler.crawl()
    # for item in tenable_results:
    #     print(f"{item['cve_id']} | {item['title']} | {item['published']}")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(run, 'interval', hours=3)  # 每3小时执行一次
    print("定时任务启动，每3小时执行一次run()")
    run()  # 启动时先执行一次
    scheduler.start()
