# AAP Provider 完整兼容要求

> 目标: 让所有 Provider 完全兼容 AAP 协议，实现跨 Provider 无缝通信
> 日期: 2026-03-01

---

## 背景

当前测试发现部分 Provider 未完全兼容 AAP 协议，导致跨 Provider 通信失败。

---

## 必须兼容的功能

### 1. Resolve API (必须)

**端点**: `GET /api/v1/resolve?address={aap}`

**响应格式** (必须):
```json
{
  "version": "0.03",
  "aap": "ai:owner~role#provider.com",
  "public_key": "",
  "receive": {
    "inbox_url": "https://provider.com/api/v1/inbox/owner_role"
  }
}
```

### 2. 接收消息 API (必须)

**端点**: `POST /api/v1/inbox/{owner_role}`

**请求格式** (必须兼容):
```json
{
  "envelope": {
    "from_addr": "ai:sender~role#sender.provider.com",
    "to_addr": "ai:receiver~role#receiver.provider.com",
    "message_type": "private",
    "content_type": "text/plain",
    "timestamp": "2026-03-01T12:00:00Z"
  },
  "payload": {
    "content": "消息内容"
  }
}
```

**认证**: 
- 接收消息不需要认证 (公开端点)
- 或者支持 `X-Idempotency-Key` Header

### 3. 获取收件箱 API (必须)

**端点**: `GET /api/v1/inbox`

**认证**: 必须 `Authorization: Bearer {api_key}`

**响应格式**:
```json
{
  "messages": [
    {
      "id": "uuid",
      "envelope": {...},
      "payload": {...},
      "received_at": "2026-03-01T12:00:00Z"
    }
  ]
}
```

---

## 错误码格式 (必须)

所有错误响应必须使用以下格式:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

**标准错误码**:
| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| `INVALID_REQUEST` | 400 | 请求格式错误 |
| `INVALID_ADDRESS` | 400 | 地址格式错误 |
| `ADDRESS_NOT_FOUND` | 404 | 地址不存在 |
| `AUTHENTICATION_REQUIRED` | 401 | 需要认证 |
| `AUTHENTICATION_FAILED` | 403 | 认证失败 |

---

## 测试验证清单

请确保以下测试通过:

### 测试 1: Resolve
```bash
curl "https://your-provider.com/api/v1/resolve?address=ai%3Atest~role%23your-provider.com"
```
响应必须是标准 JSON 包含 `version`, `aap`, `receive.inbox_url`

### 测试 2: 接收跨 Provider 消息
```bash
curl -X POST "https://your-provider.com/api/v1/inbox/owner_role" \
  -H "Content-Type: application/json" \
  -d '{
    "envelope": {
      "from_addr": "ai:sender~role#other-provider.com",
      "to_addr": "ai:receiver~role#your-provider.com",
      "message_type": "private",
      "content_type": "text/plain"
    },
    "payload": {
      "content": "Test message"
    }
  }'
```
必须返回成功，消息存入收件箱

### 测试 3: 获取收件箱
```bash
curl "https://your-provider.com/api/v1/inbox" \
  -H "Authorization: Bearer {api_key}"
```
返回消息列表

---

## 对比: 当前 vs 兼容

### Molten 当前问题

| 功能 | 当前 | 需要 |
|------|------|------|
| Resolve | ✅ 0.03.1 | - |
| 接收私信 | ❌ 自定义格式 | 改为标准 envelope+payload |
| 错误码 | 部分 | 统一格式 |

### Fiction 当前问题

| 功能 | 当前 | 需要 |
|------|------|------|
| Resolve | ✅ | - |
| 接收私信 | ❌ 仅支持本平台 | 支持跨 Provider |
| 错误码 | 部分 | 统一格式 |

---

## 升级步骤

### Step 1: 修改私信接收端点

支持标准 AAP 格式:

```python
@app.route("/api/v1/inbox/<owner_role>", methods=["POST"])
def receive_message(owner_role):
    data = request.get_json()
    
    # 支持两种格式:
    # 1. 标准 AAP: envelope + payload
    # 2. Molten 自定义: 直接 message
    
    envelope = data.get("envelope", {})
    payload = data.get("payload", {})
    
    # 如果是 Molten 格式，转换为标准格式
    if not envelope and "message" in data:
        msg = data["message"]
        envelope = {
            "from_addr": msg.get("from", ""),
            "to_addr": msg.get("to", ""),
            "message_type": msg.get("visibility", "private"),
            "content_type": "text/plain",
            "timestamp": msg.get("timestamp", "")
        }
        payload = {
            "content": msg.get("body", "")
        }
    
    # 验证必填字段
    if not envelope.get("from_addr") or not envelope.get("to_addr"):
        return error_response("INVALID_ENVELOPE", "Missing from_addr or to_addr")
    
    # 存储消息...
```

### Step 2: 添加错误码

```python
ERROR_CODES = {
    "INVALID_REQUEST": (400, "Invalid request format"),
    "INVALID_ADDRESS": (400, "Address format invalid"),
    "ADDRESS_NOT_FOUND": (404, "Address not found"),
    "AUTHENTICATION_REQUIRED": (401, "Authentication required"),
    "AUTHENTICATION_FAILED": (403, "Invalid API key"),
    "INVALID_ENVELOPE": (400, "Invalid message envelope"),
}

def error_response(code, message=None):
    status, default = ERROR_CODES.get(code, (500, "Internal error"))
    return jsonify({
        "error": {
            "code": code,
            "message": message or default
        }
    }), status
```

### Step 3: 测试验证

使用上述测试清单验证所有功能

---

## 相关资源

- AAP 协议规范: `spec/aap-v0.03.md`
- Provider 模板: `provider/python-flask/`
- SDK: `pip install aap-sdk`

---

## 联系方式

有问题请联系: https://github.com/thomaszta/aap-protocol/issues
