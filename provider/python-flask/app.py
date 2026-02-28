"""
AAP Provider Template (Python/Flask)

最小可运行的 AAP Provider 实现，快速搭建自己的 Provider 服务。

Usage:
    pip install -r requirements.txt
    python app.py
    
    # 访问 http://localhost:5000/api/v1/resolve 测试
"""

import uuid
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, g
import json
import os

app = Flask(__name__)

# ==================== 存储层 (可替换为真实数据库) ====================

class InMemoryDB:
    """内存存储，生产环境请替换为真实数据库"""
    
    def __init__(self):
        self.agents = {}      # {aap_address: agent_data}
        self.messages = {}     # {owner_role: [messages]}
        self.api_keys = {}     # {api_key: owner_role}
    
    def register_agent(self, aap_address, model):
        owner_role = aap_address.split('#')[0].replace('ai:', '')
        api_key = self._generate_api_key(aap_address)
        
        self.agents[aap_address] = {
            "aap_address": aap_address,
            "owner_role": owner_role,
            "model": model,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "public_key": ""
        }
        
        self.api_keys[api_key] = owner_role
        self.messages[owner_role] = []
        
        return {
            "success": True,
            "aap_address": aap_address,
            "api_key": api_key,
            "provider": aap_address.split('#')[1] if '#' in aap_address else "",
            "message": "Agent registered successfully"
        }
    
    def _generate_api_key(self, address):
        raw = f"{address}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]
    
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
    
    def add_message(self, owner_role, message):
        if owner_role not in self.messages:
            self.messages[owner_role] = []
        self.messages[owner_role].append(message)
    
    def get_messages(self, owner_role, limit=20):
        msgs = self.messages.get(owner_role, [])
        return msgs[-limit:]
    
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
        return jsonify({"error": "INVALID_REQUEST", "message": "Missing JSON body"}), 400
    
    aap_address = data.get("aap_address", "").strip()
    model = data.get("model", "unknown")
    
    # 简单验证
    if not aap_address.startswith("ai:"):
        return jsonify({"error": "INVALID_ADDRESS", "message": "Address must start with 'ai:'"}), 400
    
    # 检查是否已注册
    if db.get_agent(aap_address):
        return jsonify({"error": "ALREADY_EXISTS", "message": "Agent already registered"}), 409
    
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
            "version": "0.03",
            "aap": "ai:name~role#provider.com",
            "public_key": "",
            "receive": {
                "inbox_url": "https://provider.com/api/v1/inbox/name_role"
            }
        }
    """
    aap_address = request.args.get("address", "").strip()
    
    if not aap_address:
        return jsonify({"error": "MISSING_ADDRESS", "message": "Address parameter required"}), 400
    
    result = db.resolve(aap_address)
    
    if not result:
        return jsonify({
            "error": "NOT_FOUND",
            "message": f"Address {aap_address} not found"
        }), 404
    
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
        return jsonify({"error": "INVALID_REQUEST", "message": "Missing JSON body"}), 400
    
    envelope = data.get("envelope", {})
    payload = data.get("payload", {})
    
    # 验证必填字段
    required = ["from_addr", "to_addr"]
    for field in required:
        if not envelope.get(field):
            return jsonify({"error": "MISSING_FIELD", "message": f"Missing required field: {field}"}), 400
    
    # 验证目标地址属于这个 Provider
    to_addr = envelope.get("to_addr", "")
    expected_prefix = f"~#{request.host}"
    
    # 简单验证（生产环境需要更严格）
    if request.host not in to_addr:
        return jsonify({"error": "WRONG_PROVIDER", "message": "Message not for this provider"}), 400
    
    # 存储消息
    message = {
        "id": str(uuid.uuid4()),
        "envelope": envelope,
        "payload": payload,
        "received_at": datetime.utcnow().isoformat() + "Z"
    }
    
    db.add_message(owner_role, message)
    
    return jsonify({
        "success": True,
        "message": "Message received",
        "message_id": message["id"]
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
        "version": "0.03",
        "endpoints": {
            "register": "/api/agent/register",
            "resolve": "/api/v1/resolve",
            "receive": "/api/v1/inbox/{owner_role}",
            "inbox": "/api/v1/inbox"
        }
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ==================== 启动 ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    print(f"""
╔═══════════════════════════════════════════════════╗
║         AAP Provider Template v0.03               ║
╠═══════════════════════════════════════════════════╣
║  Server running at: http://localhost:{port}            ║
║                                                       ║
║  Endpoints:                                          ║
║  - POST /api/agent/register   注册 Agent            ║
║  - GET  /api/v1/resolve      解析地址               ║
║  - POST /api/v1/inbox/:user  接收消息               ║
║  - GET  /api/v1/inbox        获取收件箱             ║
╚═══════════════════════════════════════════════════╝
    """)
    
    app.run(host="0.0.0.0", port=port, debug=debug)
