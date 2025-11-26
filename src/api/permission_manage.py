from flask import Blueprint, jsonify, g, request
from .auth import login_required, permission_required
from src.utils.permission_utils import (
    get_all_permissions,
    get_all_roles,
    get_role_permissions,
    update_role_permissions
)

# 初始化蓝图，最终路径 /api/permission
permission_manage_bp = Blueprint('permission_manage', __name__, url_prefix='/permission')

# ---------------- 查询所有权限 ----------------
@permission_manage_bp.route('/all', methods=['GET'])
@login_required
@permission_required('permission:manage')
def get_all_perm():
    try:
        permissions = get_all_permissions()
        return jsonify({"success": True, "data": permissions}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"查询所有权限失败：{str(e)}"}), 500

# ---------------- 查询所有角色 ----------------
@permission_manage_bp.route('/roles', methods=['GET'])
@login_required
@permission_required('permission:manage')
def get_all_role_list():
    try:
        roles = get_all_roles()  # 返回 ['admin','user','guest']
        return jsonify({"success": True, "data": roles}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"查询所有角色失败：{str(e)}"}), 500

# ---------------- 查询指定角色权限 ----------------
@permission_manage_bp.route('/role/<role>/permissions', methods=['GET'])
@login_required
def get_role_perm(role):
    try:
        role_perm_keys = get_role_permissions(role)  # 返回 ['phishing:predict','user:view']
        all_perms = get_all_permissions()
        # 标记哪些权限已被选中
        for perm in all_perms:
            perm['is_selected'] = perm['permission_key'] in role_perm_keys
        return jsonify({"success": True, "data": all_perms}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"查询角色「{role}」权限失败：{str(e)}"}), 500

# ---------------- 更新角色权限 ----------------
@permission_manage_bp.route('/role/<role>/permissions', methods=['PUT'])
@login_required
@permission_required('permission:manage')
def update_role_perm(role):
    try:
        data = request.get_json()
        permission_ids = data.get('permission_ids', [])
        if not isinstance(permission_ids, list):
            return jsonify({"success": False, "message": "权限ID列表必须是数组格式"}), 400
        result = update_role_permissions(role, permission_ids)
        if result:
            return jsonify({"success": True, "message": f"角色「{role}」权限更新成功"}), 200
        else:
            return jsonify({"success": False, "message": f"角色「{role}」权限更新失败，请重试"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"更新角色「{role}」权限失败：{str(e)}"}), 500

__all__ = ['permission_manage_bp']
