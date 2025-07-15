# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os,sys,requests,json,ipaddress,re
from typing import List
from alibabacloud_waf_openapi20211001.client import Client as waf_openapi20211001Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_waf_openapi20211001 import models as waf_openapi_20211001_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from datetime import datetime
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

waf_deletewhite = Blueprint('waf_deletewhite', __name__)

load_dotenv()
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

    # 批量删除白名单规则
    @staticmethod
    def delect_old_rules(rule_id):
        print(f"开始删除规则 {rule_id}")
        client = waf_info.create_client()
        delete_defense_rule_request = waf_openapi_20211001_models.DeleteDefenseRuleRequest(
            region_id=os.getenv("REGION_ID"),
            instance_id=os.getenv("INSTANCE_ID"),
            template_id=os.getenv("WHITELIST_TEMPLATE_ID"),
            rule_ids=rule_id
        )
        runtime = util_models.RuntimeOptions()
        try:
            client.delete_defense_rule_with_options(delete_defense_rule_request, runtime)
        except Exception as error:
            print(error.message)

@waf_deletewhite.route('/deletewhite', methods=['POST'])
def delete_white():
    try:
        # 获取请求体中的 rule_id
        rule_id = request.json.get('rule_id')
        
        if not rule_id:
            # 如果没有提供 rule_id，返回错误信息
            return jsonify({'code': 400, 'msg': '缺少 rule_id 参数'}), 400

        # 调用删除规则的函数
        result = waf_info.delect_old_rules(rule_id)

        return jsonify({'code': 200, 'msg': '删除成功'}), 200
    except Exception as e:
        # 捕获并返回异常信息
        return jsonify({'code': 500, 'msg': f'内部错误: {str(e)}'}), 500
