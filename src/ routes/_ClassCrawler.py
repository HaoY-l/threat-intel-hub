from abc import ABC, abstractmethod

class ClassCrawler(ABC):
    def __init__(self, time=15):
        self.timeout = time
    
    @abstractmethod
    def name(self) -> str:
        """Return the name of the crawler."""
    pass

    @abstractmethod
    def source_url(self) -> str:
        """Return the source URL of the crawler.""" 
        pass

    @abstractmethod
    def crawl(self) -> list:
        """
        抓取方法，返回 List[dict]，每条是一个 CVE 字典：
        {
            "cve_id": "CVE-2025-12345",
            "title": "漏洞标题",
            "published": "2025-07-10",
            "source": "CNNVD",
            "severity": "高危",
            "url": "https://...链接",
            "description": "描述内容"
        }
        """
        pass