import os
from flask import Blueprint, request, jsonify, session, g  # 新增session和g
from werkzeug.security import check_password_hash
from data.db_init import get_db_connection

auth_bp = Blueprint('auth_bp', __name__)

# 新增数据库连接工具
def get_db():
    if 'db' not in g:
        g.db = get_db_connection
    return g.db

# 新增登录接口
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': '用户名和密码不能为空'}), 400
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401
    
    # 存储用户信息到会话
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    return jsonify({
        'status': 'success',
        'data': {
            'username': user['username'],
            'role': user['role']
        }
    })

# 新增注销接口
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success', 'message': '已注销'})

# 新增全局钩子：加载当前登录用户
@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.current_user = None
    else:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
        g.current_user = cursor.fetchone()