#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, pymysql, datetime, logging
from flask import Blueprint, request, jsonify
from data.db_init import get_db_connection
from dotenv import load_dotenv

load_dotenv()
waf_logs_bp = Blueprint('waf_logs', __name__, url_prefix='/')


@waf_logs_bp.route('/blocked_ips', methods=['GET'])
def get_blocked_ips():
    """
    从数据库查询封禁IP数据，支持传入时间范围 ?from=2025-07-24 10:00&to=2025-07-24 10:15
    默认返回最近15分钟的数据
    """
    try:
        to_str = request.args.get("to")
        from_str = request.args.get("from")

        to_dt = datetime.datetime.strptime(to_str, "%Y-%m-%d %H:%M") if to_str else datetime.datetime.now()
        from_dt = datetime.datetime.strptime(from_str, "%Y-%m-%d %H:%M") if from_str else to_dt - datetime.timedelta(minutes=15)

        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT block_ip AS 攻击IP, attack_count AS 攻击次数, attack_type AS 攻击类型,
                   attack_ratio, from_time, to_time
            FROM blocked_ips
            WHERE from_time >= %s AND to_time <= %s
            ORDER BY attack_count DESC
            """
            cursor.execute(sql, (from_dt, to_dt))
            results = cursor.fetchall()

        return jsonify(results)

    except Exception as e:
        logging.error(f"查询封禁IP失败: {e}")
        return jsonify({"error": str(e)}), 500


@waf_logs_bp.route('/ip_request_frequency', methods=['GET'])
def get_ip_request_frequency():
    """
    从数据库查询IP请求频率，默认返回最近5分钟内请求数大于2000的IP
    可选参数：?from=2025-07-24 10:00&to=2025-07-24 10:05
    """
    try:
        to_str = request.args.get("to")
        from_str = request.args.get("from")

        to_dt = datetime.datetime.strptime(to_str, "%Y-%m-%d %H:%M") if to_str else datetime.datetime.now()
        from_dt = datetime.datetime.strptime(from_str, "%Y-%m-%d %H:%M") if from_str else to_dt - datetime.timedelta(minutes=5)

        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT ip, request_count, from_time, to_time
            FROM ip_request_frequency
            WHERE from_time >= %s AND to_time <= %s AND request_count > 2000
            ORDER BY request_count DESC
            """
            cursor.execute(sql, (from_dt, to_dt))
            results = cursor.fetchall()

        return jsonify(results)

    except Exception as e:
        logging.error(f"查询请求频率失败: {e}")
        return jsonify({"error": str(e)}), 500
