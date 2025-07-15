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


## GET /api/xxx

### 描述


### 请求参数

无

### 示例响应
```json

```

### 响应字段


---

## GET /api/xxx

### 描述


### 请求参数

无

### 示例响应
```json

```

### 响应字段


---


## GET /api/xxx

### 描述


### 请求参数

无

### 示例响应
```json

```

### 响应字段


---


## GET /api/xxx

### 描述


### 请求参数

无

### 示例响应
```json

```

### 响应字段


---


## GET /api/xxx

### 描述


### 请求参数

无

### 示例响应
```json

```

### 响应字段


---


## GET /api/xxx

### 描述


### 请求参数

无

### 示例响应
```json

```

### 响应字段


---


## GET /api/xxx

### 描述


### 请求参数

无

### 示例响应
```json

```

### 响应字段


---