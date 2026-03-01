# AAP 项目备忘录

> 记录关键决策、架构设计、待办事项

---

## 1. 项目愿景

**目标**: 建立 AI Agent 的寻址与通信开放协议

```
让任何 Agent 都能发现和联系其他 Provider 上的 Agent
```

### 核心场景

| 场景 | 状态 | 说明 |
|------|------|------|
| 已知地址的跨 Provider 通信 | ✅ 可闭环 | 核心功能可用 |
| 未知地址的 Agent 发现 | ❌ 待完善 | 需要 Provider 目录 |
| 新 Provider 加入生态 | ⚠️ 待完善 | 需要注册机制 |

---

## 2. 协议版本

| 版本 | 状态 | 说明 |
|------|------|------|
| v0.02 | 已发布 | 初始协议 |
| v0.03 | 已发布 | 可选功能 (错误码、content_type) |
| v0.04 | 开发中 | 跨 Provider 发现 (域名直连) |
| v0.05 | 规划中 | DNS 发现 |
| v0.06 | 规划中 | 信任机制 |
| v0.07 | 规划中 | 种子节点 |
| v0.08 | 规划中 | P2P 网络 (最终目标) |

---

## 3. 技术架构

### 3.1 地址格式

```
ai:owner~role#provider
```

- `owner`: 身份标识 (最长 64 字符)
- `role`: 角色类型 (最长 64 字符)
- `provider`: 域名 (最长 253 字符)

### 3.2 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/agent/register` | POST | 注册 Agent |
| `/api/v1/resolve` | GET | 解析地址 |
| `/api/v1/inbox/{owner_role}` | POST | 收消息 |
| `/api/v1/inbox` | GET | 取消息 (需认证) |
| `/api/v1/providers/info` | GET | Provider 信息 |

### 3.3 SDK

- Python SDK: `sdk/python/` (v0.1.1)
- 状态: Alpha

### 3.4 Provider 模板

- Python/Flask: `provider/python-flask/`
- 状态: 可用

---

## 4. 安全与健壮性

### 4.1 已修复 (P0)

| 问题 | 修复 |
|------|------|
| 输入验证不足 | 添加长度限制和字符验证 |
| API Key 不安全 | 使用 secrets.token_urlsafe |
| 认证缺失 | inbox 需 API Key |

### 4.2 已修复 (P1)

| 问题 | 修复 |
|------|------|
| 消息幂等性 | X-Idempotency-Key 支持 |
| 错误码不统一 | 遵循 v0.03 规范 |
| 网络不稳定 | SDK 添加重试+指数退避 |

### 4.3 待解决 (P2)

- 版本协商
- 消息状态 (已读/未读)
- 线程安全

---

## 5. 关键决策

### 5.1 v0.04 互联方案

**选择**: 域名直连 (D) + 预留扩展

**原因**:
- 最简单，可立刻开始
- 预留 DNS 接口，未来可叠加
- 每阶段独立可用

**演进**:
```
v0.04: 域名直连
v0.05: 叠加 DNS
v0.06: 信任机制
v0.07: 种子节点
v0.08: P2P 网络
```

### 5.2 OpenClaw Skill

**决策**: 先提供 skill.md，不提交到 openclaw/skills

**原因**:
- 协议还在快速迭代中
- 等待 v0.04 稳定后再提交
- 先让社区讨论验证

---

## 6. 生态现状

### 6.1 Adopters

| 应用 | 说明 |
|------|------|
| Molten.it.com | AI 社交平台 (首个) |
| Agent Fiction Arena | AI 小说创作平台 |

### 6.2 待完善

- Provider 目录/注册
- 更多 Adopters
- SDK 测试
- 文档完善

---

## 7. 待办事项

### 短期 (Phase 1: 稳定可用) ✅

- [x] 发布 SDK 到 PyPI
- [x] 完善 SDK README
- [x] 添加单元测试
- [x] 验证跨 Provider 通信
- [x] 添加 CI/CD 发布流程

### 中期 (Phase 2: Provider 目录)

- [ ] 创建 Provider 注册服务
- [ ] SDK 添加 list_providers()
- [ ] 完善 v0.04 Stage 2 (DNS)

### 长期 (Phase 3: Agent 发现)

- [ ] Agent 搜索功能
- [ ] 跨 Provider 发现
- [ ] 信任机制

---

## 8. SDK 发布 (PyPI)

### 发布状态

| 项目 | 状态 |
|------|------|
| PyPI | ✅ 已发布 |
| 版本 | 0.1.1 |
| 包名 | aap-sdk |
| 测试 | 24 个通过 |

### 安装命令

```bash
pip install aap-sdk
```

### PyPI 页面

https://pypi.org/project/aap-sdk/

### CI/CD

- 测试: `.github/workflows/sdk-test.yml`
- 发布: `.github/workflows/sdk-publish.yml`

### 发布流程

1. 更新版本号 (pyproject.toml + __init__.py)
2. 提交并推送
3. 创建 GitHub Release
4. CI 自动发布到 PyPI

---

## 9. 风险与挑战

| 风险 | 影响 | 应对 |
|------|------|------|
| Provider 互联信任 | 高 | v0.05+ 解决 |
| 国内访问 GitHub | 低 | 考虑镜像 |
| 生态分散 | 中 | 推动 Adopters |
| 协议迭代快 | 中 | 保持向后兼容 |

---

## 10. 相关资源

- GitHub: https://github.com/thomaszta/aap-protocol
- PyPI: https://pypi.org/project/aap-sdk/
- 规范: `spec/aap-v0.03.md`
- v0.04 草稿: `spec/aap-v0.04-discovery.md`
- OpenClaw Skill: `skill.md`

---

## 10. 讨论记录

> 记录关键讨论和结论

### 10.1 SDK 作用

**问题**: SDK 给谁用？

**结论**:
- 平台开发者：用 SDK 接入 AAP
- 第三方应用：用 SDK 开发
- Agent 本身：可以不用，平台内置

### 10.2 OpenClaw 集成

**问题**: 是否现在提交 skill 到 openclaw/skills？

**结论**:
- 暂不提交
- 等 v0.04 稳定后再提交
- 先让 Agent 直接读取 skill.md 学习

### 10.3 v0.04 方案选择

**问题**: 如何选择互联方案？

**结论**:
- 先用最简单的域名直连
- 每阶段可独立演进
- 预留扩展接口

---

*最后更新: 2026-03-01*
