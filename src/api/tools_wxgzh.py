import requests,json,os,markdown,time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,os,logging
from data.db_init import get_db_connection
from flask import Blueprint, request, jsonify
from datetime import datetime
# 加载环境变量
load_dotenv()

# 创建蓝图
wxgzh_bp = Blueprint('wxgzh', __name__, url_prefix='/')

# 获取文章内容
def get_article_content():
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询所有 CVE 数据
        query = "SELECT * FROM cve_data ORDER BY published DESC LIMIT 30"
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        conn.close()
        return results
        # return jsonify(results)

    except Exception as err:
        logging.exception("数据库查询接口出错")
        return jsonify({"error": str(err)}), 500

def render_cve_list_to_html(cve_list: list, tech_news: dict = None) -> str:
    """
    将CVE信息和技术新闻渲染为微信公众号格式的HTML内容。
    完全符合微信公众号HTML规范，优化排版效果。
    :param cve_list: List[Dict]，每个字典包含CVE相关信息
    :param tech_news: Dict，包含技术新闻数据的字典
    :return: 微信公众号兼容的HTML字符串
    """

    def render_cve_item(item):
        """渲染单个CVE条目 - 微信公众号兼容版本"""
        cve_id = item.get('cve_id', '未知CVE')
        title = item.get('title', '暂无标题')
        description = item.get('description', '')
        severity = item.get('severity', '未知')
        source = item.get('source', '未知来源')
        published = item.get('published', '未知时间')
        url = item.get('url', '#')

        # 处理发布时间格式
        if published and published != '未知时间':
            try:
                from datetime import datetime
                if isinstance(published, str):
                    if 'GMT' in published:
                        pub_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                        formatted_date = pub_date.strftime('%Y-%m-%d')
                    else:
                        formatted_date = published
                else:
                    formatted_date = str(published)
            except:
                formatted_date = str(published)
        else:
            formatted_date = '未知时间'

        # 处理严重程度显示
        severity_text = severity.strip() if severity else '未知'
        if 'CVE' in severity_text and 'PoC' in severity_text:
            severity_display = '⚠️ 有PoC验证'
            severity_color = '#ff6b6b'
        elif 'CVE' in severity_text:
            severity_display = '🔍 已确认'  
            severity_color = '#ffa726'
        else:
            severity_display = severity_text
            severity_color = '#9e9e9e'

        # 构建描述段落 - 简化版本适配微信
        description_html = ""
        if description and description.strip():
            short_desc = description[:80] + '...' if len(description) > 80 else description
            # 移除可能不兼容的特殊字符
            short_desc = short_desc.replace('<', '&lt;').replace('>', '&gt;')
            description_html = f'<p style="color: #666666; font-size: 13px; line-height: 1.6; margin: 8px 0 0 0;">{short_desc}</p>'

        # 简化CVE项目HTML结构
        item_html = f'''
<section style="margin: 0 0 15px 0; padding: 15px; background-color: #ffffff; border: 1px solid #e8e8e8; border-radius: 8px;">
    <section style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="background-color: #4a90e2; color: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">🛡️ {cve_id}</span>
        <span style="color: #999999; font-size: 11px;">{formatted_date}</span>
    </section>
    
    <h3 style="margin: 0 0 8px 0; color: #333333; font-size: 15px; font-weight: bold; line-height: 1.4;">{title}</h3>
    
    {description_html}
    
    <section style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
        <section>
            <span style="background-color: {severity_color}; color: #ffffff; padding: 2px 8px; border-radius: 10px; font-size: 10px; margin-right: 8px;">{severity_display}</span>
            <span style="color: #999999; font-size: 10px;">来源: {source}</span>
        </section>
    </section>
    
    <section style="margin-top: 10px; padding: 8px 12px; background-color: #f5f5f5; border-radius: 6px; border-left: 3px solid #4a90e2;">
        <p style="margin: 0; font-size: 10px; color: #666666; line-height: 1.4;">🔗 详情链接: <span style="color: #4a90e2; word-break: break-all;">{url}</span></p>
        <p style="margin: 5px 0 0 0; font-size: 9px; color: #999999;">💡 复制链接到浏览器访问查看完整内容</p>
    </section>
</section>'''
        return item_html

    def render_news_item(item):
        """渲染单个新闻条目 - 微信公众号兼容版本"""
        channel = item.get('channel', '未知来源')
        title = item.get('title', '暂无标题')
        description = item.get('description', '')
        author = item.get('author', '未知作者')
        url = item.get('url', '#')
        hot = item.get('hot', 0)
        category = item.get('category', '未知分类')
        language = item.get('language', '')
        stars = item.get('stars', '')

        # 描述部分
        description_html = ""
        if description and description.strip():
            short_desc = description[:100] + '...' if len(description) > 100 else description
            short_desc = short_desc.replace('<', '&lt;').replace('>', '&gt;')
            description_html = f'<p style="color: #666666; font-size: 13px; line-height: 1.6; margin: 8px 0 0 0;">{short_desc}</p>'

        # 热度显示
        if hot >= 1000000:
            hot_display = f"{hot // 1000000}M"
        elif hot >= 1000:
            hot_display = f"{hot // 1000}K"
        else:
            hot_display = str(hot)

        # 根据渠道设置样式
        if channel == 'GitHub':
            channel_icon = '🐱'
            channel_color = '#333333'
            extra_info = f"⭐ {stars}" if stars else ""
            language_info = f"📝 {language}" if language else ""
        else:
            channel_icon = '📚'
            channel_color = '#fd7e14'
            extra_info = f"🔥 {hot_display}"
            language_info = ""

        # 简化新闻项目HTML结构
        item_html = f'''
<section style="margin: 0 0 15px 0; padding: 15px; background-color: #ffffff; border: 1px solid #e8e8e8; border-radius: 8px;">
    <section style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="background-color: {channel_color}; color: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">{channel_icon} {channel}</span>
        <span style="color: #999999; font-size: 11px;">{category}</span>
    </section>
    
    <h3 style="margin: 0 0 8px 0; color: #333333; font-size: 15px; font-weight: bold; line-height: 1.4;">{title}</h3>
    
    {description_html}
    
    <section style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
        <section>
            <span style="background-color: #28a745; color: #ffffff; padding: 2px 8px; border-radius: 10px; font-size: 10px; margin-right: 8px;">{extra_info}</span>
            <span style="color: #999999; font-size: 10px;">作者: {author}</span>
            {f'<span style="color: #666666; font-size: 10px; margin-left: 8px;">{language_info}</span>' if language_info else ''}
        </section>
    </section>
    
    <section style="margin-top: 10px; padding: 8px 12px; background-color: #f5f5f5; border-radius: 6px; border-left: 3px solid #28a745;">
        <p style="margin: 0; font-size: 10px; color: #666666; line-height: 1.4;">🔗 详情链接: <span style="color: #28a745; word-break: break-all;">{url}</span></p>
        <p style="margin: 5px 0 0 0; font-size: 9px; color: #999999;">💡 复制链接到浏览器访问查看完整内容</p>
    </section>
</section>'''
        return item_html

    # 开始构建完整HTML
    html_parts = []

    # 头部关注提示 - 微信标准格式
    html_parts.append('''
<section style="font-family: -apple-system-font, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif;">
    <section style="background-color: #e3f2fd; padding: 12px 16px; border-radius: 8px; margin-bottom: 15px; text-align: center;">
        <p style="margin: 0; color: #1565c0; font-size: 14px; font-weight: bold;">点击上方蓝字关注我们</p>
    </section>
    
    <section style="border: 1px solid #dddddd; border-radius: 8px; padding: 15px; margin-bottom: 20px; background-color: #f9f9f9;">
        <p style="margin: 0; text-indent: 2em; color: #333333; font-size: 14px; line-height: 1.6;">重要声明‼️‼️随着网络安全越来越重要，"安全info"将定期分享实用安全技术、最新行业动态、案例分析，实战技巧等。鉴于网络安全法的基础文章内容仅供学习，不做其他任何用处！</p>
    </section>
</section>''')

    # 主标题
    html_parts.append('''
<section style="background-color: #4a90e2; color: #ffffff; padding: 16px 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
    <h2 style="margin: 0; font-size: 18px; font-weight: bold;">🔐 最新 CVE 安全公告与技术资讯</h2>
</section>''')

    # 统计信息 - 基于限制后的数量
    cve_count = min(len(cve_list), 10) if cve_list else 0
    news_count = min(tech_news.get('total', 0), 10) if tech_news else 0
    html_parts.append(f'''
<section style="background-color: #fff3cd; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; border: 1px solid #ffeaa7;">
    <p style="margin: 0; color: #856404; font-weight: bold; font-size: 14px;">📊 本期精选 {cve_count} 个CVE漏洞 | {news_count} 条技术资讯 | 最新情报资讯</p>
</section>''')

    # CVE安全漏洞部分 - 限制显示最新10条
    if cve_list:
        # 只取前10条最新数据
        limited_cve_list = cve_list[:10]
        
        html_parts.append('''
<section style="margin-top: 20px;">
    <section style="background-color: #4a90e2; color: #ffffff; padding: 12px 18px; border-radius: 6px; margin: 20px 0 15px 0; text-align: center;">
        <h3 style="margin: 0; font-size: 16px; font-weight: bold;">🛡️ CVE 安全漏洞公告</h3>
    </section>
    
    <section style="border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; background-color: #f8f9fa;">''')
        
        for item in limited_cve_list:
            html_parts.append(render_cve_item(item))
            
        html_parts.append(f'''
    </section>
    
    <section style="text-align: center; margin-top: 10px; padding: 8px; background-color: #e9ecef; border-radius: 6px;">
        <p style="margin: 0; color: #6c757d; font-size: 12px;">💡 显示最新 {len(limited_cve_list)} 条CVE漏洞信息</p>
    </section>
</section>''')

    # 技术资讯部分 - 限制显示最新10条
    if tech_news and tech_news.get('data'):
        # 只取前10条最新数据
        limited_news_data = tech_news['data'][:10]
        
        html_parts.append('''
<section style="margin-top: 25px;">
    <section style="background-color: #28a745; color: #ffffff; padding: 12px 18px; border-radius: 6px; margin: 20px 0 15px 0; text-align: center;">
        <h3 style="margin: 0; font-size: 16px; font-weight: bold;">📰 技术资讯热点</h3>
    </section>
    
    <section style="border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; background-color: #f8f9fa;">''')
        
        for item in limited_news_data:
            html_parts.append(render_news_item(item))
            
        update_time = tech_news.get('update_time', '')
        html_parts.append(f'''
    </section>
    
    <section style="text-align: center; margin-top: 10px; padding: 8px; background-color: #e9ecef; border-radius: 6px;">
        <p style="margin: 0; color: #6c757d; font-size: 12px;">💡 显示最新 {len(limited_news_data)} 条技术资讯 | 数据更新时间：{update_time}</p>
    </section>
</section>''')
    # ✅ 新增说明区域（放在最后蓝色关注卡片前）
    html_parts.append('''
    <section style="border: 1px dashed #4a90e2; padding: 14px 18px; border-radius: 8px; background-color: #f0f8ff; margin-top: 30px; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 14px; color: #1565c0; line-height: 1.7;">
        📢 微信公众号每天统计最新资讯或其他内容自动发送（免人工全自动），可联系作者✍️。<br/>
        🚀 最新项目 <strong>【威胁情报聚合处理平台】</strong> 👉 
        <a href="https://github.com/HaoY-l/threat-intel-hub" style="color: #007acc; word-break: break-all;" target="_blank">
        https://github.com/HaoY-l/threat-intel-hub
        </a>
    </p>
    </section>''')

    # 底部关注区域
    html_parts.append('''
<section style="background-color: #4a90e2; padding: 20px 25px; border-radius: 16px; margin-top: 30px; text-align: center; color: #ffffff;">
    <section style="max-width: 600px; margin: 0 auto;">
        <p style="margin: 0 0 15px 0; font-size: 18px; font-weight: bold; line-height: 1.6;">🎉 关注网络安全，保护数字世界！👆</p>
        <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.6; opacity: 0.9;">✌️ 获取更多CVE漏洞情报和网络安全资讯，让我们一起构建更安全的网络环境！✌️</p>
        
        <section style="background-color: rgba(255,255,255,0.2); padding: 12px 16px; border-radius: 20px; display: inline-block; margin-top: 10px;">
            <p style="margin: 0; font-weight: bold; font-size: 14px; line-height: 1.5;">📬 联系作者：微信：tomorrow_me- | 知识星球：数据安全info | QQ/微信安全交流群</p>
        </section>
    </section>
</section>''')

    html_parts.append('</section>')
    
    return '\n'.join(html_parts)

def get_tech_news():
    """
    获取技术新闻汇总 (CSDN + GitHub)
    
    Returns:
        dict: 包含新闻数据的字典
    """
    combined_news = []
    
    # 获取CSDN热榜数据
    try:
        url = "https://blog.csdn.net/phoenix/web/blog/hot-rank?page=0&pageSize=30"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        data_list = result.get("data", [])
        
        for item in data_list:
            pic_list = item.get("picList", [])
            cover = pic_list[0] if pic_list else None
            
            combined_news.append({
                "channel": "CSDN",
                "channel_type": "技术社区",
                "title": item.get("articleTitle", ""),
                "description": None,
                "author": item.get("nickName", ""),
                "cover": cover,
                "url": item.get("articleDetailUrl", ""),
                "hot": int(item.get("hotRankScore", 0)),
                "timestamp": int(time.time()),
                "category": "排行榜"
            })
        
        logging.info(f"✅ CSDN数据获取成功: {len(data_list)} 条")
    except Exception as e:
        logging.error(f"❌ CSDN数据获取失败: {str(e)}")
    
    # 获取GitHub趋势数据
    try:
        url = "https://github.com/trending?since=daily"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        html = response.text
        
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article.Box-row")
        
        github_count = 0
        max_github_items = 6
        for article in articles:
            if github_count >= max_github_items:  # 达到限制数量就跳出循环
                break
            a_tag = article.find("h2").find("a")
            full_name = a_tag.get_text(strip=True).replace("\n", "").replace(" ", "")
            
            # 处理 "owner / repo" 格式
            parts = [p.strip() for p in full_name.split("/") if p.strip()]
            owner = parts[0] if len(parts) > 0 else ""
            repo = parts[1] if len(parts) > 1 else ""
            
            repo_url = "https://github.com" + a_tag["href"]
            
            description_tag = article.select_one("p.col-9.color-fg-muted")
            description = description_tag.get_text(strip=True) if description_tag else ""
            
            language_tag = article.select_one('[itemprop="programmingLanguage"]')
            language = language_tag.get_text(strip=True) if language_tag else ""
            
            stars_tag = article.select_one('a[href$="/stargazers"]')
            stars = stars_tag.get_text(strip=True) if stars_tag else "0"
            
            # 转换stars为数字
            hot_score = 0
            if stars:
                stars_str = stars.replace(",", "").lower()
                if 'k' in stars_str:
                    hot_score = int(float(stars_str.replace('k', '')) * 1000)
                elif 'm' in stars_str:
                    hot_score = int(float(stars_str.replace('m', '')) * 1000000)
                else:
                    try:
                        hot_score = int(stars_str)
                    except:
                        hot_score = 0
            
            combined_news.append({
                "channel": "GitHub",
                "channel_type": "开源社区",
                "title": f"{owner}/{repo}",
                "description": description,
                "author": owner,
                "cover": None,
                "url": repo_url,
                "hot": hot_score,
                "timestamp": int(time.time()),
                "category": "趋势",
                "language": language,
                "stars": stars
            })
            github_count += 1
        
        logging.info(f"✅ GitHub数据获取成功: {github_count} 条")
    except Exception as e:
        logging.error(f"❌ GitHub数据获取失败: {str(e)}")
    
    # 按热度排序
    combined_news.sort(key=lambda x: x['hot'], reverse=True)
    
    return {
        "total": len(combined_news),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": combined_news
    }

# 获取access_token
def get_access_token(appid, appsecret):
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": appsecret
    }
    try:
        response = requests.get(url, params=params)
        return response.json()["access_token"]
    except Exception as e:
        print(e)
        return None

# 获取素材id
def get_media_id():
# def get_media_id(access_token):
    # picture_dir = os.path.join(script_dir, 'data')
    # picture_file = os.path.join(picture_dir, f"{''.join(filter(str.isalnum, config()['web_content_url']))}.png")
    # url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
    # with open(picture_file, 'rb') as file:
    #     files = {
    #         'media': (os.path.basename(picture_file), file, "image/png")
    #     }
    #     response = requests.post(url, files=files)
    # return response.json()["media_id"]
    return 'eJTZQlw2NrdSR7sDOLY2Ax02TF5rmG4hhEoB65pAzjztsnwMRCKTp5Ag6L4tKsJw'
    # 素材链接：https://mmbiz.qpic.cn/mmbiz_png/Z8yWOunaWFw0C2TvI0vaXx3jBZLqraNhe23iciasEib61Xibzq4ibnk0Gkcr9X9TVEjtJBRicAGfn5wQ4BUEscWu8sTA/0?wx_fmt=png&from=appmsg


# 微信公众号上传草稿文章
def create_article():
    APPID = os.getenv("wx_appid")
    APPSECRET = os.getenv("wx_secret")
    access_token = get_access_token(APPID, APPSECRET)

    THUMB_MEDIA_ID = get_media_id()

    # 获取CVE数据
    cve_data = get_article_content()
    
    # 获取技术新闻数据
    tech_news = get_tech_news()

    # 获取当前日期并格式化标题和摘要
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")  # 格式：2025-07-16
    
    TITLE = f"{date_str} 最新CVE漏洞情报和技术资讯头条"
    DIGEST = f"{date_str} 最新CVE漏洞情报和技术资讯头条"

    # 同时传入CVE数据和技术新闻数据
    content_html = render_cve_list_to_html(cve_data, tech_news)

    url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'
    data = {
        "articles": [
            {
                "article_type":"news",
                "title":TITLE,
                "author":'We12',
                "digest":DIGEST,
                "content":content_html,
                "content_source_url":'https://github.com/HaoY-l/threat-intel-hub',
                "thumb_media_id":THUMB_MEDIA_ID,
                "need_open_comment":'1',
                "only_fans_can_comment":0,
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data, ensure_ascii=False), headers=headers)
    print(response)
    if response.json()["media_id"]:
        logging.info("草稿发布成功")
    else:
        logging.error("草稿发布失败:{response.json()}")


# 微信发布正式内容（草稿）接口如下，有free publish、batchget、get_status等功能
# 微信 Free Publish - 获取草稿箱列表
def get_wechat_draft_list(access_token, offset=0, count=20):
    """
    获取草稿箱列表 (微信官方draft_batchget接口)
    """
    try:
        # # 兼容 application/json 和 x-www-form-urlencoded
        # # if request.is_json:
        # #     data = request.get_json()
        # # else:
        # #     data = request.form.to_dict() if request.form else {}

        # offset = int(data.get('offset', 0))
        # count = int(data.get('count', 20))

        if not access_token:
            return jsonify({'error': '获取access_token失败'}), 500

        url = f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}'
        payload = {
            "offset": offset,
            "count": count,
            "no_content": 1  # 不返回正文内容，节省流量
        }
        
        # 关键修改：确保请求时正确处理编码
        resp = requests.post(url, json=payload, timeout=10)
        
        if resp.status_code != 200:
            return jsonify({'error': '微信草稿列表请求失败'}), 500

        # 关键修改：确保响应内容正确解码
        resp.encoding = 'utf-8'  # 确保响应按UTF-8解码
        wx_data = resp.json()
        
        if wx_data.get('errcode', 0) != 0:
            return jsonify({'error': f"微信返回错误: {wx_data.get('errmsg', '未知错误')}"})

        # 处理Unicode转义字符，确保中文正确显示
        for item in wx_data.get('item', []):
            try:
                if 'content' in item and 'news_item' in item['content']:
                    for news_item in item['content']['news_item']:
                        # 解码title中的Unicode转义字符
                        if 'title' in news_item:
                            # 方法1：使用encode/decode来处理Unicode转义
                            title = news_item['title']
                            if isinstance(title, str):
                                # 先编码为bytes，然后用unicode_escape解码，再用utf-8编码回字符串
                                try:
                                    news_item['title'] = title.encode().decode('unicode_escape').encode('latin1').decode('utf-8')
                                except (UnicodeDecodeError, UnicodeEncodeError):
                                    # 如果上述方法失败，尝试直接处理
                                    news_item['title'] = title
                        
                        # 同样处理digest
                        if 'digest' in news_item:
                            digest = news_item['digest']
                            if isinstance(digest, str):
                                try:
                                    news_item['digest'] = digest.encode().decode('unicode_escape').encode('latin1').decode('utf-8')
                                except (UnicodeDecodeError, UnicodeEncodeError):
                                    news_item['digest'] = digest
                        
                        # 处理author
                        if 'author' in news_item:
                            author = news_item['author']
                            if isinstance(author, str):
                                try:
                                    news_item['author'] = author.encode().decode('unicode_escape').encode('latin1').decode('utf-8')
                                except (UnicodeDecodeError, UnicodeEncodeError):
                                    news_item['author'] = author
                                    
            except Exception as e:
                print(f"Unicode解码异常: {e}")
                continue

        # 直接返回处理后的数据
        # return jsonify(wx_data)
        return wx_data

    except Exception as e:
        import traceback
        print("获取草稿列表异常:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# 微信 Free Publish - 发布草稿
def wechat_submit(access_token):
    """发布草稿"""
    try:
        if not access_token:
            return jsonify({'error': '获取access_token失败'}), 500

        # 获取草稿列表
        wx_data = get_wechat_draft_list(access_token)
        if not isinstance(wx_data, dict):
            return jsonify({'error': '草稿获取失败或格式错误'}), 500

        items = wx_data.get("item", [])
        if not items:
            return jsonify({'error': '草稿列表为空，无法发布'}), 400

        media_id = items[0].get("media_id")
        if not media_id:
            return jsonify({'error': '缺少 media_id'}), 400

        # 请求发布
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
        payload = {
            "media_id": media_id
        }
        logging.info(f"草稿id为{media_id}")
        resp = requests.post(url, json=payload, timeout=30)
        return jsonify(resp.json())

    except Exception as e:
        import traceback
        print("微信 submit 异常:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@wxgzh_bp.route('/wxgzh', methods=['POST'])
def draft_article():
    APPID = os.getenv("wx_appid")
    APPSECRET = os.getenv("wx_secret")
    access_token = get_access_token(APPID, APPSECRET)
    if not access_token:
        return jsonify({'error': '获取 access_token 失败'}), 500
    # 创建上传草稿
    create_article()

    # 捕获返回值
    result_response = wechat_submit(access_token)

    # 直接返回这个响应
    return result_response
