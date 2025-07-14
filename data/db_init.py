import os,logging
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "threat_intel"),
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
        create_cve_table_sql = """
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
        cursor.execute(create_cve_table_sql)
        logging.info("CVE data table created or already exists.")

        # 创建IP威胁表
        create_ip_threat_table_sql = """
        CREATE TABLE IF NOT EXISTS ip_threat_intel (
            id VARCHAR(100) NOT NULL COMMENT '查询目标ID，如IP/URL/Hash',
            type VARCHAR(20) NOT NULL DEFAULT 'default' COMMENT '类型，如IP/URL/File',
            source VARCHAR(50) NOT NULL DEFAULT 'default' COMMENT '数据来源平台',
            reputation_score INT NOT NULL DEFAULT 0 COMMENT '综合风险评分',
            threat_level VARCHAR(20) DEFAULT NULL COMMENT '风险等级，如malicious/suspicious/harmless',
            last_update DATETIME DEFAULT NULL COMMENT '数据最后更新时间',
            details JSON DEFAULT NULL COMMENT '原始详细数据(JSON格式)',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
            PRIMARY KEY (id, source)
        )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='威胁IP情报表';
        """
        cursor.execute(create_ip_threat_table_sql)
        logging.info("IP threat intel table created or already exists.")

        # 创建URL威胁表
        create_url_threat_table_sql = """
        CREATE TABLE IF NOT EXISTS `url_threat_intel` (
            `id` VARCHAR(255) NOT NULL COMMENT '平台唯一ID，如 VirusTotal 的 hash ID',
            `type` VARCHAR(50) NOT NULL DEFAULT 'url' COMMENT '类型，固定为 url',
            `source` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '数据来源，如 virustotal',
            `target_url` TEXT COMMENT '原始URL地址',
            `reputation_score` INT DEFAULT 0 COMMENT '信誉值（如有）',
            `last_update` DATETIME DEFAULT NULL COMMENT '平台返回的最后更新时间',
            `details` JSON DEFAULT NULL COMMENT '原始平台返回完整数据',
            `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            PRIMARY KEY (`id`, `source`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_url_threat_table_sql)
        logging.info("URL threat intel table created or already exists.")

        # 创建文件哈希威胁表
        create_file_hash_threat_table_sql = """
        CREATE TABLE IF NOT EXISTS file_threat_intel (
            id VARCHAR(255) NOT NULL COMMENT '文件标识符(通常为SHA256)',
            type VARCHAR(50) DEFAULT 'file' COMMENT '数据类型',
            source VARCHAR(100) NOT NULL COMMENT '数据源',
            reputation_score INT DEFAULT 0 COMMENT '信誉分数',
            threat_level VARCHAR(50) DEFAULT NULL COMMENT '威胁等级',
            last_update TIMESTAMP DEFAULT NULL COMMENT '最后更新时间',
            details JSON DEFAULT NULL COMMENT '详细信息(JSON格式)',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            PRIMARY KEY (id, source),
            INDEX idx_source (source),
            INDEX idx_reputation (reputation_score),
            INDEX idx_threat_level (threat_level),
            INDEX idx_last_update (last_update)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件威胁情报表';
        """
        cursor.execute(create_file_hash_threat_table_sql)
        logging.info("File threat intel table created or already exists.")

    conn.close()

if __name__ == "__main__":
    create_database_and_tables()
    logging.info("Database and tables initialized successfully.")