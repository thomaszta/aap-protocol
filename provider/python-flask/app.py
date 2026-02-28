"""
AAP Provider Template (Python/Flask)

最小可运行的 AAP Provider 实现，快速搭建自己的 Provider 服务。

Usage:
    pip install -r requirements.txt
    python app.py
    
    # 访问 http://localhost:5000/api/v1/resolve 测试
"""

import uuid
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, g
import os

app = Flask(__name__)

# ==================== 输入验证常量 ====================
MAX_OWNER_LENGTH = 64
MAX_ROLE_LENGTH = 64
MAX_PROVIDER_LENGTH = 253
VALID_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
)

# 验证地址组件
def validate_address_component(value: str, name: str, max_len: int) -> bool:
    """Validate a single address component. Returns True if valid."""
    if not value:
        return False
    if len(value) > max_len:
        return False
    # 检查有效字符
    return all(c in VALID_CHARS for c in value)

# ==================== 错误码定义 (遵循 v0.03 规范) ====================

ERROR_CODES = {
    "INVALID_REQUEST": (400, "Invalid request format or missing required fields"),
    "INVALID_ADDRESS": (400, "Address format is invalid"),
    "ADDRESS_NOT_FOUND": (404, "Address not found on this Provider"),
    "AUTHENTICATION_REQUIRED": (401, "Authentication required but not provided"),
    "AUTHENTICATION_FAILED": (403, "Authentication provided but invalid"),
    "INVALID_ENVELOPE": (400, "Message envelope is malformed"),
    "RATE_LIMIT_EXCEEDED": (429, "Too many requests"),
    "INTERNAL_ERROR": (500, "Provider internal error"),
    "ALREADY_EXISTS": (409, "Agent already registered"),
    "MISSING_FIELD": (400, "Missing required field"),
    "WRONG_PROVIDER": (400, "Message not for this provider"),
}


def error_response(code: str, message: str = None):
    """Return standardized error response."""
    status, default_msg = ERROR_CODES.get(code, (500, "Internal error"))
    return jsonify({
        "error": {
            "code": code,
            "message": message or default_msg
        }
    }), status


# ==================== 存储层 (可替换为真实数据库) ====================

class InMemoryDB:
    """内存存储，生产环境请替换为真实数据库"""
    
    def __init__(self):
        self.agents = {}      # {aap_address: agent_data}
        self.messages = {}     # {owner_role: {idempotency_key: message}}
        self.api_keys = {}     # {api_key: owner_role}
        self.idempotency = {}  # {idempotency_key: response}
    
    def register_agent(self, aap_address, model):
        owner_role = aap_address.split('#')[0].replace('ai:', '')
        api_key = self._generate_api_key()
        
        self.agents[aap_address] = {
            "aap_address": aap_address,
            "owner_role": owner_role,
            "model": model,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "public_key": ""
        }
        
        self.api_keys[api_key] = owner_role
        self.messages[owner_role] = {}
        
        return {
            "success": True,
            "aap_address": aap_address,
            "api_key": api_key,
            "provider": aap_address.split('#')[1] if '#' in aap_address else "",
            "message": "Agent registered successfully"
        }
    
    def _generate_api_key(self):
        """Generate secure API key using secrets module."""
        return secrets.token_urlsafe(32)
    
    def resolve(self, aap_address):
        """Resolve AAP address"""
        if aap_address in self.agents:
            agent = self.agents[aap_address]
            return {
                "version": "0.03",
                "aap": aap_address,
                "public_key": agent.get("public_key", ""),
                "receive": {
                    "inbox_url": f"/api/v1/inbox/{agent['owner_role']}"
                }
            }
        return None
    
    def get_agent(self, aap_address):
        return self.agents.get(aap_address)
    
    def add_message(self, owner_role, message, idempotency_key=None):
        """Add message with optional idempotency key."""
        if owner_role not in self.messages:
            self.messages[owner_role] = {}
        
        # 幂等性检查
        if idempotency_key and idempotency_key in self.messages[owner_role]:
            return self.messages[owner_role][idempotency_key]
        
        msg_id = str(uuid.uuid4())
        message["id"] = msg_id
        message["received_at"] = datetime.utcnow().isoformat() + "Z"
        
        # 如果有幂等性 key，存储映射
        if idempotency_key:
            self.messages[owner_role][idempotency_key] = message
        
        # 同时存储到列表（用于获取）
        if owner_role not in self.messages:
            self.messages[owner_role] = {}
        self.messages[owner_role]["_list"] = self.messages[owner_role].get("_list", [])
        self.messages[owner_role]["_list"].append(message)
        
        return message
    
    def get_messages(self, owner_role, limit=20):
        """Get messages for owner_role."""
        msg_dict = self.messages.get(owner_role, {})
        msg_list = msg_dict.get("_list", [])
        return msg_list[-limit:]
    
    def verify_api_key(self, api_key):
        return self.api_keys.get(api_key)


# 初始化数据库
db = InMemoryDB()

# ==================== 辅助装饰器 ====================

def require_auth(f):
    """API Key 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "UNAUTHORIZED", "message": "Missing or invalid API key"}), 401
        
        api_key = auth[7:]  # 去掉 "Bearer "
        owner_role = db.verify_api_key(api_key)
        
        if not owner_role:
            return jsonify({"error": "UNAUTHORIZED", "message": "Invalid API key"}), 401
        
        g.owner_role = owner_role
        return f(*args, **kwargs)
    return decorated


# ==================== Agent 注册 API ====================

@app.route("/api/agent/register", methods=["POST"])
def register_agent():
    """
    注册 Agent
    
    Request:
        {
            "aap_address": "ai:name~role#provider.com",
            "model": "gpt-4"
        }
    
    Response:
        {
            "success": true,
            "aap_address": "ai:name~role#provider.com",
            "api_key": "abc123...",
            "provider": "provider.com",
            "message": "Agent registered successfully"
        }
    """
    data = request.get_json()
    
    if not data:
        return error_response("INVALID_REQUEST", "Missing JSON body")
    
    aap_address = data.get("aap_address", "").strip()
    model = data.get("model", "unknown")
    
    # 简单验证
    if not aap_address.startswith("ai:"):
        return error_response("INVALID_ADDRESS", "Address must start with 'ai:'")
    
    # 检查长度
    if len(aap_address) > 500:
        return error_response("INVALID_ADDRESS", "Address too long (max 500 characters)")
    
    # 解析并验证各组件
    try:
        parts = aap_address[3:].split('#')
        if len(parts) != 2:
            return error_response("INVALID_ADDRESS", "Invalid address format")
        owner_role, provider = parts
        owner, role = owner_role.split('~')
        if not owner or not role or not provider:
            return error_response("INVALID_ADDRESS", "Empty component")
        if not validate_address_component(owner, "owner", MAX_OWNER_LENGTH):
            return error_response("INVALID_ADDRESS", "Invalid owner characters or too long")
        if not validate_address_component(role, "role", MAX_ROLE_LENGTH):
            return error_response("INVALID_ADDRESS", "Invalid role characters or too long")
        if not validate_address_component(provider, "provider", MAX_PROVIDER_LENGTH):
            return error_response("INVALID_ADDRESS", "Invalid provider characters or too long")
    except Exception:
        return error_response("INVALID_ADDRESS", "Invalid address format")
    
    # 检查是否已注册
    if db.get_agent(aap_address):
        return error_response("ALREADY_EXISTS", "Agent already registered")
    
    result = db.register_agent(aap_address, model)
    return jsonify(result), 201


# ==================== Resolve API ====================

@app.route("/api/v1/resolve", methods=["GET"])
def resolve():
    """
    Resolve AAP address
    
    GET /api/v1/resolve?address=ai:name~role#provider.com
    
    Response:
        {
            "version": "0.04",
            "aap": "ai:name~role#provider.com",
            "public_key": "",
            "receive": {
                "inbox_url": "https://provider.com/api/v1/inbox/name_role"
            }
        }
    """
    aap_address = request.args.get("address", "").strip()
    
    if not aap_address:
        return error_response("INVALID_REQUEST", "Address parameter required")
    
    if len(aap_address) > 500:
        return error_response("INVALID_ADDRESS", "Address too long")
    
    result = db.resolve(aap_address)
    
    if not result:
        return error_response("ADDRESS_NOT_FOUND", f"Address {aap_address} not found")
    
    # 转换为完整 URL（生产环境需要配置 BASE_URL）
    base_url = request.host_url.rstrip('/')
    result["receive"]["inbox_url"] = base_url + result["receive"]["inbox_url"]
    
    return jsonify(result)


# ==================== Receive API (收消息) ====================

@app.route("/api/v1/inbox/<owner_role>", methods=["POST"])
def receive_message(owner_role):
    """
    接收消息
    
    POST /api/v1/inbox/{owner_role}
    
    Body:
        {
            "envelope": {
                "from_addr": "ai:sender~role#provider.com",
                "to_addr": "ai:receiver~role#provider.com",
                "message_type": "private",
                "reply_to": "optional-message-id",
                "content_type": "text/plain",
                "timestamp": "2026-01-01T00:00:00Z"
            },
            "payload": {
                "content": "Hello!",
                "metadata": {}
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return error_response("INVALID_REQUEST", "Missing JSON body")
    
    envelope = data.get("envelope", {})
    payload = data.get("payload", {})
    
    # 验证必填字段
    required = ["from_addr", "to_addr"]
    for field in required:
        if not envelope.get(field):
            return error_response("MISSING_FIELD", f"Missing required field: {field}")
    
    # 验证目标地址属于这个 Provider
    to_addr = envelope.get("to_addr", "")
    
    # 简单验证（生产环境需要更严格）
    if request.host not in to_addr:
        return error_response("WRONG_PROVIDER", "Message not for this provider")
    
    # 获取幂等性 key
    idempotency_key = request.headers.get("X-Idempotency-Key")
    
    # 存储消息（支持幂等性）
    message = {
        "envelope": envelope,
        "payload": payload
    }
    
    result = db.add_message(owner_role, message, idempotency_key)
    
    return jsonify({
        "success": True,
        "message": "Message received",
        "message_id": result["id"]
    }), 201


# ==================== Inbox API (取消息) ====================

@app.route("/api/v1/inbox", methods=["GET"])
@require_auth
def get_inbox():
    """
    获取收件箱
    
    GET /api/v1/inbox?limit=20
    
    Headers:
        Authorization: Bearer {api_key}
    """
    limit = request.args.get("limit", 20, type=int)
    messages = db.get_messages(g.owner_role, limit)
    
    return jsonify({
        "messages": messages,
        "count": len(messages)
    })


# ==================== 静态文件 / 健康检查 ====================

@app.route("/")
def index():
    return jsonify({
        "name": "AAP Provider",
        "version": "0.04",
        "endpoints": {
            "register": "/api/agent/register",
            "resolve": "/api/v1/resolve",
            "receive": "/api/v1/inbox/{owner_role}",
            "inbox": "/api/v1/inbox",
            "providers_info": "/api/v1/providers/info"
        }
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ==================== Provider Info (v0.04 Stage 1) ====================

@app.route("/api/v1/providers/info", methods=["GET"])
def provider_info():
    """
    Get Provider information (v0.04 Stage 1).
    
    This optional endpoint provides information about the Provider,
    including supported capabilities and discovery method.
    
    Response:
        {
            "provider": "provider.com",
            "version": "0.04",
            "capabilities": ["resolve", "inbox", "register"],
            "discovery_method": "direct"
        }
    """
    return jsonify({
        "provider": request.host,
        "version": "0.04",
        "capabilities": ["resolve", "inbox", "register"],
        "discovery_method": "direct"
    })


# ==================== 启动 ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    print(f"""
╔═══════════════════════════════════════════════════╗
║         AAP Provider Template v0.04               ║
╠═══════════════════════════════════════════════════╣
║  Server running at: http://localhost:{port}            ║
║                                                       ║
║  Endpoints:                                          ║
║  - POST /api/agent/register   注册 Agent            ║
║  - GET  /api/v1/resolve      解析地址               ║
║  - GET  /api/v1/providers    Provider 信息          ║
║  - POST /api/v1/inbox/:user  接收消息               ║
║  - GET  /api/v1/inbox        获取收件箱             ║
╚═══════════════════════════════════════════════════╝
    """)
    
    app.run(host="0.0.0.0", port=port, debug=debug)
