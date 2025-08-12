import requests,json,os,markdown,time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,os,logging

import whois
from data.db_init import get_db_connection
from flask import Blueprint, request, jsonify
from datetime import datetime
# 加载环境变量
load_dotenv()

# 创建蓝图
tools_bp = Blueprint('/', __name__, url_prefix='/')

@tools_bp.route('/ip_query', methods=['GET'])
def ip_query():
    """
    接收IP地址作为GET参数，使用 ip-api.com 返回其归属地信息。
    """
    ip = request.args.get('ip')
    
    if not ip:
        return jsonify({
            "success": False,
            "message": "IP地址是必须的参数，请在URL中以'?ip=...'形式提供。"
        }), 400

    try:
        # 使用 ip-api.com 的免费API
        url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'success':
            return jsonify({
                "success": True,
                "ip": data.get('query'),
                "country": data.get('country'),
                "city": data.get('city'),
                "isp": data.get('isp')
            })
        else:
            return jsonify({
                "success": False,
                "message": data.get('message', '无效的IP地址或未知错误。')
            }), 400

    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "message": f"API请求失败: {e}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"处理响应时发生错误: {e}"
        }), 500

# 新增：域名Whois查询接口
@tools_bp.route('/whois_query', methods=['GET'])
def whois_query():
    domain = request.args.get('domain')
    
    if not domain:
        return jsonify({"success": False, "message": "域名是必须的参数。"}), 400

    try:
        # 修改这里：使用 whois.whois(...)
        whois_info = whois.whois(domain)
        
        if whois_info.domain_name:
            result = {
                "success": True,
                "domain_name": whois_info.domain_name,
                "registrar": whois_info.registrar,
                "creation_date": str(whois_info.creation_date),
                "expiration_date": str(whois_info.expiration_date),
                "updated_date": str(whois_info.updated_date),
                "name_servers": whois_info.name_servers,
                "status": whois_info.status
            }
            return jsonify(result)
        else:
            return jsonify({"success": False, "message": "未找到 Whois 信息或域名无效。"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"查询失败: {e}"}), 500