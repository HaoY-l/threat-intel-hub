#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os,pymysql,time,datetime,logging
from flask import Flask, Blueprint, request, jsonify
from alibabacloud_sls20201230.client import Client as Sls20201230Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sls20201230 import models as sls_20201230_models
from alibabacloud_tea_util import models as util_models
from data.db_init import get_db_connection
from dotenv import load_dotenv
load_dotenv()

waf_logs_bp = Blueprint('waf_logs', __name__, url_prefix='/')


def get_sls_client():
    config = open_api_models.Config(
        access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    )
    config.endpoint = 'cn-hangzhou.log.aliyuncs.com'
    return Sls20201230Client(config)

def get_time_ranges_for_day(day: datetime.date):
    start = datetime.datetime.combine(day, datetime.time.min)
    end = datetime.datetime.combine(day, datetime.time.max)
    return int(start.timestamp()), int(end.timestamp())

@waf_logs_bp.route('/blocked_ips', methods=['POST'])
def fetch_and_save_blocked_ips():
    """
    查询封禁IP，每15分钟执行一次
    接口参数 JSON: { "from": timestamp, "to": timestamp }
    """
    data = request.get_json() or {}
    from_time = data.get('from')
    to_time = data.get('to')

    if not from_time or not to_time:
        return jsonify({"error": "需要传入from和to时间戳"}), 400

    client = get_sls_client()

    query = '''* | SELECT real_client_ip AS "攻击IP", COUNT(*) AS "攻击次数", final_plugin AS "攻击类型"
WHERE 
    (final_plugin='acl' AND acl_action='block' AND acl_test='false' AND acl_rule_type='blacklist') 
    OR (final_plugin='cc' AND cc_rule_type='custom' AND cc_test='false' AND cc_action='block') 
    OR (antiscan_action='block' AND antiscan_test='false') 
GROUP BY real_client_ip, final_plugin
ORDER BY "攻击次数" DESC'''

    get_logs_request = sls_20201230_models.GetLogsRequest(
        from_=from_time,
        to=to_time,
        query=query
    )
    runtime = util_models.RuntimeOptions()
    headers = {}

    try:
        response = client.get_logs_with_options(
            os.getenv("SLS_PROJECT_NAME"),
            os.getenv("SLS_LOGSTORE_NAME"),
            get_logs_request,
            headers,
            runtime
        )
        logs = response.body

        conn = get_db_connection()
        with conn.cursor() as cursor:
            for item in logs:
                block_ip = item.get("攻击IP")
                attack_count = int(item.get("攻击次数", 0))
                # 查询总请求数用于计算占比
                total_count = get_ip_request_total_count(from_time, to_time, block_ip, client)
                attack_ratio = round(attack_count / total_count, 4) if total_count else 0.0

                sql = """
                INSERT INTO blocked_ips (block_ip, attack_count, attack_ratio, from_timestamp, to_timestamp)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (block_ip, attack_count, attack_ratio, from_time, to_time))

        return jsonify({"message": "封禁IP数据保存成功", "count": len(logs)})

    except Exception as e:
        logging.error(f"查询封禁IP失败: {e}")
        return jsonify({"error": str(e)}), 500

def get_ip_request_total_count(from_time, to_time, ip, client):
    """辅助查询某IP的总请求数"""
    query = f"* | SELECT COUNT(*) AS total_count WHERE real_client_ip='{ip}'"
    get_logs_request = sls_20201230_models.GetLogsRequest(
        from_=from_time,
        to=to_time,
        query=query
    )
    runtime = util_models.RuntimeOptions()
    headers = {}
    try:
        response = client.get_logs_with_options(
            os.getenv("SLS_PROJECT_NAME"),
            os.getenv("SLS_LOGSTORE_NAME"),
            get_logs_request,
            headers,
            runtime
        )
        total_count = response.body[0].get('total_count', 0)
        return int(total_count)
    except Exception as e:
        logging.error(f"查询IP请求总数失败: {e}")
        return 0

@waf_logs_bp.route('/ip_request_frequency', methods=['POST'])
def fetch_and_save_ip_request_frequency():
    """
    查询一分钟内IP请求频率，1分钟执行一次，只存大于2000条的IP
    参数 JSON: { "from": timestamp, "to": timestamp }
    """
    data = request.get_json() or {}
    from_time = data.get('from')
    to_time = data.get('to')

    if not from_time or not to_time:
        return jsonify({"error": "需要传入from和to时间戳"}), 400

    client = get_sls_client()

    query = '''* | SELECT real_client_ip AS ip, COUNT(*) AS request_count
WHERE real_client_ip != ''
GROUP BY real_client_ip
ORDER BY request_count DESC'''

    get_logs_request = sls_20201230_models.GetLogsRequest(
        from_=from_time,
        to=to_time,
        query=query
    )
    runtime = util_models.RuntimeOptions()
    headers = {}

    try:
        response = client.get_logs_with_options(
            os.getenv("SLS_PROJECT_NAME"),
            os.getenv("SLS_LOGSTORE_NAME"),
            get_logs_request,
            headers,
            runtime
        )
        logs = response.body

        conn = get_mysql_conn()
        with conn.cursor() as cursor:
            saved_count = 0
            for item in logs:
                ip = item.get("ip")
                request_count = int(item.get("request_count", 0))
                if request_count > 2000:
                    sql = """
                    INSERT INTO ip_request_frequency (ip, request_count, from_timestamp, to_timestamp)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (ip, request_count, from_time, to_time))
                    saved_count += 1

        return jsonify({"message": "请求频率数据保存成功", "saved_count": saved_count})

    except Exception as e:
        logging.error(f"查询请求频率失败: {e}")
        return jsonify({"error": str(e)}), 500

@waf_logs_bp.route('/daily_summary', methods=['POST'])
def save_daily_summary():
    """
    统计每日汇总数据，参数 JSON: { "date": "YYYY-MM-DD" }
    统计封禁IP数，高频请求IP数
    """
    data = request.get_json() or {}
    date_str = data.get("date")
    if not date_str:
        return jsonify({"error": "需要传入日期参数 date"}), 400
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return jsonify({"error": "日期格式错误，应为 YYYY-MM-DD"}), 400

    from_time, to_time = get_time_ranges_for_day(date_obj)

    conn = get_mysql_conn()
    with conn.cursor() as cursor:
        # 封禁IP数量统计
        sql_blocked_count = """
        SELECT COUNT(DISTINCT block_ip) AS cnt FROM blocked_ips WHERE from_timestamp >= %s AND to_timestamp <= %s
        """
        cursor.execute(sql_blocked_count, (from_time, to_time))
        blocked_ip_count = cursor.fetchone().get("cnt", 0)

        # 高频请求IP数量统计
        sql_high_freq_count = """
        SELECT COUNT(DISTINCT ip) AS cnt FROM ip_request_frequency WHERE from_timestamp >= %s AND to_timestamp <= %s
        """
        cursor.execute(sql_high_freq_count, (from_time, to_time))
        high_freq_ip_count = cursor.fetchone().get("cnt", 0)

        # 插入或更新daily_summary表
        sql_upsert = """
        INSERT INTO daily_summary (date, blocked_ip_count, high_frequency_ip_count)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            blocked_ip_count = VALUES(blocked_ip_count),
            high_frequency_ip_count = VALUES(high_frequency_ip_count)
        """
        cursor.execute(sql_upsert, (date_obj, blocked_ip_count, high_freq_ip_count))

    return jsonify({"message": "每日汇总数据保存成功", "date": date_str, "blocked_ip_count": blocked_ip_count, "high_frequency_ip_count": high_freq_ip_count})


if __name__ == '__main__':
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(bp)

    app.run(host='0.0.0.0', port=8891, debug=True)
