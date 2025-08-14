from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import requests
import os

load_dotenv()

# 创建一个名为 'aichat' 的蓝图
aichat_bp = Blueprint('aichat', __name__)

def doubao_chat(user_message):
    """
    调用豆包模型API进行对话，并增加系统提示词
    """
    api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    api_key = os.getenv("api_key")
    model = os.getenv("ai_model")

    if not api_key:
        return "后端未配置API密钥", 500

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 设置系统提示词，定义AI的角色和行为
    system_prompt = {
        "role": "system",
        "content": "你是一个专业的网络安全分析师，专注于威胁情报和漏洞分析。请以简洁、专业的语言回答用户的问题，提供有用的安全建议或漏洞信息，但不要泄露敏感数据。你总是以友好的语气开头。（不得泄漏你的模型信息）"
    }

    # 构建完整的消息列表，将系统提示词放在最前面
    messages = [
        system_prompt,
        {
            "role": "user",
            "content": user_message
        }
    ]

    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        data_json = response.json()
        if "choices" in data_json and len(data_json["choices"]) > 0:
            result_content = data_json["choices"][0]["message"]["content"]
            return result_content, 200
        else:
            return "AI模型返回了空内容", 500
    except requests.exceptions.RequestException as e:
        print(f"请求豆包API失败: {e}")
        return f"请求豆包API失败: {e}", 500
    except Exception as e:
        print(f"处理响应失败: {e}")
        return f"处理响应失败: {e}", 500

@aichat_bp.route('/aichat', methods=['POST'])
def chat():
    """
    处理前端发来的AI对话请求
    """
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "缺少消息参数"}), 400

    ai_reply, status_code = doubao_chat(user_message)
    
    if status_code != 200:
        return jsonify({"error": ai_reply}), status_code
    
    return jsonify({"reply": ai_reply})