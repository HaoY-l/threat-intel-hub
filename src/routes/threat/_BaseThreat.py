from abc import ABC, abstractmethod

class ThreatIntelCollector(ABC):
    @abstractmethod
    def name(self) -> str:
        """平台名称"""
        pass

    @abstractmethod
    def query_ip(self, ip: str) -> dict:
        """查询 IP 的情报信息"""
        pass

    @abstractmethod
    def query_url(self, url: str) -> dict:
        """查询 URL 的情报信息"""
        pass

    @abstractmethod
    def query_file(self, file_hash: str) -> dict:
        """查询文件哈希的情报信息"""
        pass
    
    @abstractmethod
    def connect_to_db(self):
        """连接到数据库"""
        pass

    @abstractmethod
    def save_to_db(self, data: dict) -> bool:
        """保存情报数据到数据库"""
        pass
    