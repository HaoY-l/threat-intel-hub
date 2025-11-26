from flask import Blueprint, jsonify, g
from .auth import login_required, permission_required
from src.utils.permission_utils import (
    get_all_permissions,
    get_all_roles,
    get_role_permissions,
    update_role_permissions,
    get_role_permissions as get_role_perm_keys
)
from data.db_init import get_db_connection

# 初始化蓝图（最终路径：/api/permission）
permission_manage_bp = Blueprint('permission_manage', __name__, url_prefix='/permission')

# -------------------------- 接口1：查询所有权限（供前端权限管理页面加载）--------------------------
@permission_manage_bp.route('/all', methods=['GET'])
@login_required
@permission_required('permission:manage')  # 仅拥有权限管理权限的用户可访问
def get_all_perm():
    try:
        permissions = get_all_permissions()
        return jsonify({
            "success": True,
            "data": permissions
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"查询所有权限失败：{str(e)}"
        }), 500

# -------------------------- 接口2：查询所有角色（供前端下拉选择）--------------------------
@permission_manage_bp.route('/roles', methods=['GET'])
@login_required
@permission_required('permission:manage')
def get_all_role_list():
    try:
        roles = get_all_roles()
        return jsonify({
            "success": True,
            "data": roles
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"查询所有角色失败：{str(e)}"
        }), 500

# -------------------------- 接口3：查询指定角色的已拥有权限（供前端回显勾选状态）--------------------------
@permission_manage_bp.route('/role/<role>/permissions', methods=['GET'])
@login_required
@permission_required('permission:manage')
def get_role_perm(role):
    try:
        # 先查询该角色的权限标识列表
        perm_keys = get_role_perm_keys(role)
        # 再查询所有权限，标记哪些是该角色已拥有的
        all_perms = get_all_permissions()
        for perm in all_perms:
            perm['is_selected'] = perm['permission_key'] in perm_keys
        
        return jsonify({
            "success": True,
            "data": all_perms
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"查询角色「{role}」权限失败：{str(e)}"
        }), 500

# -------------------------- 接口4：更新指定角色的权限（核心：保存前端配置）--------------------------
@permission_manage_bp.route('/role/<role>/permissions', methods=['PUT'])
@login_required
@permission_required('permission:manage')
def update_role_perm(role):
    try:
        from flask import request
        data = request.get_json()
        permission_ids = data.get('permission_ids', [])
        
        # 校验权限ID列表格式
        if not isinstance(permission_ids, list):
            return jsonify({
                "success": False,
                "message": "权限ID列表必须是数组格式"
            }), 400
        
        # 执行更新
        result = update_role_permissions(role, permission_ids)
        if result:
            return jsonify({
                "success": True,
                "message": f"角色「{role}」权限更新成功"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": f"角色「{role}」权限更新失败，请重试"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新角色「{role}」权限失败：{str(e)}"
        }), 500

__all__ = ['permission_manage_bp']