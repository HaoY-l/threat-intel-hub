import requests,os,json,logging,sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from ._BaseThreat import ThreatIntelCollector  # 确保路径正确
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from data.db_init import get_db_connection  # 确保路径正确

load_dotenv()

class OtxCollector(ThreatIntelCollector):
    def __init__(self):
        """初始化 OTXCollector，设置 API 密钥和基础 URL"""
        self.api_key = os.getenv("otx_api_key")
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.headers = {
            "accept": "application/json",
            "X-OTX-API-KEY": self.api_key
        }
        self.conn = None

    def name(self) -> str:
        """返回平台名称"""
        return "AlienVault OTX"

    def query_ip(self, ip: str) -> dict:
        """查询 IP 的情报信息"""
        url = f"{self.base_url}/indicators/IPv4/{ip}/general"
        return self._get(url)

    def query_url(self, url: str) -> dict:
        """查询 URL 的情报信息（不主动请求目标 URL）"""
        try:
            # URL 编码避免路径参数导致接口异常
            encoded_url = requests.utils.quote(url, safe='')
            otx_url = f"{self.base_url}/indicators/url/{encoded_url}/general"
            return self._get(otx_url)
        except Exception as e:
            logging.error(f"平台{self.name()} 解析 URL 时异常: {url} - {e}")
            return {"error": str(e)}

    def query_file(self, file_hash: str) -> dict:
        """查询文件哈希的情报信息（支持 MD5、SHA1、SHA256）"""
        # 根据哈希长度确定类型
        hash_length = len(file_hash)
        if hash_length == 32:
            hash_type = "MD5"
        elif hash_length == 40:
            hash_type = "SHA1"
        elif hash_length == 64:
            hash_type = "SHA256"
        else:
            logging.error(f"平台{self.name()}Invalid hash length for {file_hash}. Must be 32 (MD5), 40 (SHA1), or 64 (SHA256).")
            return {"error": "Invalid hash length. Must be 32 (MD5), 40 (SHA1), or 64 (SHA256)."}

        url = f"{self.base_url}/indicators/file/{file_hash}/general"
        return self._get(url)

    def _get(self, url: str) -> dict:
        """通用 GET 请求方法"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logging.error(f"平台{self.name()}Error querying {url}: {e}")
            return {"error": str(e)}

    def connect_to_db(self):
        """连接到 MySQL 数据库"""
        if self.conn is None:
            self.conn = get_db_connection()

    def save_to_db(self, data: dict) -> bool:
        self.connect_to_db()

        # 直接用顶层字段，不从 data['data']
        data_obj = data

        # 唯一 ID，优先用 indicator 字符串，如果没有，则尝试 base_indicator.id（数字）
        target_id = data_obj.get('indicator') or str(data_obj.get('base_indicator', {}).get('id'))
        if not target_id:
            logging.error(f"平台{self.name()}数据对象中缺少 'indicator' 或 'base_indicator.id' 字段")
            return False

        # 类型字段小写化
        type_ = data_obj.get('type', '').lower()
        source = self.name()

        # 属性数据直接用顶层字段
        attributes = data_obj

        # 统一将完整 JSON 字符串存 details
        details_json = json.dumps(data, ensure_ascii=False)

        with self.conn.cursor() as cursor:

            if type_ in ['ipv4', 'ip_address', 'ip']:
                reputation_score = attributes.get('reputation', 0)

                if reputation_score > 0:
                    threat_level = 'low'
                elif reputation_score == 0:
                    threat_level = 'medium'
                else:
                    reputation_score = 'high'

                # OTX返回的时间字段不固定，尝试用 modified 或 None
                last_update_ts = attributes.get('modified')
                last_update = None
                if last_update_ts:
                    try:
                        # 可能是时间戳或 ISO8601字符串
                        if isinstance(last_update_ts, int):
                            last_update = datetime.fromtimestamp(last_update_ts)
                        else:
                            last_update = datetime.fromisoformat(last_update_ts.replace('Z', '+00:00'))
                    except Exception:
                        last_update = None
                # 如果最终没有拿到时间，使用当前时间
                if last_update is None:
                    last_update = datetime.now(timezone.utc)
                cursor.execute("SELECT id FROM ip_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:
                    cursor.execute(
                        """
                        INSERT INTO ip_threat_intel (id, type, source, reputation_score, threat_level, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, 'ip', source, reputation_score, threat_level, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的IP数据 {target_id} 已插入")
                else:
                    cursor.execute(
                        """
                        UPDATE ip_threat_intel
                        SET reputation_score=%s, threat_level=%s, last_update=%s, details=%s, updated_at=CURRENT_TIMESTAMP
                        WHERE id=%s AND source=%s
                        """,
                        (reputation_score, threat_level, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的IP数据 {target_id} 已更新")

            elif type_ == 'url':
                reputation_score = attributes.get('reputation', 0)

                # URL 可能在 base_indicator.indicator 或 attributes.url
                target_url = attributes.get('url') or data_obj.get('base_indicator', {}).get('indicator') or ''

                last_update_ts = attributes.get('modified')
                last_update = None
                if last_update_ts:
                    try:
                        if isinstance(last_update_ts, int):
                            last_update = datetime.fromtimestamp(last_update_ts)
                        else:
                            last_update = datetime.fromisoformat(last_update_ts.replace('Z', '+00:00'))
                    except Exception:
                        last_update = None
                # 如果最终没有拿到时间，使用当前时间
                if last_update is None:
                    last_update = datetime.now(timezone.utc)
                cursor.execute("SELECT id FROM url_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:
                    cursor.execute(
                        """
                        INSERT INTO url_threat_intel (id, type, source, target_url, reputation_score, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, 'url', source, target_url, reputation_score, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的URL数据 {target_url} 已插入")
                else:
                    cursor.execute(
                        """
                        UPDATE url_threat_intel
                        SET target_url=%s, reputation_score=%s, last_update=%s, details=%s, updated_at=CURRENT_TIMESTAMP
                        WHERE id=%s AND source=%s
                        """,
                        (target_url, reputation_score, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的URL数据 {target_url} 已更新")

            elif type_ == 'file' or type_ in ['sha256']:
                reputation_score = attributes.get('reputation', 0)
                analysis_stats = attributes.get('last_analysis_stats', {})
                malicious_count = analysis_stats.get('malicious', 0)

                if malicious_count < 0:
                    threat_level = 'high'
                elif malicious_count == 0:
                    threat_level = 'medium'
                else:
                    threat_level = 'low'

                last_update_ts = attributes.get('last_analysis_date')
                last_update = None
                if last_update_ts:
                    try:
                        if isinstance(last_update_ts, int):
                            last_update = datetime.fromtimestamp(last_update_ts)
                        else:
                            last_update = datetime.fromisoformat(last_update_ts.replace('Z', '+00:00'))
                    except Exception:
                        last_update = None
                # 如果最终没有拿到时间，使用当前时间
                if last_update is None:
                    last_update = datetime.now(timezone.utc)
                cursor.execute("SELECT id FROM file_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:
                    cursor.execute(
                        """
                        INSERT INTO file_threat_intel (id, type, source, reputation_score, threat_level, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, 'file', source, reputation_score, threat_level, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的文件数据 {target_id} 已插入")
                else:
                    cursor.execute(
                        """
                        UPDATE file_threat_intel
                        SET reputation_score=%s, threat_level=%s, last_update=%s, details=%s, updated_at=CURRENT_TIMESTAMP
                        WHERE id=%s AND source=%s
                        """,
                        (reputation_score, threat_level, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的文件数据 {target_id} 已更新")

            else:
                logging.error(f"平台{self.name()}的不支持的类型: {type_}")
                return False

            self.conn.commit()
            return True
