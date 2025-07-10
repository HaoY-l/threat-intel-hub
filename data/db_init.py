import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    return conn

def create_database_and_tables():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # 创建数据库（如果不存在）
        cursor.execute("CREATE DATABASE IF NOT EXISTS threat_intel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute("USE threat_intel;")
        # 创建漏洞表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS cve_data (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            cve_id VARCHAR(50) NOT NULL UNIQUE,
            title VARCHAR(255) NOT NULL DEFAULT '',
            published DATE NOT NULL DEFAULT '1970-01-01',
            source VARCHAR(50) NOT NULL DEFAULT '',
            severity VARCHAR(20) DEFAULT '',
            url VARCHAR(255) DEFAULT '',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_published (published),
            INDEX idx_severity (severity)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        """
        cursor.execute(create_table_sql)
    conn.close()

if __name__ == "__main__":
    create_database_and_tables()