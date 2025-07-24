#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, pymysql, datetime, logging, requests
from flask import Blueprint, request, jsonify
from data.db_init import get_db_connection
from dotenv import load_dotenv

load_dotenv()

# 获取日志器
logger = logging.getLogger(__name__)

WAF_API_BASE_URL = 'http://localhost:8891/api'
def protected_ip_task():
    """
    查询高频请求的IP和被封禁IP，查询相对时间1分钟内，时间参考数据表中的 to_time 字段。
    如果有IP，则调用接口localhost:8891/api/query(post),查询IP的威胁情报。查询对应的reputation_score字段，如果值小于-5，则调用添加黑名单接口拉黑（接口localhost:8891/api/modifyblackrule）
    对应的操作记录记录到数据库中。表名：protected_ip
    这是一个独立的定时任务函数，不作为Flask路由。
    所有时间均为天真 datetime 对象。
    """
    try:
        now = datetime.datetime.now() # 使用天真 datetime 对象
        time_threshold = now - datetime.timedelta(minutes=1)

        conn = get_db_connection()
        ip_to_process = set()

        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 修改为基于 to_time 字段进行查询
            sql_freq = """
            SELECT ip FROM ip_request_frequency
            WHERE to_time >= %s
            """
            cursor.execute(sql_freq, (time_threshold,))
            for row in cursor.fetchall():
                ip_to_process.add(row['ip'])

            # 修改为基于 to_time 字段进行查询
            sql_blocked = """
            SELECT block_ip AS ip FROM blocked_ips
            WHERE to_time >= %s
            """
            cursor.execute(sql_blocked, (time_threshold,))
            for row in cursor.fetchall():
                ip_to_process.add(row['ip'])

        if not ip_to_process:
            logger.info("最近1分钟内没有新的高频请求或封禁IP需要处理。")
            if 'conn' in locals() and conn.open: # 确保 conn 存在且开放
                conn.close()
            return

        blacklisted_ips_count = 0
        for ip in ip_to_process:
            logger.info(f"正在处理IP: {ip}")
            reputation_score = None
            try:
                query_url = f"{WAF_API_BASE_URL}/query"
                # --- 修正点 1: /api/query 接口的请求参数 ---
                query_payload = {'value': ip, 'type': 'ip'}
                logger.info(f"调用威胁情报查询接口: {query_url} with payload: {query_payload}")
                response = requests.post(query_url, json=query_payload, timeout=5)
                response.raise_for_status()

                threat_data = response.json()
                # 威胁情报接口返回的 reputation_score 在 results 内部，且可能有多个源
                # 我们需要遍历 results 获取所有源的 reputation_score 并进行判断
                # 假设我们取所有 reputation_score 中最低（最差）的一个进行判断
                min_reputation_score = float('inf') # 初始化为正无穷
                if threat_data and 'results' in threat_data:
                    for source, data in threat_data['results'].items():
                        score = data.get('reputation_score')
                        if score is not None:
                            min_reputation_score = min(min_reputation_score, score)
                    reputation_score = min_reputation_score if min_reputation_score != float('inf') else None

                logger.info(f"IP {ip} 的威胁情报最低 reputation_score: {reputation_score}")

                if reputation_score is not None and reputation_score < -5:
                    logger.info(f"IP {ip} 威胁分数 {reputation_score} 低于 -5，准备加入黑名单。")
                    blacklist_url = f"{WAF_API_BASE_URL}/modifyblackrule"
                    # --- 修正点 2: /api/modifyblackrule 接口的请求参数 ---
                    blacklist_payload = {
                        'black_ip': ip
                        # 文档中没有 action 和 reason 字段，因此移除
                    }
                    logger.info(f"调用黑名单接口: {blacklist_url} with payload: {blacklist_payload}")
                    blacklist_response = requests.post(blacklist_url, json=blacklist_payload, timeout=5)
                    blacklist_response.raise_for_status()

                    # 文档中 modifyblackrule 示例响应为空，所以不尝试解析 json
                    # blacklist_result = blacklist_response.json()
                    logger.info(f"IP {ip} 已成功加入黑名单。WAF响应状态码: {blacklist_response.status_code}")
                    blacklisted_ips_count += 1

                    with conn.cursor() as cursor:
                        insert_sql = """
                        INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        # 记录操作时间为当前天真 datetime 对象
                        cursor.execute(insert_sql, (
                            ip,
                            'blacklisted',
                            'Threat score below -5',
                            reputation_score,
                            now
                        ))
                        conn.commit()
                        logger.info(f"IP {ip} 的拉黑操作已记录到 protected_ip 表。")
                else:
                    logger.info(f"IP {ip} 威胁分数 {reputation_score} 未达到拉黑条件或无分数。")

            except requests.exceptions.Timeout:
                logger.error(f"调用WAF接口超时 IP: {ip}")
                with conn.cursor() as cursor:
                    insert_sql = """
                    INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        ip,
                        'query_failed',
                        'WAF API Timeout during query',
                        reputation_score,
                        now
                    ))
                    conn.commit()
            except requests.exceptions.RequestException as req_e:
                logger.error(f"调用WAF接口失败 IP: {ip}, 错误: {req_e}")
                with conn.cursor() as cursor:
                    insert_sql = """
                    INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        ip,
                        'query_failed',
                        f'WAF API Request Error: {req_e}',
                        reputation_score,
                        now
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"处理IP {ip} 时发生未知错误: {e}")
                with conn.cursor() as cursor:
                    insert_sql = """
                    INSERT INTO protected_ip (ip, action, reason, reputation_score, action_time)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        ip,
                        'processing_failed',
                        f'Unknown error: {e}',
                        reputation_score,
                        now
                    ))
                    conn.commit()
        
        if 'conn' in locals() and conn.open: # 确保 conn 存在且开放
            conn.close()
        logger.info(f"总计处理了 {len(ip_to_process)} 个IP，其中 {blacklisted_ips_count} 个IP被拉黑。")

    except pymysql.Error as db_e:
        logger.error(f"数据库操作失败: {db_e}")
        if 'conn' in locals() and conn.open:
            conn.close()
    except Exception as e:
        logger.error(f"protected_ip_task 发生未预料的错误: {e}")
        if 'conn' in locals() and conn.open:
            conn.close()