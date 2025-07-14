from ._BaseCrawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class AliyunAVDCrawler(BaseCrawler):
    def name(self) -> str:
        return "Aliyun AVD"

    def source_url(self) -> str:
        return "https://avd.aliyun.com/"

    def clear_source_data(self):
        """删除当前来源的旧数据"""
        try:
            with self.conn.cursor() as cursor:
                sql = "DELETE FROM cve_data WHERE source = %s"
                cursor.execute(sql, (self.name(),))
            self.conn.commit()
        except Exception as e:
            print(f"[!] 清理旧数据失败: {e}")

    def crawl(self) -> list:
        # 先清理旧数据
        self.clear_source_data()

        url = self.source_url()
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = []

        # 简单解析页面漏洞列表行
        rows = soup.select('table.table tbody tr')
        for tr in rows:
            tds = tr.find_all('td')
            cve_id_tag = tds[0].find('a')
            cve_id = cve_id_tag.text.strip() if cve_id_tag else ''
            title = tds[1].text.strip()
            published = tds[3].text.strip()
            source = self.name()
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

        # 存入数据库
        self.save_items(items)
        return items
