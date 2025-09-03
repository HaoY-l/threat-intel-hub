#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os,pymysql,time,datetime,logging,time
from flask import Flask, Blueprint, request, jsonify
from alibabacloud_sls20201230.client import Client as Sls20201230Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sls20201230 import models as sls_20201230_models
from alibabacloud_tea_util import models as util_models
from data.db_init import get_db_connection
from dotenv import load_dotenv
load_dotenv()



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

def fetch_and_save_blocked_ips():
    """
    查询封禁IP，每15分钟执行一次
    """

    to_dt = datetime.datetime.now()
    from_dt = to_dt - datetime.timedelta(minutes=15)

    # 转时间戳整数，方便数据库存储和查询
    to_time = int(to_dt.timestamp())
    from_time = int(from_dt.timestamp())
    # print(from_time, to_time)

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
        # print(logs)

        conn = get_db_connection()
        with conn.cursor() as cursor:
            for item in logs:
                block_ip = item.get("攻击IP")
                attack_count = int(item.get("攻击次数", 0))
                attack_type = item.get("攻击类型", "")
                total_count = get_ip_request_total_count(from_time, to_time, block_ip, client)
                attack_ratio = round(attack_count / total_count, 4) if total_count else 0.0
                from_time_dt = datetime.datetime.fromtimestamp(from_time)
                to_time_dt = datetime.datetime.fromtimestamp(to_time)
                sql = """
                INSERT INTO blocked_ips (block_ip, attack_count, attack_ratio, attack_type, from_time, to_time)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (block_ip, attack_count, attack_ratio, attack_type, from_time_dt, to_time_dt))

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

def fetch_and_save_ip_request_frequency():
    """
    查询一分钟内IP请求频率，1分钟执行一次，只存大于2000条的IP
    接口无参数，自动获取当前时间往前1分钟区间
    """
    to_dt = datetime.datetime.now()
    from_dt = to_dt - datetime.timedelta(minutes=5)

    to_time = int(to_dt.timestamp())
    from_time = int(from_dt.timestamp())

    client = get_sls_client()
    highfreq_ip_count = int(os.getenv("highfreq_ip_count"))
    query = f'''* | SELECT real_client_ip AS ip, COUNT(*) AS request_count
WHERE real_client_ip != ''
GROUP BY real_client_ip
HAVING request_count > {highfreq_ip_count}
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

        conn = get_db_connection()  # 注意：这里我改成你之前用的get_db_connection()
        with conn.cursor() as cursor:
            saved_count = 0
            for item in logs:
                ip = item.get("ip")
                request_count = int(item.get("request_count", 0))
                if request_count > highfreq_ip_count:
                    sql = """
                    INSERT INTO ip_request_frequency (ip, request_count, from_time, to_time)
                    VALUES (%s, %s, %s, %s)
                    """
                    from_time_dt = datetime.datetime.fromtimestamp(from_time)
                    to_time_dt = datetime.datetime.fromtimestamp(to_time)
                    cursor.execute(sql, (ip, request_count, from_time_dt, to_time_dt))
                    saved_count += 1
            conn.commit()  # 别忘记提交事务

        return jsonify({"message": "请求频率数据保存成功", "saved_count": saved_count})

    except Exception as e:
        logging.error(f"查询请求频率失败: {e}")
        return jsonify({"error": str(e)}), 500



