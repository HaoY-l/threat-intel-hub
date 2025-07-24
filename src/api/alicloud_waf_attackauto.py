#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, pymysql, datetime, logging,requests
from flask import Blueprint, request, jsonify
from data.db_init import get_db_connection
from dotenv import load_dotenv

load_dotenv()
waf_logs_bp = Blueprint('waf_logs', __name__, url_prefix='/')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@waf_logs_bp.route('/blocked_ips', methods=['GET'])
def get_blocked_ips():
    """
    从数据库查询封禁IP数据。
    支持传入时间范围 ?from=YYYY-MM-DD HH:MM:SS&to=YYYY-MM-DD HH:MM:SS
    如果未提供时间参数，默认返回当天的数据。
    现在会额外返回 created_at 时间。
    """
    try:
        to_str = request.args.get("to")
        from_str = request.args.get("from")

        now = datetime.datetime.now()
        # 尝试解析带秒的时间，如果 from_str/to_str 是空字符串，则直接使用 now 或当天零点
        try:
            to_dt = datetime.datetime.strptime(to_str, "%Y-%m-%d %H:%M:%S") if to_str else now
        except ValueError: # 如果前端可能传来不带秒的格式，再尝试解析
            try:
                to_dt = datetime.datetime.strptime(to_str, "%Y-%m-%d %H:%M") if to_str else now
            except ValueError:
                to_dt = now # 最终兜底

        try:
            from_dt = datetime.datetime.strptime(from_str, "%Y-%m-%d %H:%M:%S") if from_str else to_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            try:
                from_dt = datetime.datetime.strptime(from_str, "%Y-%m-%d %H:%M") if from_str else to_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                from_dt = to_dt.replace(hour=0, minute=0, second=0, microsecond=0) # 最终兜底


        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT block_ip AS ip, attack_count, attack_type,
                   attack_ratio, from_time AS blocked_time, to_time,
                   created_at  -- **新增：选择 created_at 字段**
            FROM blocked_ips
            WHERE from_time >= %s AND to_time <= %s
            ORDER BY attack_count DESC
            """
            cursor.execute(sql, (from_dt, to_dt))
            results = cursor.fetchall()

        formatted_results = []
        for row in results:
            threat_score = row.get('attack_count', 0)
            formatted_results.append({
                'ip': row.get('ip'),
                'attack_count': row.get('attack_count'),
                'attack_type': row.get('attack_type'),
                'attack_ratio': row.get('attack_ratio'),
                'blocked_time': row.get('blocked_time'),
                'to_time': row.get('to_time'),
                'threat_score': threat_score,
                'created_at': row.get('created_at') # **新增：添加到返回数据中**
            })

        logging.info(f"Fetched {len(formatted_results)} blocked IPs for range {from_dt} to {to_dt}.")
        return jsonify({"data": formatted_results})

    except Exception as e:
        logging.error(f"查询封禁IP失败: {e}")
        return jsonify({"error": str(e)}), 500


@waf_logs_bp.route('/ip_request_frequency', methods=['GET'])
def get_ip_request_frequency():
    """
    从数据库查询IP请求频率。
    支持传入时间范围 ?from=YYYY-MM-DD HH:MM:SS&to=YYYY-MM-DD HH:MM:SS
    如果未提供时间参数，默认返回当天数据中请求数大于2000的IP。
    现在会额外返回 created_at 时间。
    """
    try:
        to_str = request.args.get("to")
        from_str = request.args.get("from")

        now = datetime.datetime.now()
        # 尝试解析带秒的时间，如果 from_str/to_str 是空字符串，则直接使用 now 或当天零点
        try:
            to_dt = datetime.datetime.strptime(to_str, "%Y-%m-%d %H:%M:%S") if to_str else now
        except ValueError: # 如果前端可能传来不带秒的格式，再尝试解析
            try:
                to_dt = datetime.datetime.strptime(to_str, "%Y-%m-%d %H:%M") if to_str else now
            except ValueError:
                to_dt = now # 最终兜底

        try:
            from_dt = datetime.datetime.strptime(from_str, "%Y-%m-%d %H:%M:%S") if from_str else to_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            try:
                from_dt = datetime.datetime.strptime(from_str, "%Y-%m-%d %H:%M") if from_str else to_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                from_dt = to_dt.replace(hour=0, minute=0, second=0, microsecond=0) # 最终兜底

        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT ip, request_count, from_time AS last_request_time, to_time,
                   created_at -- **新增：选择 created_at 字段**
            FROM ip_request_frequency
            WHERE from_time >= %s AND to_time <= %s AND request_count > 2000
            ORDER BY request_count DESC
            """
            cursor.execute(sql, (from_dt, to_dt))
            results = cursor.fetchall()

        formatted_results = []
        for row in results:
            rate = 0
            if row.get('to_time') and row.get('last_request_time'):
                time_diff = (row['to_time'] - row['last_request_time']).total_seconds()
                if time_diff > 0:
                    rate = round(row.get('request_count', 0) / time_diff, 2)
            formatted_results.append({
                'ip': row.get('ip'),
                'request_count': row.get('request_count'),
                'last_request_time': row.get('last_request_time'),
                'to_time': row.get('to_time'),
                'request_rate': rate,
                'created_at': row.get('created_at') # **新增：添加到返回数据中**
            })

        logging.info(f"Fetched {len(formatted_results)} IP frequencies for range {from_dt} to {to_dt}.")
        return jsonify({"data": formatted_results})

    except Exception as e:
        logging.error(f"查询请求频率失败: {e}")
        return jsonify({"error": str(e)}), 500
    

# @waf_logs_bp.route('/protected_ip', methods=['POST'])
# def protected_ip():
#     """
#     查询高频请求的IP和被封禁IP，查询相对时间1分钟内，时间参考数据表中的created_at字段。
#     如果有IP，则调用接口localhost:8891/api/query(post),查询IP的威胁情报。查询对应的reputation_score字段，如果值小于-5，则调用添加黑名单接口拉黑（接口localhost:8891/api/modifyblackrule）
#     对应的操作记录记录到数据库中。表名：protected_ip
#     """
#     try:
#         now = datetime.datetime.now()
#         # 查询最近1分钟内创建的记录
#         time_threshold = now - datetime.timedelta(minutes=1)

#         conn = get_db_connection()
#         ip_to_process = set() # 使用集合避免重复处理IP

#         with conn.cursor(pymysql.cursors.DictCursor) as cursor:
#             # 查询最近1分钟内有更新的高频请求IP
#             sql_freq = """
#             SELECT ip FROM ip_request_frequency
#             WHERE created_at >= %s
#             """
#             cursor.execute(sql_freq, (time_threshold,))
#             for row in cursor.fetchall():
#                 ip_to_process.add(row['ip'])

#             # 查询最近1分钟内有更新的被封禁IP
#             sql_blocked = """
#             SELECT block_ip AS ip FROM blocked_ips
#             WHERE created_at >= %s
#             """
#             cursor.execute(sql_blocked, (time_threshold,))
#             for row in cursor.fetchall():
#                 ip_to_process.add(row['ip'])

#         if not ip_to_process:
#             return jsonify({"message": "No new IPs to process in the last minute."}), 200

#         blacklisted_ips_count = 0
#         for ip in ip_to_process:
#             logging.info(f"正在处理IP: {ip}")
#             reputation_score = None
#             WAF_API_BASE_URL = "http://localhost:8891/api"
#             try:
#                 # 1. 查询IP的威胁情报
#                 query_url = f"{WAF_API_BASE_URL}/query"
#                 query_payload = {'ip': ip}
#                 logging.info(f"调用威胁情报查询接口: {query_url} with payload: {query_payload}")
#                 response = requests.post(query_url, json=query_payload, timeout=5)
#                 response.raise_for_status() # 对4xx/5xx状态码抛出HTTPError

#                 threat_data = response.json()
#                 reputation_score = threat_data.get('reputation_score')
#                 logging.info(f"IP {ip} 的威胁情报 reputation_score: {reputation_score}")

#                 # 2. 判断并拉黑
#                 if reputation_score is not None and reputation_score < -5:
#                     logging.info(f"IP {ip} 威胁分数 {reputation_score} 低于 -5，准备加入黑名单。")
#                     blacklist_url = f"{WAF_API_BASE_URL}/modifyblackrule"
#                     # 假设 modifyblackrule 接口需要 IP 和一个规则名称或原因
#                     # 请根据实际 WAF 接口要求调整 payload
#                     blacklist_payload = {
#                         'ip': ip,
#                         'action': 'add', # 假设 'add' 是添加操作
#                         'reason': 'High threat score from intelligence feed'
#                     }
#                     logging.info(f"调用黑名单接口: {blacklist_url} with payload: {blacklist_payload}")
#                     blacklist_response = requests.post(blacklist_url, json=blacklist_payload, timeout=5)
#                     blacklist_response.raise_for_status()

#                     blacklist_result = blacklist_response.json()
#                     logging.info(f"IP {ip} 已成功加入黑名单。WAF响应: {blacklist_result}")
#                     blacklisted_ips_count += 1

#                     # 3. 记录操作到数据库
#                     with conn.cursor() as cursor:
#                         insert_sql = """
#                         INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
#                         VALUES (%s, %s, %s, %s, %s)
#                         """
#                         cursor.execute(insert_sql, (
#                             ip,
#                             'blacklisted',
#                             'Threat score below -5',
#                             reputation_score,
#                             now
#                         ))
#                         conn.commit()
#                         logging.info(f"IP {ip} 的拉黑操作已记录到 protected_ip 表。")
#                 else:
#                     logging.info(f"IP {ip} 威胁分数 {reputation_score} 未达到拉黑条件或无分数。")

#             except requests.exceptions.Timeout:
#                 logging.error(f"调用WAF接口超时 IP: {ip}")
#                 # 记录失败操作
#                 with conn.cursor() as cursor:
#                     insert_sql = """
#                     INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
#                     VALUES (%s, %s, %s, %s, %s)
#                     """
#                     cursor.execute(insert_sql, (
#                         ip,
#                         'query_failed',
#                         'WAF API Timeout during query',
#                         reputation_score, # 可能是None
#                         now
#                     ))
#                     conn.commit()
#             except requests.exceptions.RequestException as req_e:
#                 logging.error(f"调用WAF接口失败 IP: {ip}, 错误: {req_e}")
#                 # 记录失败操作
#                 with conn.cursor() as cursor:
#                     insert_sql = """
#                     INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
#                     VALUES (%s, %s, %s, %s, %s)
#                     """
#                     cursor.execute(insert_sql, (
#                         ip,
#                         'query_failed',
#                         f'WAF API Request Error: {req_e}',
#                         reputation_score, # 可能是None
#                         now
#                     ))
#                     conn.commit()
#             except Exception as e:
#                 logging.error(f"处理IP {ip} 时发生未知错误: {e}")
#                 # 记录失败操作
#                 with conn.cursor() as cursor:
#                     insert_sql = """
#                     INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
#                     VALUES (%s, %s, %s, %s, %s)
#                     """
#                     cursor.execute(insert_sql, (
#                         ip,
#                         'processing_failed',
#                         f'Unknown error: {e}',
#                         reputation_score, # 可能是None
#                         now
#                     ))
#                     conn.commit()

#         logging.info(f"总计处理了 {len(ip_to_process)} 个IP，其中 {blacklisted_ips_count} 个IP被拉黑。")
#         return jsonify({
#             "message": "IP processing complete.",
#             "total_ips_checked": len(ip_to_process),
#             "ips_blacklisted": blacklisted_ips_count
#         }), 200

#     except pymysql.Error as db_e:
#         logging.error(f"数据库操作失败: {db_e}")
#         return jsonify({"error": f"Database error: {db_e}"}), 500
#     except Exception as e:
#         logging.error(f"protected_ip 路由发生未预料的错误: {e}")
#         return jsonify({"error": str(e)}), 500