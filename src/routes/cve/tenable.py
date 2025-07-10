#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : Haoyu
# @Time   : 2025/07/10 15:03
# @File   : tenable.py

from ._BaseCrawler import BaseCrawler
import requests
import re
from lxml import etree
from datetime import datetime

class TenableCrawler(BaseCrawler):

    def name(self) -> str:
        return "Tenable (Nessus)"

    def source_url(self) -> str:
        return "https://www.tenable.com/cve/feeds?sort=newest"
    
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }

    def crawl(self) -> list:
        url = self.source_url()
        try:
            response = requests.get(
                url,
                headers=self.headers(),
                timeout=self.timeout
            )
        except Exception as e:
            print(f"[{self.name()}] 抓取失败: {e}")
            return []

        cves = []

        if response.status_code == 200:
            # Tenable 返回的是 RSS Feed，有 XML 头（需跳过第一行处理）
            data = ''.join(response.text.split('\n')[1:])
            rss = etree.XML(data)
            items = rss.xpath("//item")

            for item in items[:10]:  # 限制抓取数量
                cve_id = item.xpath("./title")[0].text.strip()
                url = item.xpath("./link")[0].text.strip()
                pub_date = item.xpath("./pubDate")[0].text.strip()
                try:
                    published = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
                except:
                    published = ""

                desc_raw = item.xpath("./description")[0].text or ""
                desc_raw = desc_raw.replace('\r', '').replace('\n', '')
                match = re.findall(r'Description</h3>\s*<p>(.*?)</p>', desc_raw, re.DOTALL)
                description = match[0].strip() if match else ""

                # 组装标准输出格式
                cves.append({
                    "cve_id": cve_id,
                    "title": description[:100] if description else cve_id,
                    "published": published,
                    "source": self.name(),
                    "severity": "",  # Tenable 没有提供直接 severity 字段
                    "url": url,
                    "description": description
                })
        else:
            print(f"[{self.name()}] 抓取失败：HTTP {response.status_code}")

        return cves
