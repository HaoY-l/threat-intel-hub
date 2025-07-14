import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query_otx_ip(ip):
    api_key = os.getenv("otx_api_key")
    if not api_key:
        raise ValueError("请先在环境变量中设置 otx_api_key")

    base_url = "https://otx.alienvault.com/api/v1"
    headers = {
        "accept": "application/json",
        "X-OTX-API-KEY": api_key
    }

    url = f"{base_url}/indicators/IPv4/{ip}/general"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

if __name__ == "__main__":
    ip_to_query = "8.8.8.8"  # 测试IP
    result = query_otx_ip(ip_to_query)
    if result:
        print("查询结果：")
        print(result)
    else:
        print("查询失败或无结果。")
