# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os,ipaddress,re,json
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

waf_addwhite = Blueprint('waf_addwhite', __name__)

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

    # 批量添加白名单规则
    @staticmethod
    def create_new_rules(data):
        client = waf_info.create_client()
        create_defense_rule_request = waf_openapi_20211001_models.CreateDefenseRuleRequest(
            region_id=os.getenv("REGION_ID"),
            instance_id=os.getenv("INSTANCE_ID"),
            template_id=os.getenv("WHITELIST_TEMPLATE_ID"),
            defense_scene='whitelist',
            rules=json.dumps(data)  # 注意：这里需要将列表转换为 JSON 字符串，才能正确发送到 WAF API
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = client.create_defense_rule_with_options(create_defense_rule_request, runtime)
            return response
        except Exception as error:
            print(error.message)

@waf_addwhite.route('/addwhite', methods=['POST'])
def add_white():
    try:
        if 'target' in request.form:
            target_str = request.form['target']
            data = json.loads(target_str)  # 解析JSON字符串
        else:
            # 如果表单中没有，尝试从JSON中获取
            data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "请求体不能为空"}), 400

        if not isinstance(data, list):
            return jsonify({"status": "error", "message": "数据格式错误，应该是 JSON 数组"}), 400

        for item in data:
            if not isinstance(item, dict):
                return jsonify({"status": "error", "message": "规则数据格式错误"}), 400

            # 校验字段是否存在
            required_keys = ["name", "tags", "status", "origin", "conditions"]
            for key in required_keys:
                if key not in item:
                    return jsonify({"status": "error", "message": f"缺少必填字段: {key}"}), 400

            if not isinstance(item["conditions"], list) or len(item["conditions"]) == 0:
                return jsonify({"status": "error", "message": "conditions 必须是非空列表"}), 400

            for condition in item["conditions"]:
                if not isinstance(condition, dict):
                    return jsonify({"status": "error", "message": "conditions 格式错误"}), 400

                if "values" not in condition or not condition["values"]:
                    return jsonify({"status": "error", "message": "conditions 中缺少 values"}), 400

                value = condition["values"]
                if not (is_valid_ip(value) or is_valid_domain(value) or is_valid_url_path(value)):
                    return jsonify({"status": "error", "message": f"无效的 values: {value}"}), 400

        # 🚀 调用 WAF API，并获取返回结果
        response = waf_info.create_new_rules(data)
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "白名单添加成功"}), 200
        else:
            return jsonify({"status": "error", "message": "白名单添加失败"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"内部错误: {str(e)}"}), 500