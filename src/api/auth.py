import os
import datetime
from flask import Blueprint, request, jsonify, session, g
from werkzeug.security import check_password_hash
from data.db_init import get_db_connection
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建蓝图（url_prefix='/auth'，对应 /api/auth/* 路径）
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# -------------------------- 1. 定义并导出权限装饰器（核心修复） --------------------------
def login_required(func):
    """登录验证装饰器（供其他模块导入使用）"""
    def wrapper(*args, **kwargs):
        if not g.current_user:
            return jsonify({"status": "error", "message": "未登录，无访问权限"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def admin_required(func):
    """管理员验证装饰器（供其他模块导入使用）"""
    def wrapper(*args, **kwargs):
        if not g.current_user or g.current_user.get('role') != 'admin':
            return jsonify({"status": "error", "message": "无管理员权限，禁止访问"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# -------------------------- 2. 数据库连接管理 --------------------------
def get_db():
    """获取数据库连接（避免重复连接）"""
    if 'db' not in g:
        g.db = get_db_connection()  # 执行数据库连接函数
    return g.db

@auth_bp.teardown_app_request
def close_db(e=None):
    """请求结束后自动关闭数据库连接（避免泄露）"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# -------------------------- 3. Session 配置（密钥+过期时间） --------------------------
@auth_bp.record_once
def on_load(state):
    """蓝图加载时初始化 Session 配置"""
    app = state.app
    # 从环境变量获取密钥（必须配置）
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    if not app.secret_key:
        raise ValueError("ERROR: 必须在 .env 文件中配置 FLASK_SECRET_KEY！生成命令：openssl rand -hex 32")
    
    # 登录超时时间（默认15分钟=900秒）
    default_timeout = 900
    timeout_str = os.getenv('Login_timed_out', str(default_timeout))
    try:
        timeout_seconds = int(timeout_str)
        if timeout_seconds <= 0:
            raise ValueError("超时时间必须为正整数")
    except ValueError:
        timeout_seconds = default_timeout
        print(f"警告：Login_timed_out 配置无效，使用默认值 {default_timeout} 秒")
    
    app.permanent_session_lifetime = timeout_seconds
    print(f"✅ 登录超时时间配置完成：{timeout_seconds}秒（无操作自动退出）")

# -------------------------- 4. Session 续期（有操作则刷新过期时间） --------------------------
@auth_bp.before_app_request
def refresh_session_expiry():
    if 'user_id' in session and session.permanent:
        session.modified = True  # 标记修改，Flask 自动重置过期时间

# -------------------------- 5. 加载当前登录用户（全局可用 g.current_user） --------------------------
@auth_bp.before_app_request
def load_logged_in_user():
    """每个请求前加载用户信息到 g 对象"""
    user_id = session.get('user_id')
    g.current_user = None  # 初始化
    if user_id:
        try:
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, role FROM users WHERE id = %s LIMIT 1",
                    (user_id,)
                )
                g.current_user = cursor.fetchone()  # 字典格式：{'id': 1, 'username': 'admin', 'role': 'admin'}
        except Exception as e:
            session.clear()  # 数据库查询失败，强制注销
            print(f"❌ 加载用户信息失败：{str(e)}")

# -------------------------- 6. 登录接口 --------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    """登录接口（支持 JSON/表单提交）"""
    try:
        # 兼容 JSON 和表单提交
        data = request.get_json() if request.is_json else request.form.to_dict()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 基础校验
        if not username or not password:
            return jsonify({'status': 'error', 'message': '用户名和密码不能为空'}), 400
        if len(username) > 50 or len(password) > 50:
            return jsonify({'status': 'error', 'message': '用户名/密码长度不能超过50位'}), 400

        # 查询用户
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = %s LIMIT 1",
                (username,)
            )
            user = cursor.fetchone()

        # 校验密码
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401

        # 初始化 Session
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session.permanent = True  # 启用持久化 Session（配合过期时间）

        return jsonify({
            'status': 'success',
            'data': {'username': user['username'], 'role': user['role']},
            'message': '登录成功'
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'登录失败：{str(e)}',
            'error_detail': traceback.format_exc() if os.getenv('FLASK_ENV') == 'development' else ''
        }), 500

# -------------------------- 7. 注销接口 --------------------------
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """注销接口（清除 Session）"""
    session.clear()
    return jsonify({
        'status': 'success',
        'message': '已成功注销，如需继续操作请重新登录'
    }), 200

# -------------------------- 8. 测试接口（验证登录状态） --------------------------
@auth_bp.route('/current-user', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息（调试用）"""
    if g.current_user:
        return jsonify({
            'status': 'success',
            'data': g.current_user
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': '未登录或登录状态已失效'
        }), 401

# -------------------------- 显式导出（关键：供其他模块导入） --------------------------
__all__ = ['auth_bp', 'login_required', 'admin_required']