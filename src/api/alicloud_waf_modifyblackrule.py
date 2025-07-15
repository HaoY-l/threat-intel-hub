# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os,ipaddress,re,json,requests
from typing import List
from alibabacloud_waf_openapi20211001.client import Client as waf_openapi20211001Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_waf_openapi20211001 import models as waf_openapi_20211001_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from datetime import datetime
from flask import Blueprint, jsonify,request
from dotenv import load_dotenv
load_dotenv()

waf_modifyblackrule = Blueprint('waf_modifyblackrule', __name__)

def is_valid_ip(value):
    """判断字符串是否是有效的 IP 地址"""
    try:
        ipaddress.ip_network(value, strict=False)  # 兼容 CIDR 格式
        return True
    except ValueError:
        return False
def is_valid_domain(value):
    """检查是否为有效的域名（不包括 IP 和 URL 路径）"""
    domain_regex = re.compile(
        r'^(?!:\/\/)([a-zA-Z0-9-_]+\.)+[a-zA-Z]{2,}$'
    )
    return bool(domain_regex.match(value))
def is_valid_url_path(value):
    """检查是否为 URL 路径（以 `/` 开头，且不包含完整域名或IP）"""
    return value.startswith("/") and " " not in value and not is_valid_ip(value) and not is_valid_domain(value)



def create_client() -> waf_openapi20211001Client:
    config = open_api_models.Config(
        access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    )
    config.endpoint = f'wafopenapi.cn-hangzhou.aliyuncs.com'
    return waf_openapi20211001Client(config)

# 修改黑名单规则
@waf_modifyblackrule.route('/modifyblackrule', methods=['POST'])
def modify_black_rule():
    try:
        # 获取请求中的用户输入的 IP 地址
        user_ip = request.get_json().get('black_ip')

        if not user_ip or not is_valid_ip(user_ip):
            return jsonify({'status': 'error', 'message': '无效或缺失的 IP 地址'}), 400

        # 调用 descblackrule 接口，获取现有的黑名单配置
        response = requests.get('http://localhost:8891/api/descblackrule')

        if response.status_code != 200:
            return jsonify({'status': 'error', 'message': 'Failed to fetch data from descblackrule'}), 500

        data = response.json()
        # print(data)

        # 检查 message 是非空列表
        if "message" not in data or not isinstance(data["message"], list) or not data["message"]:
            return jsonify({'status': 'error', 'message': 'Invalid response structure'}), 500

        rule_info = data["message"][0]
        ip_list = rule_info.get("ip_list", [])
        rule_id = rule_info.get("rule_id")
        template_id = rule_info.get("template_id")

        if not rule_id or not template_id:
            return jsonify({'status': 'error', 'message': '缺少必要的规则 ID 或模板 ID'}), 500

        # 避免重复添加 IP
        if user_ip not in ip_list:
            ip_list.append(user_ip)

        # 构造新的规则数据
        updated_data = [{
            "action": "block",
            "id": rule_id,
            "name": "IpBlackList",
            "remoteAddr": ip_list
        }]
        rules_str = json.dumps(updated_data)
        # print(rules_str)

        # 创建防护规则请求
        client = create_client()
        modify_defense_rule_request = waf_openapi_20211001_models.ModifyDefenseRuleRequest(
            region_id=os.getenv("REGION_ID"),
            instance_id=os.getenv("INSTANCE_ID"),
            template_id=str(template_id),
            defense_scene='ip_blacklist',
            rules=rules_str
        )

        runtime = util_models.RuntimeOptions()
        client.modify_defense_rule_with_options(modify_defense_rule_request, runtime)

        return jsonify({'status': 'success', 'message': '黑名单规则已更新'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'内部错误: {str(e)}'}), 500
