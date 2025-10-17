import requests,json,os,markdown,time,base64,hashlib
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,os,logging

import whois,yaml,binascii
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
    


# ==================== Hash 计算器 ====================
@tools_bp.route('/tools/hash', methods=['POST'])
def calculate_hash():
    """
    计算多种哈希值（MD5/SHA-1/SHA-256/SHA-512）
    请求体：
    {
        "text": "要计算哈希的字符串",
        "algorithms": ["md5", "sha1", "sha256", "sha512"]  // 可选，默认全部
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        algorithms = data.get('algorithms', ['md5', 'sha1', 'sha256', 'sha512'])
        
        # 将字符串转换为字节
        text_bytes = text.encode('utf-8')
        
        result = {
            "success": True,
            "input": text,
            "hashes": {}
        }
        
        # 计算各种哈希值
        if 'md5' in algorithms:
            result['hashes']['md5'] = hashlib.md5(text_bytes).hexdigest()
        
        if 'sha1' in algorithms:
            result['hashes']['sha1'] = hashlib.sha1(text_bytes).hexdigest()
        
        if 'sha256' in algorithms:
            result['hashes']['sha256'] = hashlib.sha256(text_bytes).hexdigest()
        
        if 'sha512' in algorithms:
            result['hashes']['sha512'] = hashlib.sha512(text_bytes).hexdigest()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"哈希计算失败: {str(e)}"
        }), 500


# ==================== Base64 编码/解码 ====================
@tools_bp.route('/tools/base64/encode', methods=['POST'])
def base64_encode():
    """
    Base64 编码
    请求体：
    {
        "text": "要编码的字符串"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        
        return jsonify({
            "success": True,
            "input": text,
            "output": encoded
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Base64编码失败: {str(e)}"
        }), 500


@tools_bp.route('/tools/base64/decode', methods=['POST'])
def base64_decode():
    """
    Base64 解码
    请求体：
    {
        "text": "要解码的Base64字符串"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        decoded = base64.b64decode(text).decode('utf-8')
        
        return jsonify({
            "success": True,
            "input": text,
            "output": decoded
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Base64解码失败: {str(e)}"
        }), 500


# ==================== URL 编码/解码 ====================
@tools_bp.route('/tools/url/encode', methods=['POST'])
def url_encode():
    """
    URL 编码
    请求体：
    {
        "text": "要编码的字符串"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        encoded = quote(text)
        
        return jsonify({
            "success": True,
            "input": text,
            "output": encoded
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"URL编码失败: {str(e)}"
        }), 500


@tools_bp.route('/tools/url/decode', methods=['POST'])
def url_decode():
    """
    URL 解码
    请求体：
    {
        "text": "要解码的URL编码字符串"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        decoded = unquote(text)
        
        return jsonify({
            "success": True,
            "input": text,
            "output": decoded
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"URL解码失败: {str(e)}"
        }), 500


# ==================== Hex 编码/解码 ====================
@tools_bp.route('/tools/hex/encode', methods=['POST'])
def hex_encode():
    """
    Hex 编码
    请求体：
    {
        "text": "要编码的字符串"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        encoded = text.encode('utf-8').hex()
        
        return jsonify({
            "success": True,
            "input": text,
            "output": encoded
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Hex编码失败: {str(e)}"
        }), 500


@tools_bp.route('/tools/hex/decode', methods=['POST'])
def hex_decode():
    """
    Hex 解码
    请求体：
    {
        "text": "要解码的Hex字符串"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        decoded = bytes.fromhex(text).decode('utf-8')
        
        return jsonify({
            "success": True,
            "input": text,
            "output": decoded
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Hex解码失败: {str(e)}"
        }), 500


# ==================== JSON 格式化与验证 ====================
@tools_bp.route('/tools/json/format', methods=['POST'])
def json_format():
    """
    JSON 格式化、压缩或验证
    请求体：
    {
        "text": "JSON字符串",
        "action": "beautify" | "minify" | "validate"  // 默认 beautify
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        action = data.get('action', 'beautify')
        
        # 先验证JSON有效性
        try:
            json_obj = json.loads(text)
        except json.JSONDecodeError as e:
            return jsonify({
                "success": False,
                "message": f"无效的JSON格式: {str(e)}"
            }), 400
        
        result = {
            "success": True,
            "input": text,
            "valid": True
        }
        
        if action == 'beautify':
            result['output'] = json.dumps(json_obj, indent=2, ensure_ascii=False)
        elif action == 'minify':
            result['output'] = json.dumps(json_obj, separators=(',', ':'), ensure_ascii=False)
        elif action == 'validate':
            result['message'] = "JSON格式有效"
            result['output'] = text
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"JSON处理失败: {str(e)}"
        }), 500


# ==================== XML 格式化与验证 ====================
@tools_bp.route('/tools/xml/format', methods=['POST'])
def xml_format():
    """
    XML 格式化与验证
    请求体：
    {
        "text": "XML字符串",
        "action": "beautify" | "minify" | "validate"  // 默认 beautify
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        action = data.get('action', 'beautify')
        
        # 验证XML有效性
        try:
            dom = minidom.parseString(text)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"无效的XML格式: {str(e)}"
            }), 400
        
        result = {
            "success": True,
            "input": text,
            "valid": True
        }
        
        if action == 'beautify':
            result['output'] = dom.toprettyxml(indent="  ")
        elif action == 'minify':
            result['output'] = text.replace('\n', '').replace('  ', '')
        elif action == 'validate':
            result['message'] = "XML格式有效"
            result['output'] = text
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"XML处理失败: {str(e)}"
        }), 500


# ==================== YAML 格式化与验证 ====================
@tools_bp.route('/tools/yaml/format', methods=['POST'])
def yaml_format():
    """
    YAML 格式化与验证
    请求体：
    {
        "text": "YAML字符串",
        "action": "beautify" | "validate"  // 默认 beautify
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数 'text'"
            }), 400
        
        text = data['text']
        action = data.get('action', 'beautify')
        
        # 验证YAML有效性
        try:
            yaml_obj = yaml.safe_load(text)
        except yaml.YAMLError as e:
            return jsonify({
                "success": False,
                "message": f"无效的YAML格式: {str(e)}"
            }), 400
        
        result = {
            "success": True,
            "input": text,
            "valid": True
        }
        
        if action == 'beautify':
            result['output'] = yaml.dump(yaml_obj, allow_unicode=True, default_flow_style=False)
        elif action == 'validate':
            result['message'] = "YAML格式有效"
            result['output'] = text
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"YAML处理失败: {str(e)}"
        }), 500


# ==================== 多功能转换接口 ====================
@tools_bp.route('/tools/convert', methods=['POST'])
def multi_convert():
    """
    多功能转换接口
    请求体：
    {
        "text": "要转换的字符串",
        "from": "base64" | "url" | "hex",
        "to": "base64" | "url" | "hex" | "text"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'from' not in data or 'to' not in data:
            return jsonify({
                "success": False,
                "message": "缺少必需参数: text, from, to"
            }), 400
        
        text = data['text']
        from_format = data['from']
        to_format = data['to']
        
        # 先解码
        if from_format == 'base64':
            decoded = base64.b64decode(text).decode('utf-8')
        elif from_format == 'url':
            decoded = unquote(text)
        elif from_format == 'hex':
            decoded = bytes.fromhex(text).decode('utf-8')
        else:
            decoded = text
        
        # 再编码
        if to_format == 'base64':
            output = base64.b64encode(decoded.encode('utf-8')).decode('utf-8')
        elif to_format == 'url':
            output = quote(decoded)
        elif to_format == 'hex':
            output = decoded.encode('utf-8').hex()
        else:
            output = decoded
        
        return jsonify({
            "success": True,
            "input": text,
            "output": output,
            "conversion": f"{from_format} -> {to_format}"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"转换失败: {str(e)}"
        }), 500





