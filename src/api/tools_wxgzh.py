import requests,json,os,markdown
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys,os,logging
from data.db_init import get_db_connection
from flask import Blueprint, request, jsonify
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

def render_cve_list_to_html(cve_list: list) -> str:
    """
    将CVE信息渲染为公众号风格的HTML内容。
    :param cve_list: List[Dict]，每个字典包含CVE相关信息
    :return: HTML字符串
    """
    
    def render_cve_item(item):
        """渲染单个CVE条目"""
        cve_id = item.get('cve_id', '未知CVE')
        title = item.get('title', '暂无标题')
        description = item.get('description', '暂无描述')
        severity = item.get('severity', '未知')
        source = item.get('source', '未知来源')
        published = item.get('published', '未知时间')
        url = item.get('url', '#')
        
        # 处理发布时间格式
        if published and published != '未知时间':
            try:
                from datetime import datetime
                if isinstance(published, str):
                    # 尝试解析时间字符串
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
        
        # 处理严重程度，提取有用信息
        severity_text = severity.strip() if severity else '未知'
        if 'CVE' in severity_text and 'PoC' in severity_text:
            severity_display = '⚠️ 有PoC验证'
        elif 'CVE' in severity_text:
            severity_display = '🔍 已确认'
        else:
            severity_display = severity_text
        
        # 截取描述内容，避免过长
        if description and description.strip():
            description_short = description[:100] + '...' if len(description) > 100 else description
        else:
            description_short = '暂无描述'
        
        # 构建CVE条目HTML - 统一的滑动展示样式
        item_html = f'''
            <div style="margin-bottom:15px;padding:15px 18px;background:#ffffff;
                border:1px solid #e0e0e0;border-radius:8px;
                box-shadow:0 2px 6px rgba(0,0,0,0.08);
                transition:all 0.3s ease;position:relative;">
                
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                    <span style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:white;
                        padding:4px 10px;border-radius:15px;font-size:12px;font-weight:bold;">
                        🛡️ {cve_id}
                    </span>
                    <span style="color:#999;font-size:11px;">{formatted_date}</span>
                </div>
                
                <h4 style="margin:0 0 10px 0;color:#2c3e50;font-size:14px;font-weight:bold;line-height:1.4;">
                    {title}
                </h4>
                
                <p style="color:#666;font-size:12px;line-height:1.5;margin:8px 0;">
                    {description_short}
                </p>
                
                <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="background:{get_severity_color(severity_display)};color:white;
                            padding:2px 8px;border-radius:10px;font-size:10px;">
                            {severity_display}
                        </span>
                        <span style="color:#999;font-size:10px;">来源: {source}</span>
                    </div>
                    
                    <div style="color:#667eea;font-size:11px;padding:3px 8px;
                        border:1px solid #667eea;border-radius:4px;cursor:pointer;
                        text-decoration:none;">
                        📖 详情链接
                    </div>
                </div>
                
                <!-- 链接信息展示区域 -->
                <div style="margin-top:10px;padding:8px 12px;background:#f8f9fa;
                    border-radius:6px;border-left:3px solid #667eea;">
                    <p style="margin:0;font-size:10px;color:#666;line-height:1.4;">
                        🔗 详情链接: <span style="color:#667eea;word-break:break-all;">{url}</span>
                    </p>
                    <p style="margin:5px 0 0 0;font-size:9px;color:#999;">
                        💡 复制链接到浏览器访问查看完整内容
                    </p>
                </div>
            </div>
        '''
        
        return item_html

    def get_severity_color(severity):
        """根据严重程度返回对应颜色"""
        if '⚠️' in severity or 'PoC' in severity:
            return '#dc3545'  # 红色
        elif '🔍' in severity or '已确认' in severity:
            return '#fd7e14'  # 橙色
        else:
            return '#6c757d'  # 灰色

    # 开始构建HTML
    html_parts = []
    
    # 添加头部固定内容
    html_parts.append('''
        <div style="max-width:100%;margin:0 auto;font-family:'PingFang SC','Microsoft YaHei',Arial,sans-serif;">
            <p style="background:linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);padding:10px 15px;
                border-radius:8px;margin-bottom:10px;color:#1565c0;font-weight:bold;text-align:left;">
                点击上方蓝字关注我们
            </p>
            
            <p style="border:1px solid #ddd;border-radius:8px;padding:12px 15px;margin-bottom:20px;
                text-indent:2em;background:#f9f9f9;">
                重要声明‼️‼️随着网络安全越来越重要，"安全info"将定期分享实用安全技术、最新行业动态、案例分析，实战技巧等。鉴于网络安全法的基础文章内容仅供学习，不做其他任何用处！
            </p>
    ''')
    
    # 添加主标题
    html_parts.append('''
        <h2 style="font-weight:bold;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color:white;padding:15px 20px;border-radius:8px;margin:25px 0 20px 0;font-size:18px;
            text-align:center;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
            🔐 最新 CVE 安全公告
        </h2>
    ''')
    
    # 添加统计信息
    total_count = len(cve_list)
    html_parts.append(f'''
        <div style="background:linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            padding:12px 20px;border-radius:8px;margin-bottom:20px;text-align:center;">
            <span style="color:#2d3436;font-weight:bold;font-size:14px;">
                📊 本期共收录 {total_count} 个CVE漏洞 | 滑动查看更多
            </span>
        </div>
    ''')
    
    # 滑动窗口展示所有CVE信息
    html_parts.append('''
        <div style="margin-top:20px;">
            
            <div style="max-height:600px;overflow-y:auto;border:1px solid #dee2e6;
                padding:15px;border-radius:8px;background:#f8f9fa;
                box-shadow:inset 0 2px 4px rgba(0,0,0,0.1);">
    ''')
    
    # 渲染所有CVE信息
    for item in cve_list:
        html_parts.append(render_cve_item(item))
    
    html_parts.append('''
            </div>
            
            <div style="text-align:center;margin-top:15px;padding:12px;
                background:#e9ecef;border-radius:8px;color:#6c757d;font-size:12px;">
                💡 提示：上方区域可滑动查看更多CVE信息 | 复制链接到浏览器访问详情
            </div>
        </div>
    ''')
    
    # 添加链接说明区域
    html_parts.append('''
        <div style="background:#fff3cd;border:1px solid #ffeaa7;border-radius:8px;
            padding:15px;margin-top:20px;text-align:center;">
            <p style="margin:0 0 10px 0;color:#856404;font-size:13px;font-weight:bold;">
                🔗 如何访问详情链接
            </p>
            <p style="margin:0;color:#856404;font-size:11px;line-height:1.5;">
                由于微信限制，无法直接点击跳转。请复制上方展示的链接地址，粘贴到浏览器中访问查看完整CVE详情。
            </p>
        </div>
    ''')
    
    # 添加尾部CTA区块
    html_parts.append('''
        <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding:20px 25px;border-radius:16px;margin-top:30px;text-align:center;
            color:white;font-size:16px;box-shadow:0 8px 25px rgba(102,126,234,0.3);">
            
            <div style="max-width:600px;margin:0 auto;">
                <p style="margin:0 0 15px 0;font-size:18px;font-weight:bold;line-height:1.6;">
                    🎉 关注网络安全，保护数字世界！👆
                </p>
                
                <p style="margin:0 0 20px 0;font-size:14px;opacity:0.9;line-height:1.6;">
                    ✌️ 获取更多CVE漏洞情报和网络安全资讯，让我们一起构建更安全的网络环境！✌️
                </p>
                
                <div style="background:rgba(255,255,255,0.2);padding:12px 16px;border-radius:20px;
                    display:inline-block;font-weight:bold;font-size:14px;line-height:1.5;
                    margin-top:10px;">
                    📬 联系作者：微信：tomorrow_me- | 知识星球：数据安全info | QQ/微信安全交流群
                </div>
            </div>
        </div>
    ''')
    
    # 结束容器
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)


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

    # 构建图文文章
    json_data = get_article_content()

    TITLE = "测试标题"
    DIGEST = "测试摘要"

    content_html = render_cve_list_to_html(json_data)

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
    if response.json()["media_id"]:
        print("草稿发布成功")
    else:
        print("草稿发布失败:{response.json()}")


# 微信发布正式内容（草稿）接口如下，有free publish、batchget、get_status等功能
# 微信 Free Publish - 获取草稿箱列表
def get_wechat_draft_list():
    """
    获取草稿箱列表 (微信官方draft_batchget接口)
    """
    try:
        data = request.json or {}
        offset = int(data.get('offset', 0))
        count = int(data.get('count', 20))

        access_token = get_access_token(appid, appsecret)
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
        return jsonify(wx_data)

    except Exception as e:
        import traceback
        print("获取草稿列表异常:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# 微信 Free Publish - 发布草稿
def wechat_submit():
    """发布草稿"""
    try:
        access_token = get_access_token(appid, appsecret)
        if not access_token:
            return jsonify({'error': '获取access_token失败'}), 500

        data = request.json or {}
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
        resp = requests.post(url, json=data, timeout=30)
        return jsonify(resp.json())

    except Exception as e:
        import traceback
        print("微信 submit 异常:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@wxgzh_bp.route('/wxgzh', methods=['POST'])
def draft_article():
    create_article()
    
    return jsonify({"message": f"1"})
