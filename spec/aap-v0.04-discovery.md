# AAP v0.04 - Provider 互联方案 (草案)

> **状态**: 草稿 v0.2 - 收集方案中  
> **目标**: 实现去中心化的 Provider 互联发现

---

## 背景

当前 AAP 协议的问题：
- Agent 知道对方地址，但不知道 Provider 在哪
- 跨 Provider 发现需要手动配置
- 没有信任机制

目标：让任何 Provider 上的 Agent 都能发现和联系其他 Provider 上的 Agent。

---

## 方案对比

### 方案 A: DNS 模式 (类 Email)

**核心思路**: 借鉴 Email，用 DNS 做发现

```
地址: ai:bob~main#provider2.com
     ↓
DNS 查询 provider2.com 的 SRV 记录
     ↓
获取 API 端点
```

**优点**:
- 无需额外基础设施
- 已有成熟技术
- 去中心化（DNS 本身就是去中心的）

**缺点**:
- 需要 Provider 配置 DNS
- 国内 DNS 解析可能有问题

**DNS 记录格式**:
```dns
_aap-resolve._tcp.provider.com.  IN SRV 10 5 443 api.provider.com.
_aap-inbox._tcp.provider.com.   IN SRV 10 5 443 api.provider.com.
```

---

### 方案 B: 引导种子节点

**核心思路**: 官方维护几个种子节点，Provider 启动时连接获取列表

```
种子节点 (seed1.aap-protocol.org)
         ↑
    Provider 启动时拉取
         ↓
    本地缓存 Provider 列表
         ↓
    定期同步更新
```

**优点**:
- 实现相对简单
- 可以控制质量

**缺点**:
- 有中心化风险
- 种子节点故障影响全局

---

### 方案 C: 分布式网络 (类 BitTorrent)

**核心思路**: Provider 之间互相发现，形成 P2P 网络

```
Provider A ←→ Provider B ←→ Provider C
    ↑              ↑
  互相广播      互相广播
  已知节点      已知节点
```

**优点**:
- 完全去中心化
- 无单点故障

**缺点**:
- 实现复杂
- 需要同步机制

---

### 方案 D: 域名直连

**核心思路**: 最简单，地址本身就包含 Provider 域名

```
ai:bob~main#provider2.com
               ↑
          直接解析这个域名
          https://provider2.com/api/...
```

**优点**:
- 最简单，无需额外机制
- Provider 负责自己的域名解析

**缺点**:
- 无法知道 Provider 列表
- 无法做信任评估

---

## 待讨论问题

### 1. 最小可行方案是什么？

选项：
- A + D 组合：DNS 发现 + 直连（无需额外基础设施）
- A + B 组合：DNS 发现 + 种子辅助（更可靠）

### 2. 种子节点谁维护？

- 官方维护？
- 社区维护？
- 多方轮流？

### 3. 信任机制怎么做？

- DNS 域名所有权验证？
- Provider 互相评分？
- 官方白名单？

### 4. 认证怎么做？

- 沿用 API Key？
- JWT Token？
- 双方协商？

### 5. 国内环境考虑

- 是否需要国内镜像？
- DNS 被墙怎么办？

---

## 建议讨论流程

1. **确定最小可行方案** - 先实现能用的
2. **讨论细节** - API 格式、认证方式
3. **原型实现** - 小范围测试
4. **迭代优化** - 根据反馈改进

---

## 相关资源

- Email: DNS MX 记录, SMTP 协议
- Mastodon/Fediverse: ActivityPub 联邦
- XMPP: 即时通讯去中心化协议
- ActivityPub: W3C 去中心化社交标准

---

*欢迎讨论：https://github.com/thomaszta/aap-protocol/discussions*
