from flask import Blueprint, request, jsonify
from src.routes.threat.virustotal import VirusTotalCollector
from src.routes.threat.otx import OtxCollector
from data.db_init import get_db_connection
import datetime
import logging
import urllib.parse

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
    conn.close()
    return row

def is_data_fresh(last_update):
    if not last_update:
        return False
    now = datetime.datetime.now()
    return (now - last_update).days < CACHE_EXPIRE_DAYS

@query_bp.route('/query', methods=['POST'])
def query_threat():
    data = request.json
    query_type = data.get('type')
    query_value = data.get('value')

    logging.info(f"收到查询请求 type={query_type}, value={query_value}")

    if query_type not in ['ip', 'url', 'file'] or not query_value:
        return jsonify({'error': 'Invalid type or value'}), 400

    # 所有接入平台
    platforms = {
        "virustotal": VirusTotalCollector(),
        "otx": OtxCollector(),
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
            if query_type == 'ip' or query_type == 'ipv4':
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
        "results": results
    })
