import os
from flask import Blueprint, request, jsonify, session, g
from werkzeug.security import check_password_hash
from data.db_init import get_db_connection  # 复用db_init中的数据库连接函数
from dotenv import load_dotenv

# 加载环境变量（用于会话密钥）
load_dotenv()

# 创建蓝图（名称统一为'auth'，与url_prefix对应）
auth_bp = Blueprint('auth', __name__)

# -------------------------- 1. 修复数据库连接（关键：执行连接函数） --------------------------
def get_db():
    """获取数据库连接（确保返回的是连接对象，而非函数本身）"""
    if 'db' not in g:
        # 关键修复：调用 get_db_connection() 函数（加括号），执行连接并返回连接对象
        g.db = get_db_connection()  # 之前漏加括号，导致g.db是函数而非连接
    return g.db

# -------------------------- 2. 修复：请求结束关闭数据库连接（避免连接泄露） --------------------------
@auth_bp.teardown_app_request
def close_db(e=None):
    """请求结束后自动关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# -------------------------- 3. 修复：配置会话密钥（确保session能正常存储） --------------------------
@auth_bp.record_once
def on_load(state):
    """蓝图加载时配置会话密钥（Flask session必须有密钥才能使用）"""
    app = state.app
    # 从.env读取密钥，无则使用默认密钥（生产环境需配置复杂密钥）
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-thread-intel-secret-2025')
    # 可选：配置session有效期（如3600秒=1小时）
    app.permanent_session_lifetime = 3600

# -------------------------- 4. 登录接口（优化错误处理、参数校验） --------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    """登录接口：支持JSON参数，校验账号密码并创建会话"""
    try:
        # 兼容JSON和表单提交（避免只支持一种格式导致报错）
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # 提取并清洗参数
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 基础校验：非空、长度限制
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': '用户名和密码不能为空'
            }), 400
        if len(username) > 50 or len(password) > 50:
            return jsonify({
                'status': 'error',
                'message': '用户名或密码长度超出限制'
            }), 400

        # 获取数据库连接，查询用户
        db = get_db()
        with db.cursor() as cursor:  # 使用with语句自动关闭cursor
            # 只查询需要的字段（避免泄露敏感信息）
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = %s LIMIT 1",
                (username,)
            )
            user = cursor.fetchone()

        # 校验用户存在性和密码正确性
        if not user:
            return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401

        # 登录成功：创建会话（清除旧会话，存储关键信息）
        session.clear()
        session['user_id'] = user['id']       # 存储用户ID（用于后续加载用户）
        session['username'] = user['username']
        session['role'] = user['role']
        session.permanent = True  # 标记为永久会话（配合有效期配置）

        # 返回成功结果
        return jsonify({
            'status': 'success',
            'data': {
                'username': user['username'],
                'role': user['role']
            },
            'message': '登录成功'
        }), 200

    except Exception as e:
        # 打印错误堆栈，方便开发环境排查
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'登录失败：{str(e)}',
            'error_detail': traceback.format_exc() if os.getenv('FLASK_ENV') == 'development' else ''
        }), 500

# -------------------------- 5. 注销接口（保持不变，优化返回信息） --------------------------
@auth_bp.route('/logout', methods=['POST'])
def logout():
    """注销接口：清除会话，销毁登录状态"""
    session.clear()
    return jsonify({
        'status': 'success',
        'message': '已成功注销，如需继续操作请重新登录'
    }), 200

# -------------------------- 6. 加载当前登录用户（修复数据库连接调用） --------------------------
@auth_bp.before_app_request
def load_logged_in_user():
    """全局钩子：在每个请求前加载当前登录用户到g对象，供权限装饰器使用"""
    user_id = session.get('user_id')
    if user_id is None:
        g.current_user = None
    else:
        try:
            db = get_db()  # 正确获取数据库连接
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, role FROM users WHERE id = %s LIMIT 1",
                    (user_id,)
                )
                g.current_user = cursor.fetchone()
        except Exception as e:
            # 数据库查询失败时，重置登录状态
            session.clear()
            g.current_user = None
            import traceback
            traceback.print_exc()
            print(f"加载当前用户失败：{str(e)}")

# -------------------------- 7. 测试接口：验证登录状态（可选，用于调试） --------------------------
@auth_bp.route('/current-user', methods=['GET'])
def get_current_user():
    """测试接口：获取当前登录用户信息，验证登录状态是否正常"""
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