# src/utils/casbin.py
from flask import g, jsonify
from functools import wraps
from src.utils.casbin_init import enforcer

def permission_required(obj, act):
    """
    Casbin 鉴权装饰器
    obj: 资源
    act: 动作
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            current_user = g.get("current_user")
            if not current_user:
                return jsonify({"status": "error", "message": "未登录"}), 401

            username = current_user["username"]

            if enforcer is None:
                return jsonify({"status": "error", "message": "Casbin 未初始化"}), 500

            if enforcer.enforce(username, obj, act):
                return f(*args, **kwargs)
            else:
                return jsonify({"status": "error", "message": "无权限访问"}), 403

        return wrapped
    return decorator
