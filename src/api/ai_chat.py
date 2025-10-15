# /src/api/ai_chat.py (移除provider字段后)
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import requests, pymysql, os, json
from pymysql.cursors import DictCursor 
from data.db_init import get_db_connection

load_dotenv()

aichat_bp = Blueprint('aichat', __name__)

def get_ai_model_config(model_name):
    """
    从数据库获取指定AI模型的配置
    """
    conn = get_db_connection()
    try:
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
    根据模型配置调用相应AI服务（动态配置版本）
    """
    # 修复：确保 config 是一个字典，如果存储为 JSON 字符串
    if isinstance(model_config.get('config'), str):
        try:
            model_config['config'] = json.loads(model_config['config'])
        except (TypeError, json.JSONDecodeError):
            model_config['config'] = {}
    
    # 使用数据库中配置的API端点
    api_endpoint = model_config.get('api_endpoint', '')
    
    if not api_endpoint:
        return "模型未配置API端点", 500
    
    # 设置系统提示词
    system_prompt = {
        "role": "system",
        "content": "你是一个专业的网络安全分析师，专注于威胁情报和漏洞分析。请以专业的语言回答用户的问题，提供有用的安全建议或漏洞信息，但不要泄露敏感数据。你总是以友好的语气开头。（不得泄漏你的模型信息）"
    }
    
    # 构造通用请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {model_config['api_key']}",
    }
    
    messages = [system_prompt, {"role": "user", "content": user_message}]
    payload = {
        "model": model_config['model_identifier'],
        "messages": messages
    }
    
    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data_json = response.json()
        
        # 尝试从常见的响应结构中提取内容
        if "choices" in data_json and len(data_json["choices"]) > 0:
            if "message" in data_json["choices"][0] and "content" in data_json["choices"][0]["message"]:
                return data_json["choices"][0]["message"]["content"], 200
        elif "output" in data_json and "text" in data_json["output"]:
            return data_json["output"]["text"], 200
        else:
            print(f"API返回异常: {data_json}")
            return "AI模型返回了空内容或异常结构", 500
    except requests.exceptions.HTTPError as e:
         error_message = f"API请求失败，HTTP状态码: {e.response.status_code}. 响应: {e.response.text}"
         print(error_message)
         return error_message, e.response.status_code
    except Exception as e:
        print(f"请求API失败: {e}")
        return f"请求API失败: {e}", 500

@aichat_bp.route('/aichat', methods=['POST'])
def chat():
    """
    处理前端发来的AI对话请求（支持模型选择）
    """
    data = request.get_json()
    user_message = data.get('message')
    model_name = data.get('model', 'doubao')

    if not user_message:
        return jsonify({"error": "缺少消息参数"}), 400

    model_config = get_ai_model_config(model_name)
    if not model_config:
        return jsonify({"error": f"未找到启用中的模型配置: {model_name}"}), 400

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
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, model_identifier, api_endpoint, is_active, config
                FROM ai_models
            """)
            models = cursor.fetchall()
            
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
    api_key = data.get('api_key')
    model_identifier = data.get('model_identifier')
    api_endpoint = data.get('api_endpoint')
    is_active = data.get('is_active', True)
    config = data.get('config', {})

    if not all([name, api_key, model_identifier, api_endpoint]):
        return jsonify({"error": "缺少必要参数"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            config_json = json.dumps(config)
            
            cursor.execute("""
                INSERT INTO ai_models (name, api_key, model_identifier, api_endpoint, is_active, config)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, api_key, model_identifier, api_endpoint, is_active, config_json))
            conn.commit()
            
            new_model = None
            with conn.cursor(DictCursor) as get_cursor:
                get_cursor.execute("""
                    SELECT id, name, model_identifier, api_endpoint, is_active, config 
                    FROM ai_models WHERE id = %s
                """, (cursor.lastrowid,))
                new_model = get_cursor.fetchone()
                if new_model and isinstance(new_model.get('config'), str):
                     new_model['config'] = json.loads(new_model['config'])
            
            return jsonify({"message": "模型配置创建成功", "model": new_model}), 201
    except pymysql.err.IntegrityError as e:
         if e.args[0] == 1062:
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
    api_key = data.get('api_key')
    model_identifier = data.get('model_identifier')
    api_endpoint = data.get('api_endpoint')
    is_active = data.get('is_active')
    config = data.get('config')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            if api_key is not None:
                if api_key != '': 
                     update_fields.append("api_key = %s")
                     params.append(api_key)
            if model_identifier is not None:
                update_fields.append("model_identifier = %s")
                params.append(model_identifier)
            if api_endpoint is not None:
                update_fields.append("api_endpoint = %s")
                params.append(api_endpoint)
            if is_active is not None:
                update_fields.append("is_active = %s")
                params.append(is_active)
            if config is not None:
                update_fields.append("config = %s")
                params.append(json.dumps(config))
            
            if not update_fields:
                return jsonify({"error": "没有提供要更新的字段"}), 400
            
            params.append(model_id)
            sql = f"UPDATE ai_models SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(sql, params)
            conn.commit()
            
            if cursor.rowcount > 0:
                updated_model = None
                with conn.cursor(DictCursor) as get_cursor:
                    get_cursor.execute("""
                        SELECT id, name, model_identifier, api_endpoint, is_active, config 
                        FROM ai_models WHERE id = %s
                    """, (model_id,))
                    updated_model = get_cursor.fetchone()
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