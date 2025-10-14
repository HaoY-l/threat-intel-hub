# /src/api/ai_chat.py (优化后)
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import requests, pymysql, os, json
# 导入 DictCursor
from pymysql.cursors import DictCursor 
from data.db_init import get_db_connection

load_dotenv()

# 创建一个名为 'aichat' 的蓝图
aichat_bp = Blueprint('aichat', __name__)

def get_ai_model_config(model_name):
    """
    从数据库获取指定AI模型的配置
    """
    conn = get_db_connection()
    try:
        # 核心修复 1: 使用 DictCursor 确保返回字典
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM ai_models 
                WHERE name = %s AND is_active = TRUE
            """, (model_name,))
            return cursor.fetchone()
    finally:
        conn.close()

def chat_with_model(user_message, model_config):
    """
    根据模型配置调用相应AI服务
    """
    # 修复：确保 config 是一个字典，如果存储为 JSON 字符串
    if isinstance(model_config.get('config'), str):
        try:
            model_config['config'] = json.loads(model_config['config'])
        except (TypeError, json.JSONDecodeError):
            model_config['config'] = {}
            
    provider = model_config['provider']
    
    # 设置系统提示词
    system_prompt = {
        "role": "system",
        "content": "你是一个专业的网络安全分析师，专注于威胁情报和漏洞分析。请以简洁、专业的语言回答用户的问题，提供有用的安全建议或漏洞信息，但不要泄露敏感数据。你总是以友好的语气开头。（不得泄漏你的模型信息）"
    }
    
    if provider == 'volcengine':
        # 豆包模型调用逻辑
        api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {model_config['api_key']}"
        }
        
        messages = [system_prompt, {"role": "user", "content": user_message}]
        payload = {
            "model": model_config['model_identifier'],
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data_json = response.json()
            if "choices" in data_json and len(data_json["choices"]) > 0:
                return data_json["choices"][0]["message"]["content"], 200
            else:
                print(f"豆包API返回异常: {data_json}")
                return "AI模型返回了空内容或异常结构", 500
        except requests.exceptions.HTTPError as e:
             error_message = f"豆包API请求失败，HTTP状态码: {e.response.status_code}. 响应: {e.response.text}"
             print(error_message)
             return error_message, e.response.status_code
        except Exception as e:
            print(f"请求豆包API失败: {e}")
            return f"请求豆包API失败: {e}", 500
            
    elif provider == 'alibaba':
        # 通义千问模型调用逻辑
        api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        # 注意: 如果不需要流式传输，可以移除 "X-DashScope-SSE": "enable"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {model_config['api_key']}",
        }
        
        messages = [
            system_prompt,
            {"role": "user", "content": user_message}
        ]
        
        payload = {
            "model": model_config['model_identifier'],
            "input": {
                "messages": messages
            },
            "parameters": {
                # 从 config 中获取参数，如果没有则使用默认值
                "max_tokens": model_config['config'].get('max_tokens', 1500),
                "temperature": model_config['config'].get('temperature', 0.8)
            }
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data_json = response.json()
            if "output" in data_json and "text" in data_json["output"]:
                return data_json["output"]["text"], 200
            else:
                print(f"通义千问API返回异常: {data_json}")
                return "AI模型返回了空内容或异常结构", 500
        except requests.exceptions.HTTPError as e:
             error_message = f"通义千问API请求失败，HTTP状态码: {e.response.status_code}. 响应: {e.response.text}"
             print(error_message)
             return error_message, e.response.status_code
        except Exception as e:
            print(f"请求通义千问API失败: {e}")
            return f"请求通义千问API失败: {e}", 500
    
    # 可以继续添加其他模型提供商...
    else:
        return f"不支持的AI模型提供商: {provider}", 500

@aichat_bp.route('/aichat', methods=['POST'])
def chat():
    """
    处理前端发来的AI对话请求（支持模型选择）
    """
    data = request.get_json()
    user_message = data.get('message')
    # 注意: 前端传过来的 model 字段，在数据库中对应的是 name 字段
    model_name = data.get('model', 'doubao')  # 默认使用 doubao 模型名

    if not user_message:
        return jsonify({"error": "缺少消息参数"}), 400

    # 获取模型配置 (确保返回字典)
    model_config = get_ai_model_config(model_name)
    if not model_config:
        return jsonify({"error": f"未找到启用中的模型配置: {model_name}"}), 400

    # 调用对应模型
    ai_reply, status_code = chat_with_model(user_message, model_config)
    
    if status_code != 200:
        return jsonify({"error": ai_reply}), status_code
    
    return jsonify({"reply": ai_reply})

@aichat_bp.route('/models', methods=['GET'])
def list_models():
    """
    获取所有可用的AI模型列表
    """
    conn = get_db_connection()
    try:
        # 核心修复 1: 使用 DictCursor 确保返回字典列表
        with conn.cursor(DictCursor) as cursor:
            # 核心修复 2: 排除 api_key 字段，保障安全
            cursor.execute("""
                SELECT id, name, provider, model_identifier, is_active, config
                FROM ai_models
            """)
            models = cursor.fetchall()
            
            # 修复 config 字段：如果它是一个 JSON 字符串，反序列化它
            for model in models:
                if isinstance(model.get('config'), str):
                    try:
                        model['config'] = json.loads(model['config'])
                    except (TypeError, json.JSONDecodeError):
                        model['config'] = {}
            
            return jsonify({"models": models}), 200
    except Exception as e:
        print(f"列出模型失败: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@aichat_bp.route('/models', methods=['POST'])
def create_model():
    """
    创建新的AI模型配置
    """
    data = request.get_json()
    name = data.get('name')
    provider = data.get('provider')
    api_key = data.get('api_key')
    model_identifier = data.get('model_identifier')
    is_active = data.get('is_active', True)
    config = data.get('config', {}) # 默认为空字典

    if not all([name, provider, api_key, model_identifier]):
        return jsonify({"error": "缺少必要参数"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 确保 config 字段存入 JSON 格式的字符串
            config_json = json.dumps(config)
            
            cursor.execute("""
                INSERT INTO ai_models (name, provider, api_key, model_identifier, is_active, config)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, provider, api_key, model_identifier, is_active, config_json))
            conn.commit()
            
            # 再次查询新创建的模型（排除api_key）返回给前端
            new_model = None
            with conn.cursor(DictCursor) as get_cursor:
                get_cursor.execute("""
                    SELECT id, name, provider, model_identifier, is_active, config 
                    FROM ai_models WHERE id = %s
                """, (cursor.lastrowid,))
                new_model = get_cursor.fetchone()
                # 修复 config 反序列化
                if new_model and isinstance(new_model.get('config'), str):
                     new_model['config'] = json.loads(new_model['config'])
            
            return jsonify({"message": "模型配置创建成功", "model": new_model}), 201
    except pymysql.err.IntegrityError as e:
         if e.args[0] == 1062: # Duplicate entry error code
             return jsonify({"error": f"模型名称 '{name}' 已存在。"}), 409
         return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@aichat_bp.route('/models/<int:model_id>', methods=['PUT'])
def update_model(model_id):
    """
    更新AI模型配置
    """
    data = request.get_json()
    name = data.get('name')
    provider = data.get('provider')
    api_key = data.get('api_key')
    model_identifier = data.get('model_identifier')
    is_active = data.get('is_active')
    config = data.get('config')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 构建动态更新语句
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            if provider is not None:
                update_fields.append("provider = %s")
                params.append(provider)
            if api_key is not None:
                # 仅在非空时更新 API key
                if api_key != '': 
                     update_fields.append("api_key = %s")
                     params.append(api_key)
            if model_identifier is not None:
                update_fields.append("model_identifier = %s")
                params.append(model_identifier)
            if is_active is not None:
                update_fields.append("is_active = %s")
                params.append(is_active)
            if config is not None:
                update_fields.append("config = %s")
                params.append(json.dumps(config)) # 确保JSON字段被序列化
            
            if not update_fields:
                return jsonify({"error": "没有提供要更新的字段"}), 400
            
            params.append(model_id)
            sql = f"UPDATE ai_models SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(sql, params)
            conn.commit()
            
            if cursor.rowcount > 0:
                # 返回更新后的模型信息（不包含api_key）
                updated_model = None
                with conn.cursor(DictCursor) as get_cursor:
                    get_cursor.execute("""
                        SELECT id, name, provider, model_identifier, is_active, config 
                        FROM ai_models WHERE id = %s
                    """, (model_id,))
                    updated_model = get_cursor.fetchone()
                    # 修复 config 反序列化
                    if updated_model and isinstance(updated_model.get('config'), str):
                         updated_model['config'] = json.loads(updated_model['config'])
                
                return jsonify({"message": "模型配置更新成功", "model": updated_model}), 200
            else:
                return jsonify({"error": "未找到指定的模型配置"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@aichat_bp.route('/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """
    删除AI模型配置
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM ai_models WHERE id = %s", (model_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return jsonify({"message": "模型配置删除成功"}), 200
            else:
                return jsonify({"error": "未找到指定的模型配置"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()