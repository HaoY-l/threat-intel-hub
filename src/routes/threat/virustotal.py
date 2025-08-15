import requests
import os, json, logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ._BaseThreat import ThreatIntelCollector
from data.db_init import get_db_connection

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
        
        # 在返回结果中额外保存原始URL
        result = self._get(url)
        if result and not result.get('error'):
            result['original_url'] = url_str
        return result

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

    def calculate_reputation_score(self, attributes: dict, data_type: str) -> int:
        """
        重新计算reputation分值（简化版）
        
        Returns:
            int: reputation分值
            - 负数: 有风险
            - 0或正数: 无风险/低风险
        """
        score = 0
        
        # 基于检测引擎分析结果计算
        analysis_stats = attributes.get('last_analysis_stats', {})
        malicious = analysis_stats.get('malicious', 0)
        harmless = analysis_stats.get('harmless', 0)
        suspicious = analysis_stats.get('suspicious', 0)
        
        if data_type == 'file':
            # 文件类型：主要看恶意检测数量和YARA规则
            score -= malicious * 3  # 每个恶意检测 -3分
            score -= suspicious * 1  # 每个可疑检测 -1分
            score += harmless * 1   # 每个良性检测 +1分
            
            # YARA规则匹配
            yara_count = len(attributes.get('crowdsourced_yara_results', []))
            score -= yara_count * 10  # 每个YARA规则 -10分
            
        elif data_type == 'ip_address':
            # IP地址类型
            score -= malicious * 5   # 每个恶意检测 -5分  
            score -= suspicious * 2  # 每个可疑检测 -2分
            score += harmless * 1    # 每个良性检测 +1分
            
        elif data_type == 'url':
            # URL类型
            score -= malicious * 4   # 每个恶意检测 -4分
            score -= suspicious * 2  # 每个可疑检测 -2分  
            score += harmless * 1    # 每个良性检测 +1分
        
        return score

    def connect_to_db(self):
        if self.conn is None:
            self.conn = get_db_connection()

    def save_to_db(self, data: dict) -> bool:
        self.connect_to_db()

        data_obj = data.get('data', {})
        
        # --- 修改开始 ---
        # 对于 URL 类型，id和target_url都存入用户输入的原始 URL
        original_url = data.get('original_url')
        if original_url:
            target_id = original_url
            target_url = original_url
        else:
            # 非 URL 类型或没有原始 URL 数据时，使用原逻辑
            target_id = data_obj.get('id')
            target_url = data_obj.get('attributes', {}).get('url', '')

        if not target_id:
            logging.error(f"平台{self.name()}数据对象中缺少 'id' 字段或原始URL")
            return False
        # --- 修改结束 ---

        type_ = data_obj.get('type', 'default')
        source = self.name()
        attributes = data_obj.get('attributes', {})
        details_json = json.dumps(data, ensure_ascii=False)
        
        # 重新计算reputation分值
        reputation_score = self.calculate_reputation_score(attributes, type_)

        with self.conn.cursor() as cursor:
            if type_ == 'ip_address':
                # 根据重新计算的reputation分值设置威胁等级
                if reputation_score >= 0:
                    threat_level = 'low'
                else:
                    threat_level = 'high'
                    
                last_update_ts = attributes.get('last_analysis_date')
                type_ = 'ip'  # 确保类型一致
                last_update = datetime.fromtimestamp(last_update_ts) if last_update_ts else None

                cursor.execute("SELECT id FROM ip_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:
                    cursor.execute(
                        """
                        INSERT INTO ip_threat_intel (id, type, source, reputation_score, threat_level, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, type_, source, reputation_score, threat_level, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的IP数据{target_id}已插入，重新计算的reputation: {reputation_score}")
                else:
                    cursor.execute(
                        """
                        UPDATE ip_threat_intel 
                        SET reputation_score=%s, threat_level=%s, last_update=%s, details=%s 
                        WHERE id=%s AND source=%s
                        """,
                        (reputation_score, threat_level, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的IP数据{target_id}已更新，重新计算的reputation: {reputation_score}")

            elif type_ == 'url':
                # 根据重新计算的reputation分值设置威胁等级
                if reputation_score >= 0:
                    threat_level = 'low'
                else:
                    threat_level = 'high'
                    
                last_update_ts = attributes.get('last_analysis_date') or attributes.get('last_modification_date')
                last_update = datetime.fromtimestamp(last_update_ts) if last_update_ts else None
                
                cursor.execute("SELECT id FROM url_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:
                    cursor.execute(
                        """
                        INSERT INTO url_threat_intel (id, type, source, target_url, reputation_score, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, type_, source, target_url, reputation_score, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的URL数据 {target_url} 已插入，重新计算的reputation: {reputation_score}")
                else:
                    cursor.execute(
                        """
                        UPDATE url_threat_intel 
                        SET target_url=%s, reputation_score=%s, last_update=%s, details=%s 
                        WHERE id=%s AND source=%s
                        """,
                        (target_url, reputation_score, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的URL数据 {target_url} 已更新，重新计算的reputation: {reputation_score}")

            elif type_ == 'file':
                # 根据重新计算的reputation分值设置威胁等级
                if reputation_score >= 0:
                    threat_level = 'low'
                else:
                    threat_level = 'high'
                    
                last_update_ts = attributes.get('last_analysis_date')
                last_update = datetime.fromtimestamp(last_update_ts) if last_update_ts else None

                cursor.execute("SELECT id FROM file_threat_intel WHERE id=%s AND source=%s", (target_id, source))
                row = cursor.fetchone()

                if not row:
                    cursor.execute(
                        """
                        INSERT INTO file_threat_intel (id, type, source, reputation_score, threat_level, last_update, details)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (target_id, type_, source, reputation_score, threat_level, last_update, details_json)
                    )
                    logging.info(f"平台{self.name()}的文件数据 {target_id} 已插入，重新计算的reputation: {reputation_score}")
                else:
                    cursor.execute(
                        """
                        UPDATE file_threat_intel 
                        SET reputation_score=%s, threat_level=%s, last_update=%s, details=%s 
                        WHERE id=%s AND source=%s
                        """,
                        (reputation_score, threat_level, last_update, details_json, target_id, source)
                    )
                    logging.info(f"平台{self.name()}的文件数据 {target_id} 已更新，重新计算的reputation: {reputation_score}")

            else:
                logging.info(f"平台{self.name()}的不支持的类型: {type_}")
                return False

            self.conn.commit()
            return True