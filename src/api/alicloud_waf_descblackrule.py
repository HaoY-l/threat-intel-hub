import os
from typing import List
from alibabacloud_waf_openapi20211001.client import Client as waf_openapi20211001Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_waf_openapi20211001 import models as waf_openapi_20211001_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from flask import Flask, request, jsonify, Blueprint
from dotenv import load_dotenv
load_dotenv()

waf_descrule = Blueprint('waf_descrule', __name__)

def create_client() -> waf_openapi20211001Client:
        config = open_api_models.Config(
            access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
            access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        )
        config.endpoint = f'wafopenapi.cn-hangzhou.aliyuncs.com'
        return waf_openapi20211001Client(config)

@waf_descrule.route('/descblackrule', methods=['GET'])
def desc_rule():
        client = create_client()
        describe_defense_rule_request = waf_openapi_20211001_models.DescribeDefenseRuleRequest(
            region_id=os.getenv("REGION_ID"),
            instance_id=os.getenv("INSTANCE_ID"),
            template_id=os.getenv("BLACKLIST_TEMPLATE_ID"),
            rule_id=os.getenv("BLACKLIST_RULES_ID")
        )
        runtime = util_models.RuntimeOptions()
        try:
            response = client.describe_defense_rule_with_options(describe_defense_rule_request, runtime)
            # 尝试获取 rule 对象
            rule_obj = getattr(response.body, 'rule', None)
            
            if rule_obj is None:
                return jsonify({'status': 'error', 'message': 'No rule object found in the response body.'}), 500

            if not hasattr(rule_obj, 'to_map'):
                return jsonify({'status': 'error', 'message': 'Rule object does not have to_map() method.'}), 500

            rule_dict = rule_obj.to_map()

            # 解析 Config 字段中的 IP 列表
            config_str = rule_dict.get('Config')
            if not config_str:
                return jsonify({'status': 'error', 'message': 'No Config field found.'}), 500

            import json
            try:
                config_data = json.loads(config_str)
                ip_list = config_data.get('remoteAddr', [])
            except json.JSONDecodeError:
                return jsonify({'status': 'error', 'message': 'Failed to parse Config JSON.'}), 500

            # 构造规则信息
            result = [{
                "template_id": rule_dict.get('TemplateId'),
                "rule_id": rule_dict.get('RuleId'),
                "rule_name": rule_dict.get('RuleName'),
                "ip_list": ip_list
            }]

            return jsonify({'status': 'success', 'message': result}), 200

        except Exception as error:
            print("Error:", error)
            return jsonify({'status': 'error', 'message': str(error)}), 500