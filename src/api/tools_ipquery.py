import requests,json,os,markdown,time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,os,logging
from data.db_init import get_db_connection
from flask import Blueprint, request, jsonify
from datetime import datetime
# 加载环境变量
load_dotenv()

# 创建蓝图
ipquery_bp = Blueprint('ipquery', __name__, url_prefix='/')

@ipquery_bp.route('/ip_query', methods=['GET'])
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
