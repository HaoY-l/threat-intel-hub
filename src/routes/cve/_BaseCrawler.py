from abc import ABC, abstractmethod
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

class BaseCrawler(ABC):
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.conn = self.get_db_connection()

    def get_db_connection(self):
        return pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_NAME"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def source_url(self) -> str:
        pass

    @abstractmethod
    def crawl(self) -> list:
        """返回字典列表，每个是漏洞信息"""
        pass

    def save_items(self, items: list):
        """
        保存数据，字段缺失时用空字符串或默认值代替。
        """
        sql = """
        INSERT INTO cve_data (cve_id, title, published, source, severity, url, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        title=VALUES(title),
        published=VALUES(published),
        source=VALUES(source),
        severity=VALUES(severity),
        url=VALUES(url),
        description=VALUES(description),
        updated_at=CURRENT_TIMESTAMP
        """
        with self.conn.cursor() as cursor:
            data = []
            for item in items:
                cve_id = item.get('cve_id', '') or ''
                title = item.get('title', '') or ''
                published = item.get('published')
                if published is None:
                    published = '1970-01-01'  # 这里默认一个很早的时间
                source = item.get('source', '') or ''
                severity = item.get('severity', '') or ''
                url = item.get('url', '') or ''
                description = item.get('description', '') or ''

                data.append((
                    cve_id,
                    title,
                    published,
                    source,
                    severity,
                    url,
                    description,
                ))
            cursor.executemany(sql, data)
