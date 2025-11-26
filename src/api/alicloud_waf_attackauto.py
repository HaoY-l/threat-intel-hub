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
        highfreq_ip_count = int(os.getenv("highfreq_ip_count"))
        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT ip, request_count, from_time AS last_request_time, to_time,
                   created_at -- **新增：选择 created_at 字段**
            FROM ip_request_frequency
            WHERE from_time >= %s AND to_time <= %s AND request_count > %s
            ORDER BY request_count DESC
            """
            cursor.execute(sql, (from_dt, to_dt,highfreq_ip_count))
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
    

@waf_logs_bp.route('/protected_ip', methods=['GET'])
def protected_ip():
    """
    查询 protected_ip 数据库表中今天的自动封禁记录。
    返回一个 JSON 数组，包含今天的每条封禁记录及其详细信息。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor) # 使用字典游标，方便获取字段名

        # 获取今天的开始和结束时间
        now = datetime.datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # 查询今天的 protected_ip 记录
        # 注意：这里查询的是所有记录，前端会负责筛选和计数
        sql = """
        SELECT
            id,
            ip,
            action,
            reason,
            reputation_score,
            action_time
        FROM
            protected_ip
        WHERE
            action_time >= %s AND action_time <= %s
        ORDER BY
            action_time ASC;
        """
        cursor.execute(sql, (today_start, today_end))
        records = cursor.fetchall()

        # 格式化 action_time 为 ISO 8601 字符串，方便前端解析
        formatted_records = []
        for record in records:
            # 确保 action_time 是 datetime 对象再进行格式化
            if isinstance(record.get('action_time'), datetime.datetime):
                record['action_time'] = record['action_time'].isoformat() # 转换为 ISO 8601 格式
            formatted_records.append(record)

        return jsonify(formatted_records), 200

    except pymysql.Error as e:
        print(f"数据库查询错误: {e}")
        return jsonify({"error": "数据库查询失败", "details": str(e)}), 500
    except Exception as e:
        print(f"服务器内部错误: {e}")
        return jsonify({"error": "服务器内部错误", "details": str(e)}), 500
    finally:
        if conn and conn.open:
            conn.close()
