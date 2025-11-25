from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_init import get_db_connection
from .auth import login_required, admin_required
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

# 初始化蓝图时添加 /auth 前缀（最终路径：/api/auth/users）
auth_users_bp = Blueprint('auth_users', __name__, url_prefix='/auth')

# -------------------------- 接口：查询所有用户（路由为 /users，配合前缀后是 /api/auth/users） --------------------------
@auth_users_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_all_users():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, role, created_at 
                FROM users 
                ORDER BY created_at DESC
            """)
            users = cursor.fetchall()
        return jsonify({
            "success": True,
            "count": len(users),
            "data": users
        }), 200
    except Exception as e:
        print(f"❌ 查询用户异常：{e}")
        return jsonify({
            "success": False,
            "message": f"查询用户失败：{str(e)}"
        }), 500
    finally:
        conn.close()

# -------------------------- 接口：新增用户 --------------------------
@auth_users_bp.route('/users', methods=['POST'])
@login_required
@admin_required
def add_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'user').strip()

        if not username or not password:
            return jsonify({"success": False, "message": "请输入用户名和密码"}), 400
        if len(username) < 3 or len(username) > 20:
            return jsonify({"success": False, "message": "用户名长度需在3-20位之间"}), 400
        if len(password) < 6:
            return jsonify({"success": False, "message": "密码长度至少6位"}), 400
        if role not in ['user', 'admin']:
            return jsonify({"success": False, "message": "角色只能是 user 或 admin"}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        conn = get_db_connection()

        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({"success": False, "message": "用户名已存在"}), 400

            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
            """, (username, hashed_password, role))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "新增用户成功",
            "data": {"username": username, "role": role}
        }), 201
    except Exception as e:
        conn.rollback() if 'conn' in locals() else None
        print(f"❌ 新增用户异常：{e}")
        return jsonify({
            "success": False,
            "message": f"新增用户失败：{str(e)}"
        }), 500
    finally:
        conn.close() if 'conn' in locals() else None

# -------------------------- 接口：删除用户 --------------------------
@auth_users_bp.route('/users/<username>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(username):
    if g.current_user and username == g.current_user.get('username'):
        return jsonify({"success": False, "message": "不能删除当前登录用户"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                return jsonify({"success": False, "message": "用户不存在"}), 404

            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"用户「{username}」删除成功"
        }), 200
    except Exception as e:
        conn.rollback()
        print(f"❌ 删除用户异常：{e}")
        return jsonify({
            "success": False,
            "message": f"删除用户失败：{str(e)}"
        }), 500
    finally:
        conn.close()

# -------------------------- 接口：重置用户密码 --------------------------
@auth_users_bp.route('/users/<username>/reset_password', methods=['PUT'])
@login_required
@admin_required
def reset_user_password(username):
    try:
        data = request.get_json() or {}
        new_password = data.get('password', '').strip()
        if not new_password or len(new_password) < 6:
            return jsonify({"success": False, "message": "密码长度至少6位"}), 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                return jsonify({"success": False, "message": "用户不存在"}), 404

            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            cursor.execute("UPDATE users SET password_hash=%s WHERE username=%s", (hashed_password, username))
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"用户「{username}」的密码已重置成功"
        }), 200
    except Exception as e:
        conn.rollback() if 'conn' in locals() else None
        print(f"❌ 重置密码异常：{e}")
        return jsonify({
            "success": False,
            "message": f"重置密码失败：{str(e)}"
        }), 500
    finally:
        conn.close() if 'conn' in locals() else None

__all__ = ['auth_users_bp']