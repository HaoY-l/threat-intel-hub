#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
import os,time,json,datetime,requests
from alibabacloud_waf_openapi20211001.client import Client as waf_openapi20211001Client
from typing import List
from alibabacloud_sls20201230.client import Client as Sls20201230Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sls20201230 import models as sls_20201230_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from dotenv import load_dotenv
from models import WAFLog
from extensions import db
load_dotenv()

waf_attack_alert = Blueprint('alert', __name__)  # 创建 WAF 蓝图
script_dir = os.path.dirname(__file__)
# 获取日期和时间戳
def get_time_ranges():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # 当天 00:00:00
    start_of_today = datetime.datetime.combine(today, datetime.time.min)
    start_of_today_timestamp = int(start_of_today.timestamp())

    # 当前时间（当天结束时间）
    current_timestamp = int(time.time())

    # 前一天 00:00:00
    start_of_yesterday = datetime.datetime.combine(yesterday, datetime.time.min)
    start_of_yesterday_timestamp = int(start_of_yesterday.timestamp())

    # 前一天 23:59:59
    end_of_yesterday = datetime.datetime.combine(yesterday, datetime.time(23, 59, 59))
    end_of_yesterday_timestamp = int(end_of_yesterday.timestamp())
    
    return {
        'today': today,
        'yesterday': yesterday,
        'start_of_today_timestamp': start_of_today_timestamp,
        'current_timestamp': current_timestamp,
        'start_of_yesterday_timestamp': start_of_yesterday_timestamp,
        'end_of_yesterday_timestamp': end_of_yesterday_timestamp
    }

class waf_alerts:
    def __init__(self):
        pass

    @staticmethod
    def create_sls_client() -> Sls20201230Client:
        config = open_api_models.Config(
            access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
            access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        )
        config.endpoint = f'cn-hangzhou.log.aliyuncs.com'
        return Sls20201230Client(config)

    @staticmethod
    def get_block_log(from_time, to_time):            
        client = waf_alerts.create_sls_client()
        get_logs_request = sls_20201230_models.GetLogsRequest(
            from_=from_time,
            to=to_time,
            query='''* | SELECT real_client_ip AS "攻击IP", COUNT(*) AS "攻击次数"
WHERE 
    (final_plugin='acl' AND acl_action='block' AND acl_test='false' AND acl_rule_type='blacklist') 
    OR (final_plugin='cc' AND cc_rule_type='custom' AND cc_test='false' AND cc_action='block') 
    OR (antiscan_action='block' AND antiscan_test='false') 
GROUP BY 
    real_client_ip 
ORDER BY "攻击次数" DESC
'''
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        result = []  # 用于存储结果
        try:
            response = client.get_logs_with_options(os.getenv("SLS_PROJECT_NAME"), os.getenv("SLS_LOGSTORE_NAME"), get_logs_request, headers, runtime)
            date = response.body
            for item in date:
                block_ip = item.get("攻击IP", "N/A")  # 获取封禁 IP
                if block_ip != "N/A":
                    result.append({
                        "攻击IP": block_ip,
                        "攻击次数": item.get("攻击次数", "N/A"),
                        "攻击占比":""
                    })
        except Exception as error:
            print(f"获取封禁日志时出错: {error}")
        return (result) 

    @staticmethod
    def get_ip_total(from_time=None, to_time=None, ip=None):
        client = waf_alerts.create_sls_client()
        get_logs_request = sls_20201230_models.GetLogsRequest(
            from_=from_time,
            to=to_time,
            query=f'''* | SELECT COUNT(*) AS "total_count" WHERE real_client_ip='{ip}' '''
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            response = client.get_logs_with_options(os.getenv("SLS_PROJECT_NAME"), os.getenv("SLS_LOGSTORE_NAME"), get_logs_request, headers, runtime)
            date = response.body[0]
            total_count = date['total_count']
        except Exception as error:
            print(f"获取扫描日志时出错: {error}")
        return (total_count) 
    @staticmethod
    def result():
        from_time = get_time_ranges()['start_of_yesterday_timestamp']
        to_time = get_time_ranges()['end_of_yesterday_timestamp']
        sub_data = waf_alerts.get_block_log(from_time, to_time)
        results = []
        WAFLogs = []
        for item in sub_data:
            dict = {
                "封禁IP": item.get("攻击IP", "N/A"),
                "攻击次数": item.get("攻击次数", "N/A"),
                "攻击占比":f"{(int(item.get('攻击次数', 0)) / int(waf_alerts.get_ip_total(from_time, to_time, item.get('攻击IP', 'N/A')))):.1%}"}
            results.append(dict)
            WAFLogs.append(WAFLog(ip=item.get("攻击IP", "N/A"), attack_count=item.get("攻击次数", 0), attack_ratio=f"{(int(item.get('攻击次数', 0)) / int(waf_alerts.get_ip_total(from_time, to_time, item.get('攻击IP', 'N/A')))):.1%}"))
        db.session.add_all(WAFLogs)
        db.session.commit()
        return results

def send_dingtalk_message(content):
    # 钉钉机器人消息体
    webhook_url = os.getenv("DDINGTALK_WEBHOOK_URL")
    headers = {"Content-Type": "application/json"}
    message = {
        "msgtype": "markdown",  # 发送文本消息
        "markdown": {
            "title": "WAF昨日攻击拦截统计情况",  # 消息标题
            "text": content
        }
    }
    # 发送请求
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(message))
        response.raise_for_status()  # 如果请求失败，抛出异常
        if response.json().get("errcode") == 0:
            print("钉钉消息发送成功！")
        else:
            print(f"消息发送失败，错误码：{response.json().get('errcode')}")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")

def send_daily_report():
    print(f"开始生成每日报告: {datetime.datetime.now()}")
    attack_data = waf_alerts.result()
    # 构建显示详细信息的部分
    attack_details = "\n".join([f"- 🔹 **IP**: {item['封禁IP']}, **拦截次数**: {item['攻击次数']}, **拦截占比**: {item['攻击占比']}"
                            for item in attack_data])
    
    content = f"""
## 🛡️ WAF攻击情况统计🚨 ({get_time_ranges()['yesterday']})

**总攻击IP数**: {len(attack_data)}

{attack_details}

---

> 📊 *统计时间: {get_time_ranges()['today']}  叫叫项目*
"""
    send_dingtalk_message(content)
    print(f"每日报告发送完成: {datetime.datetime.now()}")

@waf_attack_alert.route('/alert', methods=['GET'])
def send_report():
    result = send_daily_report()
    return jsonify({"status": "success", "message": "钉钉告警发送成功！"}), 200
