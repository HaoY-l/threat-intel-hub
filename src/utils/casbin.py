from flask import g, jsonify
from functools import wraps
from app import enforcer  # 导入Casbin实例

def permission_required(obj, act):
    """权限校验装饰器：检查用户是否有权限访问指定接口"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            current_user = g.get('current_user')
            if not current_user:
                return jsonify({'status': 'error', 'message': '未登录'}), 401
            
            # 校验权限（用户名、接口路径、HTTP方法）
            if enforcer.enforce(current_user['username'], obj, act):
                return f(*args, **kwargs)
            else:
                return jsonify({'status': 'error', 'message': '无权限访问'}), 403
        return wrapped
    return decorator