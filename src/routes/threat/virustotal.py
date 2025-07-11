import requests
import os, json,logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ._BaseThreat import ThreatIntelCollector  # 确保路径正确
from data.db_init import get_db_connection  # 确保路径正确

load_dotenv()

class VirusTotalCollector(ThreatIntelCollector):
    def __init__(self):
        self.api_key = os.getenv("virustotal_api_key")
        self.base_url = "https://www.virustotal.com/api/v3"
        self.headers = {
            "accept": "application/json",
            "x-apikey": self.api_key
        }
        self.conn = None

    def name(self) -> str:
        return "VirusTotal"

    def query_ip(self, ip: str) -> dict:
        url = f"{self.base_url}/ip_addresses/{ip}"
        return self._get(url)

    def query_url(self, url_str: str) -> dict:
        import base64
        encoded_url = base64.urlsafe_b64encode(url_str.encode()).decode().strip("=")
        url = f"{self.base_url}/urls/{encoded_url}"
        return self._get(url)

    def query_file(self, file_hash: str) -> dict:
        url = f"{self.base_url}/files/{file_hash}"
        return self._get(url)

    def _get(self, url: str) -> dict:
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def connect_to_db(self):
        if self.conn is None:
            self.conn = get_db_connection()

    def save_to_db(self, data: dict) -> bool:
        self.connect_to_db()

        data_obj = data.get('data', {})
        target_id = data_obj.get('id')
        target_url = data_obj.get('attributes', {}).get('url', '')
        if not target_id:
            logging.error(f"平台{self.name()}数据对象中缺少 'id' 字段")
            return False

        type_ = data_obj.get('type', 'default')
        source = self.name()
        attributes = data_obj.get('attributes', {})
        details_json = json.dumps(data, ensure_ascii=False)

        with self.conn.cursor() as cursor:
            if type_ == 'ip_address':
                reputation_score = attributes.get('reputation', 0)
                threat_level = None  # 可自定义威胁等级
                last_update_ts = attributes.get('last_analysis_date')
                last_update = datetime.fromtimestamp(last_update_ts) if last_update_ts else None

                cursor.execute("SELECT id FROM ip_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:  # 修复：只有当记录不存在时才插入
                    cursor.execute(
                        """
                        INSERT INTO ip_threat_intel (id, type, source, reputation_score, threat_level, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, type_, source, reputation_score, threat_level, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的IP数据{target_id}已插入")
                else:
                    # 如果记录存在，更新数据
                    cursor.execute(
                        """
                        UPDATE ip_threat_intel 
                        SET reputation_score=%s, threat_level=%s, last_update=%s, details=%s 
                        WHERE id=%s AND source=%s
                        """,
                        (reputation_score, threat_level, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的IP数据{target_id}已更新")

            elif type_ == 'url':
                reputation_score = attributes.get('reputation', 0)
                last_update_ts = attributes.get('last_analysis_date') or attributes.get('last_modification_date')
                last_update = datetime.fromtimestamp(last_update_ts) if last_update_ts else None
                target_url = attributes.get('url') or attributes.get('last_final_url') or ''

                cursor.execute("SELECT id FROM url_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:  # 修复：只有当记录不存在时才插入
                    cursor.execute(
                        """
                        INSERT INTO url_threat_intel (id, type, source, target_url, reputation_score, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, type_, source, target_url, reputation_score, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的URL数据 {target_url} 已插入")
                else:
                    # 如果记录存在，更新数据
                    cursor.execute(
                        """
                        UPDATE url_threat_intel 
                        SET target_url=%s, reputation_score=%s, last_update=%s, details=%s 
                        WHERE id=%s AND source=%s
                        """,
                        (target_url, reputation_score, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的URL数据 {target_url} 已更新")

            elif type_ == 'file':
                reputation_score = attributes.get('reputation', 0)
                
                # 根据恶意检测数量设置威胁等级
                analysis_stats = attributes.get('last_analysis_stats', {})
                malicious_count = analysis_stats.get('malicious', 0)
                if malicious_count > 5:
                    threat_level = 'high'
                elif malicious_count > 0:
                    threat_level = 'medium'
                else:
                    threat_level = 'low'
                
                # 最后分析时间
                last_update_ts = attributes.get('last_analysis_date')
                last_update = datetime.fromtimestamp(last_update_ts) if last_update_ts else None

                cursor.execute("SELECT id FROM file_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:  # 修复：只有当记录不存在时才插入
                    cursor.execute(
                        """
                        INSERT INTO file_threat_intel (id, type, source, reputation_score, threat_level, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, type_, source, reputation_score, threat_level, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的文件数据 {target_id} 已插入")
                else:
                    # 如果记录存在，更新数据
                    cursor.execute(
                        """
                        UPDATE file_threat_intel 
                        SET reputation_score=%s, threat_level=%s, last_update=%s, details=%s 
                        WHERE id=%s AND source=%s
                        """,
                        (reputation_score, threat_level, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的文件数据 {target_id} 已更新")

            else:
                logging.info(f"平台{self.name()}的不支持的类型: {type_}")
                return False

            self.conn.commit()
            return True