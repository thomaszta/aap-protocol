# AAP v0.04 - Provider 互联方案 (草案)

> **状态**: 草稿 v0.1  
> **目标**: 实现真正的去中心化 Provider 互联发现

---

## 1. 问题定义

### 当前问题

```
Agent A (provider1.com) → 发现 → Agent B (provider2.com)
     ↓
问题1: 怎么知道 provider2.com 存在？
问题2: 怎么访问 provider2.com？
问题3: 怎么认证？
```

### 核心挑战

| 挑战 | 描述 |
|------|------|
| **发现** | 如何知道有哪些 Provider？ |
| **可达** | 如何跨 Provider 网络通信？ |
| **信任** | 如何确认对方是合法 Provider？ |
| **认证** | 如何确认 Agent 身份？ |

---

## 2. 方案设计

### 方案 A: Provider 注册表 (Registry)

#### 2.1 中心化注册表

```
┌─────────────────────────────┐
│   AAP Registry (中心)         │
│   registry.aap-protocol.org  │
│                             │
│   - provider1.com            │
│   - provider2.com           │
│   - fiction.molten.it.com   │
└─────────────────────────────┘
          ↑
     Provider 注册
          ↓
┌─────────┴─────────┐
│   Provider 网络   │
│   互相发现        │
└──────────────────┘
```

**优点**: 简单，实现快  
**缺点**: 有中心化风险

#### 2.2 分布式注册表 (推荐)

```
┌────────────────────────────────────────┐
│         Provider 互联网络               │
│                                        │
│   .──.      .──.      .──.           │
│  (provider1) (provider2) (provider3)  │
│   `──'      `──'      `──'           │
│      ↓        ↓        ↓              │
│   互相发现     互相发现    互相发现    │
│                                        │
│   known_providers = {                  │
│     "provider1.com": {                │
│       "resolve": "https://...",       │
│       "inbox": "https://...",        │
│       "trust_score": 0.9             │
│     }                                 │
│   }                                   │
└────────────────────────────────────────┘
```

**优点**: 去中心化，无单点故障  
**缺点**: 实现复杂，需要同步机制

---

### 2.3 Hybrid 方案 (折中)

```
┌────────────────────────────────────────┐
│            AAP 生态                     │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │   引导 Provider (种子节点)       │  │
│  │   seed1.aap-protocol.org        │  │
│  │   seed2.aap-protocol.org        │  │
│  │   (官方维护，滚动更新)           │  │
│  └─────────────────────────────────┘  │
│                  ↑                     │
│         Provider 启动时拉取            │
│                  ↓                     │
│  ┌─────────────────────────────────┐  │
│  │        Provider 网络             │  │
│  │   定期同步已知 Provider 列表     │  │
│  └─────────────────────────────────┘  │
└────────────────────────────────────────┘
```

**工作流程**:

1. **新 Provider 启动**
   - 连接种子节点获取初始 Provider 列表
   - 获取种子节点的 Known Providers

2. **定期同步**
   - 每个 Provider 定时广播自己的存在
   - 互相更新 Known Providers

3. **跨 Provider 通信**
   - 查本地 Known Providers
   - 如果不存在，查询种子节点
   - 发起 HTTP 请求

---

## 3. API 设计

### 3.1 Provider 注册 (可选)

```http
POST /api/v1/providers/register
Content-Type: application/json

{
  "provider": "my-provider.com",
  "endpoints": {
    "resolve": "https://my-provider.com/api/v1/resolve",
    "inbox": "https://my-provider.com/api/v1/inbox",
    "register": "https://my-provider.com/api/agent/register"
  },
  "public_key": "base64-encoded-key",
  "capabilities": ["resolve", "inbox", "register"],
  "trust_score": 1.0
}
```

### 3.2 Provider 发现

```http
GET /api/v1/providers?capability=resolve

Response:
{
  "providers": [
    {
      "provider": "fiction.molten.it.com",
      "endpoints": {
        "resolve": "https://fiction.molten.it.com/api/v1/resolve",
        "inbox": "https://fiction.molten.it.com/api/v1/inbox"
      },
      "trust_score": 0.95
    }
  ]
}
```

### 3.3 Provider 状态

```http
GET /api/v1/providers/{provider}/health

Response:
{
  "provider": "fiction.molten.it.com",
  "status": "online",
  "last_seen": "2026-02-28T12:00:00Z",
  "agent_count": 150
}
```

---

## 4. 信任模型

### 4.1 Provider 信任评分

| 评分 | 含义 |
|------|------|
| 1.0 | 完全信任 (种子节点) |
| 0.9-0.99 | 高信任 (已验证) |
| 0.7-0.89 | 中等信任 |
| 0.5-0.69 | 低信任 (新节点) |
| <0.5 | 不信任 (拒绝) |

### 4.2 信任计算

```
trust_score = 
  base_score (0.5)
  + age_bonus (上线时间)
  + activity_bonus (活跃度)
  - timeout_penalty (失联扣分)
  + peer_endorsement (其他 Provider 背书)
```

---

## 5. 认证方案

### 5.1 Agent 跨 Provider 认证

```
问题: Provider A 的 Agent 怎么证明自己是合法的？

方案: JWT Token

1. Agent 在 Provider A 注册
   → 获得 AAP Address + API Key

2. Agent 发送消息到 Provider B
   → Header: Authorization: Bearer {jwt_token}
   
3. Provider B 验证 JWT
   → 验证 Provider A 的公钥
   → 验证 Agent 身份
```

### 5.2 JWT 格式

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "provider-a-key-id"
  },
  "payload": {
    "sub": "ai:agent~role#provider-a.com",
    "iss": "provider-a.com",
    "aud": "provider-b.com",
    "exp": 1735689600,
    "iat": 1735686000,
    "capabilities": ["send", "receive"]
  }
}
```

---

## 6. 实现路线

### Phase 1: 种子节点 (MVP)

- [ ] 搭建种子 Provider 注册服务
- [ ] 实现 Provider 注册 API
- [ ] 实现 Provider 发现 API
- [ ] 种子节点定时同步

### Phase 2: Provider 集成

- [ ] Provider 支持注册到种子节点
- [ ] 实现 Known Providers 本地缓存
- [ ] 定期同步机制

### Phase 3: 认证增强

- [ ] 实现 JWT 颁发
- [ ] 实现 JWT 验证
- [ ] 跨 Provider 认证

### Phase 4: 优化

- [ ] 信任评分算法
- [ ] Provider 健康检查
- [ ] 性能优化

---

## 7. 向后兼容性

- [x] 保持 v0.03 所有 API 不变
- [x] 新增 API 都是可选的
- [x] 现有 Provider 不需要修改
- [x] Agent SDK 逐步迁移

---

## 8. 讨论要点

1. **种子节点谁维护？** 官方？社区？多方？
2. **Provider 加入需要审批吗？** 
3. **如何防止恶意 Provider？**
4. **种子节点故障怎么办？**
5. **中国区是否需要独立种子节点？**

---

## 9. 参考

- [联邦模型 (Federation)](https://en.wikipedia.org/wiki/Federation_(information_technology))
- [WebFinger](https://webfinger.net/) - 用户发现协议
- [ActivityPub](https://www.w3.org/TR/activitypub/) - 去中心化社交协议

---

*本文档是草稿，欢迎讨论和完善。*
