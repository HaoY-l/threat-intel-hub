from flask import Blueprint, request, jsonify
from src.routes.threat.virustotal import VirusTotalCollector
from src.routes.threat.otx import OtxCollector
from data.db_init import get_db_connection
import datetime
import logging
import urllib.parse
import json
import re

query_bp = Blueprint('query', __name__, url_prefix='/')

CACHE_EXPIRE_DAYS = 7

def get_table_by_type(type_):
    if type_ == 'ip':
        return 'ip_threat_intel'
    elif type_ == 'url':
        return 'url_threat_intel'
    elif type_ == 'file':
        return 'file_threat_intel'
    return None

def normalize_url_for_db(url):
    """统一数据库存储URL格式"""
    if not url:
        return url
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    parsed = urllib.parse.urlparse(url)
    normalized_path = parsed.path if parsed.path else '/'
    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        normalized_path,
        '', '', ''
    ))

def query_db(type_, id_, source=None):
    table = get_table_by_type(type_)
    if not table:
        return None

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            row = None
            if type_ == 'url':
                # --- 修改开始 ---
                # 直接使用原始的 id_ 进行查询
                targets = [id_]
                if id_.endswith('/'):
                    targets.append(id_.rstrip('/'))
                else:
                    targets.append(id_ + '/')
                
                # OTX有时会存储没有协议头的域名
                if not id_.startswith(('http://', 'https://')):
                     targets.append('http://' + id_)
                     targets.append('https://' + id_)
                
                for target in targets:
                    if source:
                        sql = f"SELECT * FROM {table} WHERE (id=%s OR target_url=%s) AND source=%s ORDER BY last_update DESC LIMIT 1"
                        cursor.execute(sql, (target, target, source))
                    else:
                        sql = f"SELECT * FROM {table} WHERE (id=%s OR target_url=%s) ORDER BY last_update DESC LIMIT 1"
                        cursor.execute(sql, (target, target))
                    row = cursor.fetchone()
                    if row:
                        logging.info(f"URL查询命中: {target}")
                        break
                # --- 修改结束 ---
            else:
                if source:
                    sql = f"SELECT * FROM {table} WHERE id=%s AND source=%s ORDER BY last_update DESC LIMIT 1"
                    cursor.execute(sql, (id_, source))
                else:
                    sql = f"SELECT * FROM {table} WHERE id=%s ORDER BY last_update DESC LIMIT 1"
                    cursor.execute(sql, (id_,))
                row = cursor.fetchone()
    finally:
        conn.close()
    return row

def is_data_fresh(last_update):
    if not last_update:
        return False
    now = datetime.datetime.now()
    return (now - last_update).days < CACHE_EXPIRE_DAYS

def detect_query_type(query_value):
    """自动检测查询类型"""
    if not query_value:
        return None

    if query_value.startswith(('http://', 'https://')):
        return 'url'

    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ip_pattern, query_value):
        return 'ip'

    hash_pattern = r'^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$'
    if re.match(hash_pattern, query_value):
        return 'file'

    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if re.match(domain_pattern, query_value):
        return 'url'

    return None

@query_bp.route('/query', methods=['POST'])
def query_threat():
    try:
        raw_data = request.get_json()

        if raw_data is None:
            return jsonify({'error': '没有接收到JSON数据'}), 400

        if isinstance(raw_data, str):
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                data = {'query': raw_data}
        elif isinstance(raw_data, dict):
            data = raw_data
        else:
            return jsonify({'error': f'不支持的数据类型: {type(raw_data)}'}), 400

        query_value = data.get('query') or data.get('value') or data.get('q')
        query_type = data.get('type')

        if not query_type and query_value:
            query_type = detect_query_type(query_value)
            logging.info(f"自动检测查询类型: {query_type}")

        if not query_value:
            return jsonify({'error': '查询内容不能为空'}), 400

        if query_type not in ['ip', 'url', 'file']:
            return jsonify({'error': f'不支持的查询类型: {query_type}，支持的类型: ip, url, file'}), 400

        logging.info(f"收到查询请求 type={query_type}, value={query_value}")

        platforms = {
            "VirusTotal": VirusTotalCollector(),
            "AlienVault OTX": OtxCollector(),
        }

        results = {}

        for name, collector in platforms.items():
            try:
                # URL 统一使用原始的 query_value，不再进行 normalize_url_for_db
                query_key = query_value

                cached = query_db(query_type, query_key, name)
                if cached and is_data_fresh(cached.get("last_update")):
                    logging.info(f"{name} 返回缓存数据")
                    results[name] = {**cached, "from_cache": True}
                    continue

                if query_type == 'ip':
                    api_result = collector.query_ip(query_value)
                elif query_type == 'url':
                    api_result = collector.query_url(query_value)
                elif query_type == 'file':
                    api_result = collector.query_file(query_value)
                else:
                    results[name] = {"error": "Unsupported type"}
                    continue

                if "error" in api_result:
                    results[name] = {"error": api_result['error']}
                    continue

                save_ok = collector.save_to_db(api_result)
                if not save_ok:
                    results[name] = {"error": "数据保存失败"}
                    continue

                # 查询时也用原始的 query_key
                refreshed = query_db(query_type, query_key, name)
                if refreshed:
                    results[name] = {**refreshed, "from_cache": False}
                else:
                    results[name] = {"error": "保存成功但查询不到"}

            except Exception as e:
                logging.exception(f"{name} 处理错误")
                results[name] = {"error": str(e)}

        return jsonify({
            "type": query_type,
            "value": query_value,
            "results": results,
            "status": "success"
        })

    except Exception as e:
        logging.exception("查询处理总体错误")
        return jsonify({
            'error': f'服务器内部错误: {str(e)}',
            'status': 'error'
        }), 500