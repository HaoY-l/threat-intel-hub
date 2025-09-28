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
            severity VARCHAR(50) DEFAULT '',
            url VARCHAR(255) DEFAULT '',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_published (published),
            INDEX idx_severity (severity)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

        """
        cursor.execute(create_cve_table_sql)
  

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


        # 创建操作历史表
        create_search_history_table_sql = """
        CREATE TABLE IF NOT EXISTS search_history (
            id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
            query VARCHAR(255) NOT NULL COMMENT '查询关键字',
            type VARCHAR(20) NOT NULL COMMENT '查询类型，如ip/url/file',
            timestamp DATETIME NOT NULL COMMENT '查询时间',
            results INT DEFAULT 0 COMMENT '结果数量',
            max_score INT DEFAULT 0 COMMENT '最大风险评分',
            max_threat_level VARCHAR(20) DEFAULT NULL COMMENT '最大威胁等级',

            -- 存储简化的详情数据，JSON格式
            detail_results JSON DEFAULT NULL COMMENT '查询结果详情，去掉大字段详情，方便快速读取',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

            INDEX idx_query (query),
            INDEX idx_type (type),
            INDEX idx_timestamp (timestamp),
            INDEX idx_max_threat_level (max_threat_level)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作查询历史表';"""
        cursor.execute(create_search_history_table_sql)

        create_blocked_ips_table_sql = """
        CREATE TABLE IF NOT EXISTS blocked_ips (
            id INT AUTO_INCREMENT PRIMARY KEY,
            block_ip VARCHAR(45) NOT NULL,
            attack_count INT NOT NULL,
            attack_type VARCHAR(50) DEFAULT NULL,
            attack_ratio DECIMAL(5,2) DEFAULT NULL,
            from_time DATETIME NOT NULL,
            to_time DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_blocked_ips_table_sql)

        create_ip_request_frequency_table_sql = """
        CREATE TABLE IF NOT EXISTS ip_request_frequency (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(45) NOT NULL,
            request_count INT NOT NULL,
            from_time DATETIME NOT NULL,
            to_time DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
        cursor.execute(create_ip_request_frequency_table_sql)

        create_daily_summary_table_sql = """
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            blocked_ip_count INT DEFAULT 0,
            high_frequency_ip_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY (date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
        cursor.execute(create_daily_summary_table_sql)

        create_protected_ip_table_sql = """
        CREATE TABLE IF NOT EXISTS protected_ip (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(45) NOT NULL COMMENT '被保护或处理的IP地址',
            action VARCHAR(50) NOT NULL COMMENT '执行的操作类型 (e.g., blacklisted, query_failed, processing_failed)',
            reason TEXT COMMENT '操作原因或错误信息',
            reputation_score FLOAT COMMENT '查询到的威胁情报分数，如果查询失败可能为NULL',
            action_time DATETIME NOT NULL COMMENT '执行此操作的时间',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
        ) COMMENT='WAF IP保护操作记录表';"""
        cursor.execute(create_protected_ip_table_sql)

        # 创建新闻表 
        create_news_data_table_sql = """
        CREATE TABLE IF NOT EXISTS news_data (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(500) NOT NULL DEFAULT '' COMMENT '新闻标题',
            summary TEXT COMMENT '新闻摘要',
            content TEXT COMMENT '新闻内容',
            source VARCHAR(100) NOT NULL DEFAULT '' COMMENT '新闻来源，例如 it之家、csdn',
            category VARCHAR(100) DEFAULT '' COMMENT '新闻分类',
            author VARCHAR(100) DEFAULT '' COMMENT '作者',
            url VARCHAR(500) DEFAULT '' COMMENT '原始链接，用于跳转',
            mobile_url VARCHAR(500) DEFAULT '' COMMENT '移动端链接',
            cover VARCHAR(500) DEFAULT '' COMMENT '封面图片',
            hot INT DEFAULT 0 COMMENT '热度值',
            timestamp BIGINT DEFAULT 0 COMMENT '新闻时间戳',
            published_at DATETIME DEFAULT NULL COMMENT '发布时间',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_source (source),
            INDEX idx_category (category),
            INDEX idx_timestamp (timestamp),
            INDEX idx_published_at (published_at),
            INDEX idx_hot (hot)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='新闻数据表';
        """
        cursor.execute(create_news_data_table_sql)

        # 创建邮件预测结果表
        create_phishing_results_table_sql = """
        CREATE TABLE IF NOT EXISTS phishing_results (
            id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
            timestamp DATETIME NOT NULL COMMENT '预测时间',
            result VARCHAR(20) NOT NULL COMMENT '预测结果：Phishing 或 Not Phishing',
            probability FLOAT(5,4) NOT NULL COMMENT '模型预测的概率值',
            email_content TEXT NOT NULL COMMENT '邮件原文内容',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
            INDEX idx_timestamp (timestamp),
            INDEX idx_result (result)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='邮件钓鱼预测结果表';
        """
        cursor.execute(create_phishing_results_table_sql)

        
    conn.close()

if __name__ == "__main__":
    create_database_and_tables()
    logging.info("Database and tables initialized successfully.")