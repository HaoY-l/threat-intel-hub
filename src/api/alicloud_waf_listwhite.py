# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os,sys,requests,json,ipaddress,re
from flask import Blueprint, jsonify
from typing import List
from alibabacloud_waf_openapi20211001.client import Client as waf_openapi20211001Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_waf_openapi20211001 import models as waf_openapi_20211001_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
waf_listwhite = Blueprint('listwhite', __name__)  # 创建 WAF 蓝图

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

class waf_info:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> waf_openapi20211001Client:
        config = open_api_models.Config(
            access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
            access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        )
        config.endpoint = f'wafopenapi.cn-hangzhou.aliyuncs.com'
        return waf_openapi20211001Client(config)

    # 返回白名单规则列表，需要过滤出指定模版ID的rules
    @staticmethod
    def template_id_rules():
        client = waf_info.create_client()
        describe_defense_rules_request = waf_openapi_20211001_models.DescribeDefenseRulesRequest(
            region_id=os.getenv("REGION_ID"),
            instance_id=os.getenv("INSTANCE_ID"),
            rule_type='whitelist',
            page_number=1,
            page_size=1000
        )
        template_id = os.getenv("WHITELIST_TEMPLATE_ID")
        template_id_rules = []
        runtime = util_models.RuntimeOptions()
        try:
            response = client.describe_defense_rules_with_options(describe_defense_rules_request, runtime)
            all_rules = response.body.rules
            for rule in all_rules:
                if rule.template_id == int(template_id):
                    template_id_rules_dict = {
                        "rule_template" : rule.template_id,
                        "rule_id" : rule.rule_id,
                        "rule_name" : rule.rule_name
                    }
                    template_id_rules.append(template_id_rules_dict)
            return template_id_rules
        except Exception as error:
            print(error.message)
@waf_listwhite.route('/listwhite', methods=['GET'])
def list_white():
    template_id_rules = waf_info.template_id_rules()
    return jsonify({"status": "success", "message": template_id_rules}), 200

