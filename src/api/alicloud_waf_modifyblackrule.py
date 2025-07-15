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
    # 获取请求中的用户输入的 IP 地址
    user_ip = request.get_json().get('black_ip')  # 获取用户提交的 'black_ip' 字段

    # 调用 descblackrule 接口，获取现有的黑名单配置
    response = requests.get('http://localhost:5003/api/waf/descblackrule')
    
    if response.status_code == 200:
        data = response.json()  # 将响应解析为 JSON 字典
        
        # 检查返回的结构是否包含我们需要的字段
        if "message" not in data or "Config" not in data["message"]:
            return jsonify({'status': 'error', 'message': 'Invalid response data structure'}), 500
        
        config = data["message"]["Config"]

        # 如果 config 是字符串，尝试将其解析为字典
        if isinstance(config, str):
            try:
                config = json.loads(config)  # 尝试将字符串转换为 JSON 对象
            except json.JSONDecodeError as e:
                return jsonify({'status': 'error', 'message': f"Failed to parse config JSON: {e}"}), 500
        
        # 确保 config 现在是字典
        if not isinstance(config, dict):
            return jsonify({'status': 'error', 'message': 'Config is not a valid dictionary'}), 500
        
        remote_addr = config.get("remoteAddr", [])
        
        if user_ip and user_ip not in remote_addr:  # 检查用户 IP 是否存在于列表中，避免重复
            remote_addr.append(user_ip)  # 将用户输入的 IP 加入到 remoteAddr 列表中
        # 更新后的配置数据
        updated_data = [{'action': 'block', 'id': os.getenv("BLACKLIST_RULES_ID"), 'name': 'IpBlackList', 'remoteAddr': remote_addr}]
        rules_str = json.dumps(updated_data)
        # 创建防护规则请求
        client = create_client()
        create_defense_rule_request = waf_openapi_20211001_models.CreateDefenseRuleRequest(
            region_id=os.getenv("REGION_ID"),
            instance_id=os.getenv("INSTANCE_ID"),
            template_id=os.getenv("BLACKLIST_TEMPLATE_ID"),
            defense_scene='ip_blacklist',
            rules=rules_str  # 转换为 JSON 字符串
        )
        
        runtime = util_models.RuntimeOptions()
        try:
            client.create_defense_rule_with_options(create_defense_rule_request, runtime)
            return jsonify({'status': 'success', 'message': 'Rule updated successfully'}), 200
        except Exception as error:
            return jsonify({'status': 'error', 'message': str(error)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Failed to fetch data from descblackrule'}), 500
