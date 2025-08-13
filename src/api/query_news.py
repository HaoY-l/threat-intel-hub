# ============ News API (news.py) - 修改后 ============
from flask import Blueprint, request, jsonify
from data.db_init import get_db_connection
from datetime import datetime, timedelta
import logging
import requests
from bs4 import BeautifulSoup
import re
import json
import time

news_bp = Blueprint('news', __name__)

def format_timestamp(timestamp):
    """将时间戳转换为相对时间"""
    if not timestamp:
        return "未知时间"

    try:
        news_time = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        diff = now - news_time

        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
    except:
        return "未知时间"

def clear_news_data():
    """清理新闻数据表"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE news_data")
        conn.close()
        logging.info("News data table cleared successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to clear news data table: {str(e)}")
        return False

def insert_news_data(news_items):
    """批量插入新闻数据"""
    if not news_items:
        return False

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            insert_sql = """
            INSERT INTO news_data (
                title, summary, content, source, category, author,
                url, mobile_url, cover, hot, timestamp, published_at
            ) VALUES (
                %(title)s, %(summary)s, %(content)s, %(source)s, %(category)s, %(author)s,
                %(url)s, %(mobile_url)s, %(cover)s, %(hot)s, %(timestamp)s, %(published_at)s
            )
            """

            for item in news_items:
                published_at = None
                if item.get('timestamp'):
                    try:
                        published_at = datetime.fromtimestamp(item['timestamp'])
                    except:
                        published_at = None

                news_data = {
                    'title': item.get('title', ''),
                    'summary': item.get('desc', ''),
                    'content': item.get('content', ''),
                    'source': item.get('source', ''),
                    'category': item.get('category', ''),
                    'author': item.get('author', ''),
                    'url': item.get('url', ''),
                    'mobile_url': item.get('mobile_url', ''),
                    'cover': item.get('cover', ''),
                    'hot': item.get('hot', 0),
                    'timestamp': item.get('timestamp', 0),
                    'published_at': published_at,
                }

                cursor.execute(insert_sql, news_data)

        conn.close()
        logging.info(f"Successfully inserted {len(news_items)} news items")
        return True
    except Exception as e:
        logging.error(f"Failed to insert news data: {str(e)}")
        return False

def get_time(time_str):
    """将相对时间字符串转换为时间戳"""
    try:
        if "分钟前" in time_str:
            minutes = int(re.search(r"(\d+)", time_str).group(1))
            return int((datetime.now() - timedelta(minutes=minutes)).timestamp())
        elif "小时前" in time_str:
            hours = int(re.search(r"(\d+)", time_str).group(1))
            return int((datetime.now() - timedelta(hours=hours)).timestamp())
        elif "天前" in time_str:
            days = int(re.search(r"(\d+)", time_str).group(1))
            return int((datetime.now() - timedelta(days=days)).timestamp())
        elif "刚刚" in time_str:
            return int(datetime.now().timestamp())
        else:
            return int(datetime.strptime(time_str, "%Y-%m-%d %H:%M").timestamp())
    except Exception as e:
        logging.warning(f"Failed to parse time string: {time_str}, error: {e}")
        return int(time.time())

def fetch_csdn_news():
    """抓取CSDN新闻"""
    url = "https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=15"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        logging.error(f"请求 CSDN API 失败: {e}")
        return []

    data_list = result.get("data", [])
    parsed_list = []
    for item in data_list:
        pic_list = item.get("picList", [])
        cover = pic_list[0] if pic_list else None
        parsed_list.append({
            "id": item.get("productId"),
            "title": item.get("articleTitle"),
            "cover": cover,
            "desc": None,
            "author": item.get("nickName"),
            "timestamp": get_time(item.get("period")),
            "hot": int(item.get("hotRankScore", 0)),
            "url": item.get("articleDetailUrl"),
            "mobile_url": item.get("articleDetailUrl"),
            "source": "CSDN",
            "category": "网络安全"
        })
    return parsed_list

def fetch_freebuf_news():
    """抓取Freebuf新闻"""
    api_urls = [
        "https://www.freebuf.com/api/articles/recommend",
        "https://www.freebuf.com/api/articles/latest",
        "https://www.freebuf.com/ajax/articles",
        "https://m.freebuf.com/api/articles",
        "https://www.freebuf.com/api/index"
    ]
    headers = {
        "Referer": "https://www.freebuf.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    data_list = []
    for url in api_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            data = result.get("data", {}).get("list", []) or result.get("data", [])
            if data:
                data_list = data
                break
        except Exception as e:
            logging.warning(f"请求 Freebuf API 失败: {url}, error: {e}")
            continue

    if not data_list:
        logging.error("未能从 Freebuf 任何 API 接口获取到数据。")
        return []
    
    parsed_list = []
    for item in data_list:
        try:
            article_id = item.get("id")
            title = item.get("title")
            desc = item.get("summary", "") or item.get("desc", "")
            url = item.get("url") or f"https://www.freebuf.com/articles/{article_id}"
            
            cover = item.get("cover")
            if cover and cover.startswith('//'):
                cover = 'https:' + cover
            elif cover and cover.startswith('/'):
                cover = "https://www.freebuf.com" + cover
            
            time_fields = ["create_time", "publish_time", "time", "created_at", "date"]
            timestamp = ""
            for field in time_fields:
                if field in item and item[field]:
                    timestamp = get_time(item[field])
                    break
            
            parsed_item = {
                "id": article_id,
                "title": title,
                "desc": desc,
                "cover": cover,
                "author": item.get("author", item.get("username", item.get("writer", "FreeBuf"))),
                "timestamp": timestamp,
                "hot": int(item.get("view_count", item.get("views", item.get("hot", item.get("read_count", 0))))),
                "url": url,
                "mobile_url": url.replace('www.freebuf.com', 'm.freebuf.com') if url else "",
                "source": "FreeBuf",
                "category": item.get("category", "网络安全")
            }
            parsed_list.append(parsed_item)
                
        except Exception as e:
            logging.warning(f"解析单篇文章失败: {e}")
            continue
    
    return parsed_list[:15]

@news_bp.route('/news', methods=['GET'])
def query_news():
    """
    统一格式的新闻查询接口 - 直接返回数组，与CVE接口格式一致
    """
    try:
        logging.info("接收到 GET /news 请求，开始执行数据抓取和同步。")
        
        # 1. 抓取数据
        all_news_data = []
        all_news_data.extend(fetch_csdn_news())
        all_news_data.extend(fetch_freebuf_news())
        
        # 2. 清理旧数据并插入新数据
        clear_news_data()
        success = insert_news_data(all_news_data)
        
        if not success:
            logging.error("插入新闻数据失败")
            return jsonify([]), 500
            
        logging.info(f"成功抓取并插入 {len(all_news_data)} 条新闻数据")

        # 3. 获取查询参数
        limit = request.args.get('limit', 30, type=int)
        source_filter = request.args.get('source', '')
        category_filter = request.args.get('category', '')
        keyword = request.args.get('keyword', '')

        # 4. 查询数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT id, title, summary, content, source, category, author, url, mobile_url, cover, hot, timestamp, published_at, created_at, updated_at FROM news_data"
        params = []
        conditions = []

        if source_filter:
            conditions.append("source = %s")
            params.append(source_filter)

        if category_filter:
            conditions.append("category = %s")
            params.append(category_filter)

        if keyword:
            conditions.append("title LIKE %s")
            params.append(f"%{keyword}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY published_at DESC, timestamp DESC, hot DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        # 5. 格式化数据并直接返回数组（与CVE格式一致）
        formatted_news = []
        for row in results:
            news_item = {
                "id": row['id'],
                "title": row['title'] or "无标题",
                "summary": row['summary'] or "暂无描述信息...",
                "content": row['content'],
                "source": row['source'] or "未知来源",
                "category": row['category'],
                "author": row['author'],
                "url": row['url'],
                "mobile_url": row['mobile_url'],
                "cover": row['cover'],
                "hot": row['hot'] or 0,
                "timestamp": row['timestamp'],
                "published_at": row['published_at'].isoformat() if row['published_at'] else None,
                "time": format_timestamp(row['timestamp']),
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
            }
            formatted_news.append(news_item)

        # 直接返回数组，与CVE接口格式保持一致
        return jsonify(formatted_news)

    except Exception as err:
        logging.exception("News 查询接口出错")
        return jsonify([]), 500

@news_bp.route('/news/sync', methods=['POST'])
def sync_news_data():
    """同步新闻数据接口 (已废弃)"""
    return jsonify({
        "success": False,
        "message": "此接口已废弃，请使用 GET /news 接口来获取最新数据。"
    }), 410

@news_bp.route('/news/stats', methods=['GET'])
def get_news_stats():
    """获取新闻统计信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM news_data")
        total = cursor.fetchone()['total']

        cursor.execute("SELECT source, COUNT(*) as count FROM news_data GROUP BY source")
        by_source = {row['source']: row['count'] for row in cursor.fetchall()}

        cursor.execute("SELECT category, COUNT(*) as count FROM news_data GROUP BY category")
        by_category = {row['category']: row['count'] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as recent FROM news_data WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)")
        recent_24h = cursor.fetchone()['recent']

        cursor.close()
        conn.close()

        # 统计信息可以保持对象格式，因为这是专门的统计接口
        return jsonify({
            "success": True,
            "stats": {
                "total": total,
                "recent_24h": recent_24h,
                "by_source": by_source,
                "by_category": by_category,
            }
        })

    except Exception as err:
        logging.exception("获取新闻统计信息出错")
        return jsonify({
            "success": False,
            "error": str(err)
        }), 500