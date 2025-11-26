from casbin import Adapter, Model
from data.db_init import get_db_connection
import pymysql

class DatabaseAdapter(Adapter):
    """Casbin 数据库适配器：从 MySQL 读取/保存权限策略"""

    def load_policy(self, model: Model) -> None:
        """加载策略（从数据库读取 role → permission → method 映射）"""
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT 
                        rp.role, 
                        p.permission_key, 
                        CASE p.method WHEN 'ALL' THEN '*' ELSE p.method END AS act
                    FROM role_permissions rp
                    JOIN permissions p ON rp.permission_id = p.id
                """
                cursor.execute(sql)
                policies = cursor.fetchall()

                for policy in policies:
                    model.add_policy("p", "p", [
                        policy["role"], 
                        policy["permission_key"], 
                        policy["act"]
                    ])
                print(f"✅ Casbin 从数据库加载 {len(policies)} 条权限策略")
        except Exception as e:
            print(f"❌ Casbin 加载数据库策略失败: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def save_policy(self, model: Model) -> bool:
        """保存策略（可选，当前用不到）"""
        return True

    def get_permission_key_by_route(self, route_path: str, method: str) -> str:
        """根据路径+方法获取 permission_key"""
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 精确匹配
                cursor.execute("""
                    SELECT permission_key FROM permissions
                    WHERE route_path = %s AND (method = %s OR method = 'ALL')
                """, (route_path, method))
                result = cursor.fetchone()
                if result:
                    return result["permission_key"]

                # 通配符匹配
                cursor.execute("""
                    SELECT permission_key FROM permissions
                    WHERE is_wildcard = 1 
                      AND (method = %s OR method = 'ALL')
                      AND %s LIKE CONCAT(route_path, '%%')
                """, (method, route_path))
                result = cursor.fetchone()
                return result["permission_key"] if result else None
        except Exception as e:
            print(f"❌ 查询接口权限映射失败: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    def get_permission_white_list(self) -> list:
        """返回白名单接口路径"""
        return [
            "/health", "/", "/static/*",
            "/api/auth/login", "/api/auth/register"
        ]
