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
            sql = "SELECT id, permission_name, permission_key, method, module_name FROM permissions"
            cursor.execute(sql)
            result = cursor.fetchall()
            perms = []
            for row in result:
                perms.append({
                    "id": row[0],
                    "permission_name": row[1],
                    "permission_key": row[2],
                    "method": row[3],
                    "module": row[4] or "other",
                    "is_selected": False  # 默认未选中
                })
            return perms
    finally:
        conn.close()

# ---------------- 查询所有角色 ----------------
def get_all_roles():
    """
    返回角色列表：['admin','user','guest']
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT role_name FROM roles")
            return [row[0] for row in cursor.fetchall()]
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
                JOIN roles r ON rp.role_id = r.id
                WHERE r.role_name = %s
            """
            cursor.execute(sql, (role_name,))
            return [row[0] for row in cursor.fetchall()]
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
            # 获取角色ID
            cursor.execute("SELECT id FROM roles WHERE role_name=%s", (role_name,))
            role_row = cursor.fetchone()
            if not role_row:
                return False
            role_id = role_row[0]

            # 删除原权限
            cursor.execute("DELETE FROM role_permissions WHERE role_id=%s", (role_id,))

            # 批量插入新权限
            if permission_ids:
                insert_values = [(role_id, pid) for pid in permission_ids]
                cursor.executemany(
                    "INSERT INTO role_permissions(role_id, permission_id) VALUES (%s, %s)",
                    insert_values
                )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

# ---------------- 判断角色是否拥有某个权限 ----------------
def has_permission(role_name, permission_key):
    """
    判断指定角色是否拥有指定权限
    :param role_name: 角色名
    :param permission_key: 权限key
    :return: True/False
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 1
                FROM role_permissions rp
                JOIN permissions p ON rp.permission_id = p.id
                JOIN roles r ON rp.role_id = r.id
                WHERE r.role_name=%s AND p.permission_key=%s
                LIMIT 1
            """
            cursor.execute(sql, (role_name, permission_key))
            return cursor.fetchone() is not None
    finally:
        conn.close()
