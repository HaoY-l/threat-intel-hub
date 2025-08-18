# Threat Intel API 文档

## 通用信息

* 统一接口前缀：`/api`
* 响应格式：`application/json`
* 时间格式：ISO8601

---

## GET /api/cve

### 描述

获取阿里云漏洞中心每天最新的 【漏洞】 数据

### 请求参数

无

### 示例响应

```json
[
  {
    "created_at": "Tue, 15 Jul 2025 02:46:09 GMT",
    "cve_id": "AVD-2025-25257",
    "description": "",
    "id": 1352,
    "published": "Mon, 14 Jul 2025 00:00:00 GMT",
    "severity": "CVE\n                            \nPoC",
    "source": "Aliyun AVD",
    "title": "Fortinet FortiWeb Fabric Connector SQL注入漏洞（CVE-2025-25257）",
    "updated_at": "Tue, 15 Jul 2025 02:46:09 GMT",
    "url": "https://avd.aliyun.com/detail?id=AVD-2025-25257"
  },
  {
    "created_at": "Tue, 15 Jul 2025 02:46:09 GMT",
    "cve_id": "AVD-2025-53689",
    "description": "",
    "id": 1351,
    "published": "Mon, 14 Jul 2025 00:00:00 GMT",
    "severity": "CVE\n                            \nPoC",
    "source": "Aliyun AVD",
    "title": "Apache Jackrabbit XXE漏洞（CVE-2025-53689）",
    "updated_at": "Tue, 15 Jul 2025 02:46:09 GMT",
    "url": "https://avd.aliyun.com/detail?id=AVD-2025-53689"
  }
]
```

### 响应字段

| 字段名         | 类型     | 描述                 |
| ----------- | ------ | ------------------ |
| id          | number | 自增 ID              |
| cve\_id     | string | CVE 编号             |
| title       | string | 标题                 |
| description | string | 漏洞描述               |
| severity    | string | 严重程度（如 CVE/PoC/级别） |
| source      | string | 数据来源               |
| url         | string | 外部链接               |
| published   | string | 发布时间 (ISO8601)     |
| created\_at | string | 创建时间 (ISO8601)     |
| updated\_at | string | 更新时间 (ISO8601)     |

---

## POST /api/query

### 描述

根据 target 查询威胁情报

### 请求参数 (JSON)

| 字段    | 类型     | 是否必填 | 描述              |
| ----- | ------ | ---- | --------------- |
| value | string | 是    | 查询对象（ip/域名/文件）  |
| type  | string | 是    | 类型（ip/url/file） |

### 示例请求

```json
{
  "value": "8.8.8.8",
  "type": "ip"
}
```

### 示例响应

#### IP 类型

```json
{
  "results": {
    "AlienVault OTX": {
      "created_at": "Mon, 14 Jul 2025 02:18:41 GMT",
      "details": "",
      "from_cache": true,
      "id": "87.236.176.190",
      "last_update": "Mon, 14 Jul 2025 02:18:41 GMT",
      "reputation_score": 0,
      "source": "AlienVault OTX",
      "threat_level": "medium",
      "type": "ip",
      "updated_at": "Mon, 14 Jul 2025 02:18:41 GMT"
    },
    "VirusTotal": {
      "created_at": "Mon, 14 Jul 2025 02:18:37 GMT",
      "details": "",
      "from_cache": true,
      "id": "87.236.176.190",
      "last_update": "Sun, 13 Jul 2025 23:09:16 GMT",
      "reputation_score": -3,
      "source": "VirusTotal",
      "threat_level": "high",
      "type": "ip",
      "updated_at": "Mon, 14 Jul 2025 02:18:37 GMT"
    }
  },
  "status": "success",
  "type": "ip",
  "value": "87.236.176.190"
}
```

#### URL 类型

```json
{
  "results": {
    "AlienVault OTX": {
      "created_at": "Mon, 14 Jul 2025 02:26:02 GMT",
      "details": "",
      "from_cache": true,
      "id": "http://truewarstoriespodcast.com/",
      "last_update": "Mon, 14 Jul 2025 02:27:25 GMT",
      "reputation_score": 0,
      "source": "AlienVault OTX",
      "target_url": "http://truewarstoriespodcast.com/",
      "type": "url",
      "updated_at": "Mon, 14 Jul 2025 02:27:25 GMT"
    },
    "VirusTotal": {
      "created_at": "Mon, 14 Jul 2025 02:19:31 GMT",
      "details": "",
      "from_cache": true,
      "id": "992bd646ed4505a4263247be2c0e3a41a8ea6223557f3981ebb1373036753b75",
      "last_update": "Sat, 12 Jul 2025 01:01:48 GMT",
      "reputation_score": 0,
      "source": "VirusTotal",
      "target_url": "http://truewarstoriespodcast.com/",
      "type": "url",
      "updated_at": "Mon, 14 Jul 2025 02:19:31 GMT"
    }
  },
  "status": "success",
  "type": "url",
  "value": "http://truewarstoriespodcast.com/"
}
```

#### File 类型

```json
{
  "results": {
    "AlienVault OTX": {
      "created_at": "Mon, 14 Jul 2025 02:38:07 GMT",
      "details": "",
      "from_cache": true,
      "id": "9d08d1ff2d678b150b252c90f30df24a41f2aa0577ac09fa9104085c1d85809b",
      "last_update": "Mon, 14 Jul 2025 09:01:46 GMT",
      "reputation_score": 0,
      "source": "AlienVault OTX",
      "threat_level": "medium",
      "type": "file",
      "updated_at": "Mon, 14 Jul 2025 09:01:46 GMT"
    },
    "VirusTotal": {
      "created_at": "Mon, 14 Jul 2025 02:38:06 GMT",
      "details": "",
      "from_cache": true,
      "id": "9d08d1ff2d678b150b252c90f30df24a41f2aa0577ac09fa9104085c1d85809b",
      "last_update": "Tue, 08 Jul 2025 23:28:19 GMT",
      "reputation_score": 0,
      "source": "VirusTotal",
      "threat_level": "medium",
      "type": "file",
      "updated_at": "Mon, 14 Jul 2025 02:38:06 GMT"
    }
  },
  "status": "success",
  "type": "file",
  "value": "9d08d1ff2d678b150b252c90f30df24a41f2aa0577ac09fa9104085c1d85809b"
}
```

---


## GET /api/listwhite

### 描述
列举阿里云WAF所有白名单列表

### 请求参数

无

### 示例响应
```json
{
  "message": [
    {
      "rule_id": 10238952,
      "rule_name": "yyy白名单",
      "rule_template": 208428
    },
    {
      "rule_id": 10238951,
      "rule_name": "xxx白名单",
      "rule_template": 208428
    }]
}
```
### 响应字段
| 字段名         | 类型     | 描述                 |
| ----------- | ------ | ------------------ |
| rule_id          | number | 白名单id              |
| rule_name     | string | 白名单命名             |
| rule_template       | number | 白名单模版id                 |


---

## GET /api/addwhite

### 描述
添加阿里云WAF白名单

### 请求参数
json数组
```json
[
    {
        "name": "test1",
        "tags": ["waf"],
        "status": 1,
        "origin": "custom",
        "conditions": [
            {
                "key": "IP",
                "opValue": "contain",
                "subKey": "",
                "values": "124.222.195.27"
            }
        ]
    }
]
```
### 示例响应
```json
{
  "message": "白名单添加成功",
  "status": "success"
}
```

### 响应字段

| 字段名         | 类型     | 描述                 |
| ----------- | ------ | ------------------ |
| message          | string | 消息              |
| status     | string | 返回状态             |
---


## POST /api/deletewhite

### 描述
通过阿里云WAF的白名单规则id，删除对应的白名单规则

### 请求参数
```json
{
    "rule_id":"10238959"
}
```
### 示例响应
```json
{
  "code": 200,
  "msg": "删除成功"
}
```
### 响应字段


---


## GET /api/descblackrule

### 描述
显示固定模版下固定规则的黑名单IP列表

### 请求参数

无

### 示例响应
```json
{
  "message": [
    {
      "ip_list": [
        "116.238.81.166",
        "183.223.240.178",
      ],
      "rule_id": 20705051,
      "rule_name": "IpBlackList",
      "template_id": 179863
    }
  ],
  "status": "success"
}
```

### 响应字段


---



## POST /api/modifyblackrule

### 描述
添加黑名单IP接口

### 请求参数

{
    "black_ip": "247.xx.xx.42"
}

### 示例响应
```json

```

### 响应字段


---

## GET /api/blocked_ips

### 描述
查询封禁IP信息（15分钟内）接口

### 请求参数

暂无

### 示例响应
```json
{
  "count": 1,
  "message": "封禁IP数据保存成功"
}
```

### 响应字段


---


## GET /api/ip_request_frequency

### 描述
查询IP请求频率（5分钟内）接口

### 请求参数
暂无

### 示例响应
```json
{
  "message": "请求频率数据保存成功",
  "saved_count": 1
}
```

### 响应字段


---


## POST /api/wxgzh

### 描述
微信公众号自动推文

### 请求参数
暂无

### 示例响应
```json

```

### 响应字段


---

## GET /api/alert

### 描述
钉钉waf封禁播报（日报）

### 请求参数
暂无

### 示例响应
{
  "message": "Daily report sent successfully.",
  "status": "success"
}

### 响应字段


---


## GET /api/news

### 描述
Freebuf、CSDN最新安全资讯获取

### 请求参数
暂无

### 示例响应
[
  {
    "author": "一只牛博",
    "category": "网络安全",
    "content": "",
    "cover": "https://i-blog.csdnimg.cn/direct/f824564ffa654b45a8ede7f0c4e43548.png",
    "created_at": "2025-08-18T03:08:00",
    "hot": 20864,
    "id": 6,
    "mobile_url": "https://blog.csdn.net/Mrxiao_bo/article/details/150447592",
    "published_at": "2025-08-18T11:07:58",
    "source": "CSDN",
    "summary": "暂无描述信息...",
    "time": "刚刚",
    "timestamp": 1755486478,
    "title": "从0到1掌握 Spring Security（第三篇）：三种认证方式，按配置一键切换",
    "updated_at": "2025-08-18T03:08:00",
    "url": "https://blog.csdn.net/Mrxiao_bo/article/details/150447592"
  },
]

### 响应字段


---