from flask import Blueprint, request, jsonify
from src.routes.threat.virustotal import VirusTotalCollector
from data.db_init import get_db_connection, create_database_and_tables
import datetime
import logging
import urllib.parse

# 预留后续平台
# from routes.threat.xforce import XForceCollector
# from routes.threat.alienvault import AlienVaultCollector

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
    
    # 解析URL
    parsed = urllib.parse.urlparse(url)
    
    # 如果路径为空或只有根路径，统一处理
    if not parsed.path or parsed.path == '/':
        normalized_path = '/'
    else:
        normalized_path = parsed.path
    
    # 重新构建URL
    normalized = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        normalized_path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return normalized

def query_db(type_, id_, source=None):
    table = get_table_by_type(type_)
    if not table:
        return None

    conn = get_db_connection()
    with conn.cursor() as cursor:
        if type_ == 'url':
            # 对于URL类型，使用更灵活的查询方式
            if source:
                # 先尝试精确匹配
                sql = f"SELECT * FROM {table} WHERE target_url=%s AND source=%s ORDER BY last_update DESC LIMIT 1"
                cursor.execute(sql, (id_, source))
                row = cursor.fetchone()
                
                # 如果精确匹配失败，尝试标准化URL匹配
                if not row:
                    normalized_query = normalize_url(id_)
                    # 尝试匹配标准化后的URL
                    sql = f"SELECT * FROM {table} WHERE target_url=%s AND source=%s ORDER BY last_update DESC LIMIT 1"
                    cursor.execute(sql, (normalized_query, source))
                    row = cursor.fetchone()
                
                # 如果还是找不到，尝试模糊匹配（处理尾部斜杠问题）
                if not row:
                    if id_.endswith('/'):
                        alt_url = id_.rstrip('/')
                    else:
                        alt_url = id_ + '/'
                    
                    sql = f"SELECT * FROM {table} WHERE target_url=%s AND source=%s ORDER BY last_update DESC LIMIT 1"
                    cursor.execute(sql, (alt_url, source))
                    row = cursor.fetchone()
                    
                    if row:
                        logging.info(f"使用替代URL {alt_url} 查询到数据")
            else:
                # 不指定source的情况下，也使用类似的策略
                sql = f"SELECT * FROM {table} WHERE target_url=%s ORDER BY last_update DESC LIMIT 1"
                cursor.execute(sql, (id_,))
                row = cursor.fetchone()
                
                if not row:
                    normalized_query = normalize_url(id_)
                    sql = f"SELECT * FROM {table} WHERE target_url=%s ORDER BY last_update DESC LIMIT 1"
                    cursor.execute(sql, (normalized_query,))
                    row = cursor.fetchone()
                
                if not row:
                    if id_.endswith('/'):
                        alt_url = id_.rstrip('/')
                    else:
                        alt_url = id_ + '/'
                    
                    sql = f"SELECT * FROM {table} WHERE target_url=%s ORDER BY last_update DESC LIMIT 1"
                    cursor.execute(sql, (alt_url,))
                    row = cursor.fetchone()
                    
                    if row:
                        logging.info(f"使用替代URL {alt_url} 查询到数据")
                        
            logging.info(f"URL查询结果: {row is not None}, 查询URL: {id_}")
        else:
            # 对于IP和文件类型，直接用ID查询
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
    delta = now - last_update
    return delta.days < CACHE_EXPIRE_DAYS

@query_bp.route('/query', methods=['POST'])
def query_threat():
    data = request.json
    query_type = data.get('type')  # "ip" | "url" | "file"
    query_value = data.get('value')
    logging.info(f"本次查询收到请求类型:{query_type}，参数：{query_value}")

    if query_type not in ['ip', 'url', 'file'] or not query_value:
        logging.error("无效的查询类型或值")
        return jsonify({'error': 'Invalid type or value'}), 400

    # 先查询缓存数据
    cached_data = query_db(query_type, query_value)

    # 如果有缓存数据且数据新鲜，直接返回
    if cached_data and is_data_fresh(cached_data.get('last_update')):
        logging.info(f"本次查询 {query_value} 返回缓存数据")
        return jsonify({
            "type": query_type,
            "value": query_value,
            "results": {"cached": cached_data}
        })

    # 如果没有缓存数据或数据过期，调用API获取新数据
    platforms = {
        "virustotal": VirusTotalCollector(),
        # "xforce": XForceCollector(),
        # "alienvault": AlienVaultCollector(),
    }

    results = {}
    for name, collector in platforms.items():
        try:
            # 调用对应的API接口
            if query_type == 'ip':
                api_result = collector.query_ip(query_value)
            elif query_type == 'url':
                api_result = collector.query_url(query_value)
            elif query_type == 'file':
                api_result = collector.query_file(query_value)
            else:
                continue

            # 检查API调用是否成功
            if 'error' in api_result:
                logging.error(f"{name} API调用失败: {api_result['error']}")
                results[name] = {"error": api_result['error']}
                continue

            # 保存到数据库
            try:
                save_success = collector.save_to_db(api_result)
                if save_success:
                    # 从数据库获取刚保存的数据，指定source
                    db_data = query_db(query_type, query_value, name)
                    
                    if db_data:
                        results[name] = db_data
                        logging.info(f"{name} 成功从数据库查询到数据")
                    else:
                        logging.error(f"{name} 从数据库查询失败")
                        # 尝试直接查询最新插入的数据
                        logging.info(f"尝试使用API返回的数据结构查询...")
                        api_data = api_result.get('data', {})
                        api_url = api_data.get('attributes', {}).get('url') or api_data.get('attributes', {}).get('last_final_url')
                        if api_url:
                            db_data = query_db(query_type, api_url, name)
                            if db_data:
                                results[name] = db_data
                                logging.info(f"{name} 使用API返回的URL成功查询到数据")
                            else:
                                results[name] = {"error": "查询失败"}
                        else:
                            results[name] = {"error": "查询失败"}
                else:
                    logging.error(f"{name} 数据保存失败")
                    results[name] = {"error": "数据保存失败"}
            except Exception as e:
                logging.error(f"{name} 保存数据时发生错误: {e}")
                results[name] = {"error": f"保存数据时发生错误: {str(e)}"}

        except Exception as e:
            logging.error(f"{name} 处理过程中发生错误: {e}")
            results[name] = {"error": str(e)}

    return jsonify({
        "type": query_type,
        "value": query_value,
        "results": results
    })