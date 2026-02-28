# AAP vs Google A2A

本文档对比 **Agent Address Protocol (AAP)** 与 **Google A2A** 协议。

> **注**：本文基于公开信息撰写，如有偏差请指正。

---

## 概述

| 特性 | AAP | A2A |
|------|-----|-----|
| **发起者** | 社区开源 (ThomasZta) | Google |
| **定位** | Agent 寻址与通信 | Agent 互操作协议 |
| **设计哲学** | 去中心化、Email+DNS+名片 | 任务分发、状态跟踪 |
| **状态** | v0.03.1 | 早期 (Draft) |

---

## 核心差异

### 1. 地址模型

**AAP**: 使用类似 Email 的全局唯一地址
```
ai:owner~role#provider
```
- 示例: `ai:tom~novel#molten.com`
- 类似于 Email，但专为 Agent 设计
- Provider 负责地址解析和管理

**A2A**: 使用 Agent ID + Server Endpoint
```json
{
  "agentId": "agent-123",
  "url": "https://agent.example.com"
}
```
- 需要预先知道 Agent 的 endpoint
- 无统一地址格式

---

### 2. 发现机制

**AAP**: 
- 通过 `GET /api/v1/resolve?address={aap}` 发现
- 类似 DNS，任何 Provider 可解析任何地址

**A2A**:
- 无内置发现机制
- 需要外部注册表或手动配置

---

### 3. 消息模型

**AAP**:
- Envelope + Payload 分离
- 支持 `public` (动态) 和 `private` (私信)
- 异步消息，存入 Inbox
- 简单直观

**A2A**:
- JSON-RPC 风格
- 任务流: `tasks/send` → `tasks/get`
- 支持流式响应 (streaming)
- 更复杂的状态机

---

### 4. 认证

**AAP**:
- Provider 自定义 (API Key、Bearer Token 等)
- v0.04 计划标准化

**A2A**:
- 基于 HTTP 认证
- 支持 OAuth 2.0

---

### 5. 生态

| 维度 | AAP | A2A |
|------|-----|-----|
| **Provider** | 任何域名 | 需要实现 A2A Server |
| **Adopters** | Molten, Agent Fiction 等 | Google 生态 |
| **SDK** | Python SDK | 官方 SDK (JS, Python) |
| **文档** | 开源社区驱动 | Google 官方 |

---

## 对比总结

| 场景 | 推荐协议 |
|------|----------|
| Agent 身份标识 (类似 Email) | **AAP** |
| 去中心化发现 | **AAP** |
| 简单消息传递 | **AAP** |
| 复杂任务流/状态跟踪 | **A2A** |
| 与 Google 生态集成 | **A2A** |
| 开放标准/社区驱动 | **AAP** |

---

## 为什么 AAP 仍然有价值

1. **更简单**: 地址格式直观，类似 Email + DNS
2. **去中心化**: 无需中央注册表，任何人都能搭建 Provider
3. **专注于身份**: A2A 侧重任务分发，AAP 侧重 Agent 寻址
4. **生态互补**: AAP 可与 A2A 等协议共存

---

## 相关链接

- **AAP**: https://github.com/thomaszta/aap-protocol
- **A2A**: https://github.com/google/a2a
- **MCP (Anthropic)**: https://modelcontextprotocol.io

---

*本文档将持续更新。如有错误，请提交 Issue 或 PR 修正。*
