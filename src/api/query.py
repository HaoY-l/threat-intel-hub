from flask import Blueprint, request, jsonify
from src.routes.threat.virustotal import VirusTotalCollector
from src.routes.threat.otx import OtxCollector
from data.db_init import get_db_connection
import datetime
import logging
import urllib.parse
import json

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

def normalize_url(url):
    """标准化URL，处理尾部斜杠等问题"""
    if not url:
        return url
    parsed = urllib.parse.urlparse(url)
    normalized_path = parsed.path if parsed.path and parsed.path != '/' else '/'
    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        normalized_path,
        parsed.params,
        parsed.query,
        parsed.fragment
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
                targets = [id_, normalize_url(id_)]
                if id_.endswith('/'):
                    targets.append(id_.rstrip('/'))
                else:
                    targets.append(id_ + '/')

                for target in targets:
                    if source:
                        sql = f"SELECT * FROM {table} WHERE target_url=%s AND source=%s ORDER BY last_update DESC LIMIT 1"
                        cursor.execute(sql, (target, source))
                    else:
                        sql = f"SELECT * FROM {table} WHERE target_url=%s ORDER BY last_update DESC LIMIT 1"
                        cursor.execute(sql, (target,))
                    row = cursor.fetchone()
                    if row:
                        logging.info(f"URL查询命中: {target}")
                        break
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
    
    # 检查是否是URL
    if query_value.startswith(('http://', 'https://')):
        return 'url'
    
    # 检查是否是IP地址
    import re
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ip_pattern, query_value):
        return 'ip'
    
    # 检查是否是文件哈希（MD5, SHA1, SHA256）
    hash_pattern = r'^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$'
    if re.match(hash_pattern, query_value):
        return 'file'
    
    # 检查是否是域名
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    if re.match(domain_pattern, query_value):
        return 'url'
    
    return None

@query_bp.route('/query', methods=['POST'])
def query_threat():
    try:
        # 获取请求数据并处理不同的数据格式
        raw_data = request.get_json()
        
        # 调试信息
        logging.info(f"接收到的原始数据: {raw_data}")
        logging.info(f"数据类型: {type(raw_data)}")
        
        # 处理不同的数据格式
        if raw_data is None:
            return jsonify({'error': '没有接收到JSON数据'}), 400
        
        # 统一处理数据格式
        if isinstance(raw_data, str):
            # 如果前端发送的是字符串，尝试解析为JSON
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                # 如果不是JSON字符串，假设它是查询值
                data = {'query': raw_data}
        elif isinstance(raw_data, dict):
            data = raw_data
        else:
            return jsonify({'error': f'不支持的数据类型: {type(raw_data)}'}), 400
        
        # 提取查询参数，支持多种参数名
        query_value = data.get('query') or data.get('value') or data.get('q')
        query_type = data.get('type')
        
        # 如果没有指定类型，尝试自动检测
        if not query_type and query_value:
            query_type = detect_query_type(query_value)
            logging.info(f"自动检测查询类型: {query_type}")
        
        # 验证参数
        if not query_value:
            return jsonify({'error': '查询内容不能为空'}), 400
        
        if query_type not in ['ip', 'url', 'file']:
            return jsonify({'error': f'不支持的查询类型: {query_type}，支持的类型: ip, url, file'}), 400

        logging.info(f"收到查询请求 type={query_type}, value={query_value}")

        # 所有接入平台
        platforms = {
            "VirusTotal": VirusTotalCollector(),
            "AlienVault OTX": OtxCollector(),
            # 预留扩展平台
            # "xforce": XForceCollector(),
        }

        results = {}

        for name, collector in platforms.items():
            try:
                # 先查数据库缓存
                cached = query_db(query_type, query_value, name)
                if cached and is_data_fresh(cached.get("last_update")):
                    logging.info(f"{name} 返回缓存数据")
                    results[name] = {**cached, "from_cache": True}
                    continue

                # 没有缓存或数据过期，发起 API 查询
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

                # 保存后再查数据库
                refreshed = query_db(query_type, query_value, name)
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