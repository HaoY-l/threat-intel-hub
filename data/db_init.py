import os
import logging
import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash  # 密码加密工具

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection(use_db=True):
    """
    获取数据库连接
    :param use_db: 是否指定数据库（创建数据库时需设为 False）
    :return: pymysql 连接对象
    """
    db_params = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True
    }
    # 创建数据库时不指定 database 参数
    if use_db:
        db_params["database"] = os.getenv("MYSQL_DATABASE", "threat_intel")
    return pymysql.connect(**db_params)

def create_database_and_tables():
    """创建数据库和所有表（含用户、权限相关表）"""
    conn = None
    try:
        # 1. 先连接 MySQL（不指定数据库，用于创建数据库）
        conn = get_db_connection(use_db=False)
        with conn.cursor() as cursor:
            # 创建数据库（如果不存在）
            db_name = os.getenv("MYSQL_DATABASE", "threat_intel")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            logging.info(f"✅ 数据库 {db_name} 已创建或已存在")
            
            # 切换到目标数据库
            cursor.execute(f"USE {db_name};")

            # 2. 创建漏洞表
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
            logging.info("✅ cve_data 表已创建或已存在")

            # 3. 创建IP威胁表
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
            logging.info("✅ ip_threat_intel 表已创建或已存在")

            # 4. 创建URL威胁表
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
            logging.info("✅ url_threat_intel 表已创建或已存在")

            # 5. 创建文件哈希威胁表
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
            logging.info("✅ file_threat_intel 表已创建或已存在")

            # 6. 创建操作历史表
            create_search_history_table_sql = """
            CREATE TABLE IF NOT EXISTS search_history (
                id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
                query VARCHAR(255) NOT NULL COMMENT '查询关键字',
                type VARCHAR(20) NOT NULL COMMENT '查询类型，如ip/url/file',
                timestamp DATETIME NOT NULL COMMENT '查询时间',
                results INT DEFAULT 0 COMMENT '结果数量',
                max_score INT DEFAULT 0 COMMENT '最大风险评分',
                max_threat_level VARCHAR(20) DEFAULT NULL COMMENT '最大威胁等级',
                detail_results JSON DEFAULT NULL COMMENT '查询结果详情，去掉大字段详情，方便快速读取',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_query (query),
                INDEX idx_type (type),
                INDEX idx_timestamp (timestamp),
                INDEX idx_max_threat_level (max_threat_level)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作查询历史表';
            """
            cursor.execute(create_search_history_table_sql)
            logging.info("✅ search_history 表已创建或已存在")

            # 7. 创建拦截IP表
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
            logging.info("✅ blocked_ips 表已创建或已存在")

            # 8. 创建IP请求频率表
            create_ip_request_frequency_table_sql = """
            CREATE TABLE IF NOT EXISTS ip_request_frequency (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip VARCHAR(45) NOT NULL,
                request_count INT NOT NULL,
                from_time DATETIME NOT NULL,
                to_time DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_ip_request_frequency_table_sql)
            logging.info("✅ ip_request_frequency 表已创建或已存在")

            # 9. 创建每日汇总表
            create_daily_summary_table_sql = """
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                blocked_ip_count INT DEFAULT 0,
                high_frequency_ip_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY (date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_daily_summary_table_sql)
            logging.info("✅ daily_summary 表已创建或已存在")

            # 10. 创建保护IP表
            create_protected_ip_table_sql = """
            CREATE TABLE IF NOT EXISTS protected_ip (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip VARCHAR(45) NOT NULL COMMENT '被保护或处理的IP地址',
                action VARCHAR(50) NOT NULL COMMENT '执行的操作类型 (e.g., blacklisted, query_failed, processing_failed)',
                reason TEXT COMMENT '操作原因或错误信息',
                reputation_score FLOAT COMMENT '查询到的威胁情报分数，如果查询失败可能为NULL',
                action_time DATETIME NOT NULL COMMENT '执行此操作的时间',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
            ) COMMENT='WAF IP保护操作记录表';
            """
            cursor.execute(create_protected_ip_table_sql)
            logging.info("✅ protected_ip 表已创建或已存在")

            # 11. 创建新闻表
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
            logging.info("✅ news_data 表已创建或已存在")

            # 12. 创建邮件预测结果表
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
            logging.info("✅ phishing_results 表已创建或已存在")

            # 13. 创建邮箱配置表
            create_email_configs_table_sql = """
            CREATE TABLE IF NOT EXISTS email_configs (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
                username VARCHAR(255) NOT NULL COMMENT '邮箱用户名',
                passwd VARCHAR(255) NOT NULL COMMENT '邮箱密码',
                server VARCHAR(255) NOT NULL COMMENT 'IMAP服务器地址',
                port INT NOT NULL COMMENT 'IMAP端口',
                webhook_url TEXT NOT NULL COMMENT '企业微信Webhook URL',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='邮箱配置表';
            """
            cursor.execute(create_email_configs_table_sql)
            logging.info("✅ email_configs 表已创建或已存在")

            # 14. 创建AI模型配置表
            create_ai_models_table_sql = """
            CREATE TABLE IF NOT EXISTS ai_models (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE COMMENT '模型名称，如 doubao, qwen 等',
                api_key VARCHAR(255) NOT NULL COMMENT 'API密钥',
                model_identifier VARCHAR(100) NOT NULL COMMENT '模型标识符，如具体模型名',
                api_endpoint VARCHAR(255) NOT NULL COMMENT 'API调用地址',
                is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
                config JSON COMMENT '其他配置参数',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI模型配置表';
            """
            cursor.execute(create_ai_models_table_sql)
            logging.info("✅ ai_models 表已创建或已存在")

            # 15. 创建用户表
            create_users_table_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
                password_hash VARCHAR(255) NOT NULL COMMENT '加密存储的密码',
                role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色：admin/user',
                email VARCHAR(100) UNIQUE COMMENT '用户邮箱',
                is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';
            """
            cursor.execute(create_users_table_sql)
            logging.info("✅ users 表已创建或已存在")

            # 插入默认管理员用户
            default_admin_sql = """
            INSERT IGNORE INTO users (username, password_hash, role, email, is_active)
            VALUES (
                'threatintel',
                %s,
                'admin',
                'threatintel@example.com',
                TRUE
            )
            """
            # 生成密码哈希（默认密码：threatintel）
            hashed_password = generate_password_hash('threatintel', method='pbkdf2:sha256')
            cursor.execute(default_admin_sql, (hashed_password,))
            logging.info("✅ 默认管理员用户已初始化（用户名：threatintel，密码：threatintel）")

            # 16. 创建权限表
            create_permissions_table_sql = """
            CREATE TABLE IF NOT EXISTS permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                permission_key VARCHAR(50) NOT NULL UNIQUE COMMENT '权限唯一标识（需与接口对应，如 user:list）',
                permission_name VARCHAR(100) NOT NULL COMMENT '权限名称（如：查询用户列表）',
                description VARCHAR(255) DEFAULT '' COMMENT '权限描述（说明该权限控制的功能）',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_permission_key (permission_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统权限表（控制接口/功能访问）';
            """
            cursor.execute(create_permissions_table_sql)
            logging.info("✅ permissions 表已创建或已存在")

            # 17. 创建角色-权限关联表
            create_role_permissions_table_sql = """
            CREATE TABLE IF NOT EXISTS role_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                role VARCHAR(20) NOT NULL COMMENT '角色（复用 users 表的 role 字段，如 admin/user）',
                permission_id INT NOT NULL COMMENT '权限ID（关联 permissions 表）',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                UNIQUE KEY uk_role_permission (role, permission_id),
                FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE,
                INDEX idx_role (role),
                INDEX idx_permission_id (permission_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色-权限关联表（控制角色拥有的权限）';
            """
            cursor.execute(create_role_permissions_table_sql)
            logging.info("✅ role_permissions 表已创建或已存在")

            # 18. 初始化默认权限
            init_permissions_sql = """
            INSERT IGNORE INTO permissions (permission_key, permission_name, description) VALUES
            -- 1. 用户管理相关权限
            ('user:list', '查询用户列表', '查看系统所有用户信息'),
            ('user:add', '新增用户', '创建新的系统用户'),
            ('user:delete', '删除用户', '删除系统用户（不含自己）'),
            -- 2. 威胁情报查询相关权限
            ('threat:ip:query', '查询IP威胁情报', '查询 ip_threat_intel 表数据'),
            ('threat:url:query', '查询URL威胁情报', '查询 url_threat_intel 表数据'),
            ('threat:file:query', '查询文件威胁情报', '查询 file_threat_intel 表数据'),
            ('threat:cve:query', '查询CVE漏洞情报', '查询 cve_data 表数据'),
            -- 3. WAF相关权限
            ('waf:blocked:list', '查看拦截IP列表', '查看 blocked_ips 表数据'),
            ('waf:blocked:add', '新增拦截IP', '向 blocked_ips 表添加记录'),
            ('waf:blocked:delete', '删除拦截IP', '删除 blocked_ips 表记录'),
            ('waf:protected:list', '查看保护IP列表', '查看 protected_ip 表数据'),
            -- 4. 操作历史相关权限
            ('history:list', '查看查询历史', '查看 search_history 表数据'),
            ('history:delete', '删除查询历史', '删除 search_history 表数据'),
            -- 5. 新闻/邮件相关权限
            ('news:list', '查看安全新闻', '查看 news_data 表数据'),
            ('phishing:list', '查看钓鱼邮件预测结果', '查看 phishing_results 表数据'),
            ('email:config:manage', '管理邮箱配置', '增删改查 email_configs 表数据'),
            -- 6. AI模型相关权限
            ('ai:model:list', '查看AI模型配置', '查看 ai_models 表数据'),
            ('ai:model:manage', '管理AI模型配置', '增删改查 ai_models 表数据'),
            -- 7. 权限管理相关权限（仅超级管理员可用）
            ('permission:manage', '配置角色权限', '管理 role_permissions 表数据，分配角色权限');
            """
            cursor.execute(init_permissions_sql)
            logging.info("✅ 默认权限已初始化")

            # 19. 初始化角色-权限映射（核心修复：分条执行SQL）
            init_role_permissions_sql = [
                # 管理员（admin）：拥有所有权限
                "INSERT IGNORE INTO role_permissions (role, permission_id) SELECT 'admin', id FROM permissions;",
                # 普通用户（user）：仅拥有「查询类权限」
                """INSERT IGNORE INTO role_permissions (role, permission_id)
                   SELECT 'user', id FROM permissions WHERE permission_key IN (
                       'threat:ip:query',
                       'threat:url:query',
                       'threat:file:query',
                       'threat:cve:query',
                       'news:list',
                       'phishing:list',
                       'history:list'
                   );"""
            ]
            # 分条执行，避免多行SQL语法错误
            for sql in init_role_permissions_sql:
                cursor.execute(sql)
            logging.info("✅ 默认角色-权限映射已初始化")

        logging.info("🎉 所有数据库表创建和初始化完成！")

    except pymysql.MySQLError as e:
        logging.error(f"❌ MySQL 错误：{e.args[0]} - {e.args[1]}")
        raise
    except Exception as e:
        logging.error(f"❌ 创建数据库表失败：{str(e)}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("🔌 数据库连接已关闭")

if __name__ == "__main__":
    create_database_and_tables()
    logging.info("✅ 数据库初始化脚本执行完成")