/*
 Navicat Premium Dump SQL

 Source Server         : 218.244.149.26
 Source Server Type    : MySQL
 Source Server Version : 80027 (8.0.27)
 Source Host           : 218.244.149.26:3340
 Source Schema         : threat_intel

 Target Server Type    : MySQL
 Target Server Version : 80027 (8.0.27)
 File Encoding         : 65001

 Date: 20/08/2025 10:27:07
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for blocked_ips
-- ----------------------------
DROP TABLE IF EXISTS `blocked_ips`;
CREATE TABLE `blocked_ips` (
  `id` int NOT NULL AUTO_INCREMENT,
  `block_ip` varchar(45) NOT NULL,
  `attack_count` int NOT NULL,
  `attack_type` varchar(50) DEFAULT NULL,
  `attack_ratio` decimal(5,2) DEFAULT NULL,
  `from_time` datetime NOT NULL,
  `to_time` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for cve_data
-- ----------------------------
DROP TABLE IF EXISTS `cve_data`;
CREATE TABLE `cve_data` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `cve_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `published` date NOT NULL DEFAULT '1970-01-01',
  `source` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `severity` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '',
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cve_id` (`cve_id`),
  KEY `idx_published` (`published`),
  KEY `idx_severity` (`severity`)
) ENGINE=InnoDB AUTO_INCREMENT=11071 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for daily_summary
-- ----------------------------
DROP TABLE IF EXISTS `daily_summary`;
CREATE TABLE `daily_summary` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `blocked_ip_count` int DEFAULT '0',
  `high_frequency_ip_count` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for file_threat_intel
-- ----------------------------
DROP TABLE IF EXISTS `file_threat_intel`;
CREATE TABLE `file_threat_intel` (
  `id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件标识符(通常为SHA256)',
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'file' COMMENT '数据类型',
  `source` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '数据源',
  `reputation_score` int DEFAULT '0' COMMENT '信誉分数',
  `threat_level` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '威胁等级',
  `last_update` timestamp NULL DEFAULT NULL COMMENT '最后更新时间',
  `details` json DEFAULT NULL COMMENT '详细信息(JSON格式)',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`,`source`),
  KEY `idx_source` (`source`),
  KEY `idx_reputation` (`reputation_score`),
  KEY `idx_threat_level` (`threat_level`),
  KEY `idx_last_update` (`last_update`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件威胁情报表';

-- ----------------------------
-- Table structure for ip_request_frequency
-- ----------------------------
DROP TABLE IF EXISTS `ip_request_frequency`;
CREATE TABLE `ip_request_frequency` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ip` varchar(45) NOT NULL,
  `request_count` int NOT NULL,
  `from_time` datetime NOT NULL,
  `to_time` datetime NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2821 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for ip_threat_intel
-- ----------------------------
DROP TABLE IF EXISTS `ip_threat_intel`;
CREATE TABLE `ip_threat_intel` (
  `id` varchar(100) NOT NULL COMMENT '查询目标ID，如IP/URL/Hash',
  `type` varchar(20) NOT NULL DEFAULT 'default' COMMENT '类型，如IP/URL/File',
  `source` varchar(50) NOT NULL DEFAULT 'default' COMMENT '数据来源平台',
  `reputation_score` int NOT NULL DEFAULT '0' COMMENT '综合风险评分',
  `threat_level` varchar(20) DEFAULT NULL COMMENT '风险等级，如malicious/suspicious/harmless',
  `last_update` datetime DEFAULT NULL COMMENT '数据最后更新时间',
  `details` json DEFAULT NULL COMMENT '原始详细数据(JSON格式)',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
  PRIMARY KEY (`id`,`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='威胁IP情报表';

-- ----------------------------
-- Table structure for news_data
-- ----------------------------
DROP TABLE IF EXISTS `news_data`;
CREATE TABLE `news_data` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '新闻标题',
  `summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '新闻摘要',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '新闻内容',
  `source` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '新闻来源，例如 it之家、csdn',
  `category` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '新闻分类',
  `author` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '作者',
  `url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '原始链接，用于跳转',
  `mobile_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '移动端链接',
  `cover` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '封面图片',
  `hot` int DEFAULT '0' COMMENT '热度值',
  `timestamp` bigint DEFAULT '0' COMMENT '新闻时间戳',
  `published_at` datetime DEFAULT NULL COMMENT '发布时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_source` (`source`),
  KEY `idx_category` (`category`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_published_at` (`published_at`),
  KEY `idx_hot` (`hot`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='新闻数据表';

-- ----------------------------
-- Table structure for protected_ip
-- ----------------------------
DROP TABLE IF EXISTS `protected_ip`;
CREATE TABLE `protected_ip` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '被保护或处理的IP地址',
  `action` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '执行的操作类型 (e.g., blacklisted, query_failed, processing_failed)',
  `reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '操作原因或错误信息',
  `reputation_score` float DEFAULT NULL COMMENT '查询到的威胁情报分数，如果查询失败可能为NULL',
  `action_time` datetime NOT NULL COMMENT '执行此操作的时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=468 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='WAF IP保护操作记录表';

-- ----------------------------
-- Table structure for search_history
-- ----------------------------
DROP TABLE IF EXISTS `search_history`;
CREATE TABLE `search_history` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `query` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '查询关键字',
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '查询类型，如ip/url/file',
  `timestamp` datetime NOT NULL COMMENT '查询时间',
  `results` int DEFAULT '0' COMMENT '结果数量',
  `max_score` int DEFAULT '0' COMMENT '最大风险评分',
  `max_threat_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '最大威胁等级',
  `detail_results` json DEFAULT NULL COMMENT '查询结果详情，去掉大字段详情，方便快速读取',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_query` (`query`),
  KEY `idx_type` (`type`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_max_threat_level` (`max_threat_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作查询历史表';

-- ----------------------------
-- Table structure for url_threat_intel
-- ----------------------------
DROP TABLE IF EXISTS `url_threat_intel`;
CREATE TABLE `url_threat_intel` (
  `id` varchar(255) NOT NULL COMMENT '平台唯一ID，如 VirusTotal 的 hash ID',
  `type` varchar(50) NOT NULL DEFAULT 'url' COMMENT '类型，固定为 url',
  `source` varchar(50) NOT NULL DEFAULT '' COMMENT '数据来源，如 virustotal',
  `target_url` text COMMENT '原始URL地址',
  `reputation_score` int DEFAULT '0' COMMENT '信誉值（如有）',
  `last_update` datetime DEFAULT NULL COMMENT '平台返回的最后更新时间',
  `details` json DEFAULT NULL COMMENT '原始平台返回完整数据',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`,`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
