import logging
from data.db_init import get_db_connection

def get_role_permissions(role: str) -> list:
    """
    根据角色查询该角色拥有的所有权限标识（permission_key）
    :param role: 角色名称（如 admin/user）
    :return: 权限标识列表（如 ['user:list', 'user:add']）
    """
    permissions = []
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 关联查询角色对应的权限标识
            cursor.execute("""
                SELECT p.permission_key 
                FROM role_permissions rp
                JOIN permissions p ON rp.permission_id = p.id
                WHERE rp.role = %s
            """, (role,))
            results = cursor.fetchall()
            permissions = [item['permission_key'] for item in results]
    except Exception as e:
        logging.error(f"查询角色「{role}」权限失败：{str(e)}")
    finally:
        if conn:
            conn.close()
    return permissions

def has_permission(role: str, permission_key: str) -> bool:
    """
    校验角色是否拥有指定权限
    :param role: 角色名称
    :param permission_key: 权限标识（如 'user:list'）
    :return: 有权限返回 True，无则返回 False
    """
    if not role or not permission_key:
        return False
    # 获取角色的所有权限
    role_perms = get_role_permissions(role)
    # 判断目标权限是否在角色权限列表中
    return permission_key in role_perms

def get_all_permissions() -> list:
    """
    查询所有系统权限（用于前端权限管理页面）
    :return: 权限列表（包含 id、permission_key、permission_name、description）
    """
    permissions = []
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, permission_key, permission_name, description
                FROM permissions
                ORDER BY id ASC
            """)
            permissions = cursor.fetchall()
    except Exception as e:
        logging.error(f"查询所有权限失败：{str(e)}")
    finally:
        if conn:
            conn.close()
    return permissions

def get_all_roles() -> list:
    """
    查询所有系统角色（复用 users 表的 role 字段，去重）
    :return: 角色列表（如 ['admin', 'user']）
    """
    roles = []
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT role FROM users ORDER BY role ASC")
            results = cursor.fetchall()
            roles = [item['role'] for item in results]
            # 确保至少包含默认角色（防止无用户时角色列表为空）
            if 'user' not in roles:
                roles.append('user')
            if 'admin' not in roles:
                roles.append('admin')
    except Exception as e:
        logging.error(f"查询所有角色失败：{str(e)}")
    finally:
        if conn:
            conn.close()
    return roles

def update_role_permissions(role: str, permission_ids: list) -> bool:
    """
    更新角色的权限（先删除旧权限，再批量添加新权限）
    :param role: 角色名称
    :param permission_ids: 选中的权限ID列表（如 [1, 2, 3]）
    :return: 更新成功返回 True，失败返回 False
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. 删除该角色的所有旧权限（事务内执行）
            cursor.execute("DELETE FROM role_permissions WHERE role = %s", (role,))
            
            # 2. 批量插入新的角色-权限映射
            if permission_ids and isinstance(permission_ids, list):
                insert_data = [(role, perm_id) for perm_id in permission_ids]
                cursor.executemany(
                    "INSERT INTO role_permissions (role, permission_id) VALUES (%s, %s)",
                    insert_data
                )
        conn.commit()
        logging.info(f"更新角色「{role}」权限成功，新权限ID列表：{permission_ids}")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"更新角色「{role}」权限失败：{str(e)}")
        return False
    finally:
        if conn:
            conn.close()