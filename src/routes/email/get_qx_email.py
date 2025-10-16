import imaplib
import email
from email.header import decode_header
import requests
import json
import time
from datetime import datetime, timedelta
from flask_cors import CORS

# 配置 - 替换为实际值
# 注意：现在main函数接受参数，而不是使用dotenv

def connect_imap(email_addr, password, imap_server, imap_port):
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    mail.login(email_addr, password)
    mail.select("inbox")  # 选择收件箱
    return mail

def fetch_email_list(mail, minutes_ago=None):
    search_criteria = "ALL"  # 默认所有邮件
    if minutes_ago:
        # 计算开始时间（minutes_ago分钟之前）
        start_time = datetime.now() - timedelta(minutes=minutes_ago)
        since_date = start_time.strftime("%d-%b-%Y")  # 如'23-Sep-2025'
        search_criteria = f'(SINCE "{since_date}")'
    
    status, messages = mail.search(None, search_criteria)
    if status != "OK":
        raise Exception("Failed to search emails")
    return messages[0].split()  # 返回邮件ID列表

def decode_with_fallback(bytes_data, charset=None):
    """尝试使用指定编码解码，如果失败则回退常见编码"""
    encodings = [charset] if charset else []
    encodings += ['utf-8', 'gbk', 'gb18030', 'iso-8859-1', 'windows-1252']
    for enc in encodings:
        if enc:
            try:
                return bytes_data.decode(enc)
            except UnicodeDecodeError:
                continue
    # 如果都失败，返回原始字节作为字符串（避免崩溃）
    return str(bytes_data)

def get_email_date(mail, msg_id):
    """获取邮件的发送时间"""
    status, msg = mail.fetch(msg_id, "(RFC822)")
    if status != "OK":
        return None
    email_msg = email.message_from_bytes(msg[0][1])
    date_str = email_msg["Date"]
    if date_str:
        try:
            # 解析邮件日期
            email_date = email.utils.parsedate_to_datetime(date_str)
            # 转换为本地时间（如果需要）
            if email_date.tzinfo is None:
                email_date = email_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            return email_date.replace(tzinfo=None)  # 移除时区信息以便比较
        except:
            return None
    return None

def fetch_email_content(mail, msg_id):
    status, msg = mail.fetch(msg_id, "(RFC822)")
    if status != "OK":
        raise Exception("Failed to fetch email")
    email_msg = email.message_from_bytes(msg[0][1])
    
    # 处理主题：正确解码每个部分
    subject_parts = decode_header(email_msg["Subject"] or "")
    subject = ""
    for part, charset in subject_parts:
        if isinstance(part, bytes):
            subject += decode_with_fallback(part, charset)
        else:
            subject += part
    
    from_email = email.utils.parseaddr(email_msg["From"])[1]
    
    # 获取内容（处理多部分）
    content = ""
    if email_msg.is_multipart():
        for part in email_msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                content = decode_with_fallback(payload, charset)
                break  # 优先纯文本
            elif part.get_content_type() == "text/html" and not content:
                # 如果没有纯文本，回退到HTML（但简化处理）
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                content = decode_with_fallback(payload, charset)
    else:
        payload = email_msg.get_payload(decode=True)
        charset = email_msg.get_content_charset()
        content = decode_with_fallback(payload, charset)
    
    return f"From: {from_email}\nSubject: {subject}\nContent: {content}"

def predict_phishing(phishing_url, email_content):
    body = {"email_content": email_content}  # 调整key如果需要
    response = requests.post(phishing_url, json=body)
    data = response.json()
    # print(data)
    return data.get("result")

def send_to_webhook(webhook_url, message):
    body = {
        "msgtype": "text",
        "text": {"content": message}
    }
    response = requests.post(webhook_url, json=body)
    if response.json().get("errcode") != 0:
        print("Failed to send to webhook")
    else:
        print("Message sent")

def main(minutes, email_addr, password, imap_server, imap_port, webhook_url, phishing_api_url="http://localhost:8891/api/phishing/predict"):
    """
    检查单个邮箱中的钓鱼邮件
    
    Args:
        minutes: 检查多少分钟内的邮件
        email_addr: 邮箱地址
        password: 邮箱密码
        imap_server: IMAP服务器地址
        imap_port: IMAP端口
        webhook_url: 企业微信Webhook URL
        phishing_api_url: 钓鱼邮件检测API地址
    """
    try:
        mail = connect_imap(email_addr, password, imap_server, imap_port)
        
        # 计算时间范围
        current_time = datetime.now()
        start_time = current_time - timedelta(minutes=minutes)
        
        # 先获取可能的邮件列表（按天筛选，避免获取太多邮件）
        email_ids = fetch_email_list(mail, minutes)
        
        # 精确筛选：检查每封邮件的时间戳是否在指定范围内
        filtered_emails = []
        phishing_count = 0  # 添加钓鱼邮件计数器
        
        for email_id in email_ids:
            email_date = get_email_date(mail, email_id)
            if email_date and start_time <= email_date <= current_time:
                filtered_emails.append(email_id)
        
        print(f"找到 {len(filtered_emails)} 封邮件在过去 {minutes} 分钟内 for {email_addr}")
        
        # 处理筛选后的邮件
        for email_id in filtered_emails:
            content = fetch_email_content(mail, email_id)
            is_phishing = predict_phishing(phishing_api_url, content)
            result = "phishing" if is_phishing == "Phishing" else "Safe"
            
            # 统计钓鱼邮件数量
            if is_phishing == "Phishing":
                phishing_count += 1
                # 只有在检测到钓鱼邮件时才发送通知
                message = f"⚠️ 钓鱼邮件警报!\nEmail ID: {email_id.decode()}\nResult: {result}\nDetails: {content[:200]}..."
                send_to_webhook(webhook_url, message)
                
        mail.logout()
        # 返回符合时间范围的邮件ID和钓鱼邮件数量
        return {
            'email_ids': [eid.decode() for eid in filtered_emails],
            'phishing_count': phishing_count
        }
    except Exception as e:
        print(f"Error for {email_addr}: {e}")
        # 发生错误时也发送通知
        try:
            error_message = f"❌ 邮件检测出错!\n邮箱: {email_addr}\n错误: {str(e)}"
            send_to_webhook(webhook_url, error_message)
        except:
            pass
        return {'email_ids': [], 'phishing_count': 0}  # 错误时返回空列表