from data.db_init import get_db_connection

# ---------------- 查询所有权限 ----------------
def get_all_permissions():
    """
    返回权限列表，每条权限包含：
    id, permission_name, permission_key, method, module (可选), is_selected
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, permission_name, permission_key, method, route_path FROM permissions"
            cursor.execute(sql)
            result = cursor.fetchall()
            perms = []
            for row in result:
                perms.append({
                    "id": row["id"],
                    "permission_name": row["permission_name"],
                    "permission_key": row["permission_key"],
                    "method": row["method"],
                    "module": "other",  # 现有表没有 module 字段，统一用 other
                    "is_selected": False
                })
            return perms
    finally:
        conn.close()

# ---------------- 查询所有角色 ----------------
def get_all_roles():
    """
    返回角色列表：['admin','user','guest']
    因为没有单独的 roles 表，这里通过 role_permissions 表获取所有角色
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT DISTINCT role FROM role_permissions"
            cursor.execute(sql)
            return [row["role"] for row in cursor.fetchall()]
    finally:
        conn.close()

# ---------------- 查询角色拥有的权限 ----------------
def get_role_permissions(role_name):
    """
    返回指定角色拥有的 permission_key 列表
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT p.permission_key
                FROM role_permissions rp
                JOIN permissions p ON rp.permission_id = p.id
                WHERE rp.role = %s
            """
            cursor.execute(sql, (role_name,))
            return [row["permission_key"] for row in cursor.fetchall()]
    finally:
        conn.close()

# ---------------- 检查用户是否有权限 ----------------
def has_permission(role_name, permission_key):
    """
    判断某个角色是否拥有指定权限
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 1
                FROM role_permissions rp
                JOIN permissions p ON rp.permission_id = p.id
                WHERE rp.role = %s AND p.permission_key = %s
                LIMIT 1
            """
            cursor.execute(sql, (role_name, permission_key))
            return cursor.fetchone() is not None
    finally:
        conn.close()

# ---------------- 更新角色权限 ----------------
def update_role_permissions(role_name, permission_ids):
    """
    更新角色权限：
    - 删除原有权限
    - 插入新的权限列表
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 删除原权限
            cursor.execute("DELETE FROM role_permissions WHERE role=%s", (role_name,))
            # 批量插入新权限
            if permission_ids:
                insert_values = [(role_name, pid) for pid in permission_ids]
                cursor.executemany(
                    "INSERT INTO role_permissions(role, permission_id) VALUES (%s, %s)",
                    insert_values
                )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()
