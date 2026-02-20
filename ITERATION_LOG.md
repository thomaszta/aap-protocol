# AAP Protocol Iteration Log

## v0.03 迭代记录

**日期**: 2026-02-20  
**状态**: 已完成并推送至 GitHub

---

### 完成内容

#### 1. 协议规范
- 创建 `spec/aap-v0.03.md`
- 添加可选功能：
  - 结构化错误响应 (Error codes)
  - content_type 字段
  - Capabilities 端点

#### 2. 文档更新
- 更新 `CHANGELOG.md`
- 更新 `spec/README.md`
- 更新 `CONTRIBUTING.md` (修复合并冲突)
- 更新 `README.md` (Badge 和链接)
- 更新 `docs/provider-guide.md`
- 更新 `docs/consumer-guide.md`
- 更新 `docs/address-uniqueness.md`

#### 3. 示例代码
- 修复 `examples/python/aap_address.py` 合并冲突
- 修复 `examples/javascript/README.md` 合并冲突
- 简化 `examples/python/README.md`
- 简化 `examples/README.md`
- 更新所有示例中的版本号引用

#### 4. Adopters
- 更新 `adopters/README.md`
- 更新 `adopters/molten-it-com.md`

#### 5. Issue Templates
- 更新 `.github/ISSUE_TEMPLATE/bug-report.md`
- 更新 `.github/ISSUE_TEMPLATE/question.md`

---

### 提交记录

| Commit | Description |
|--------|-------------|
| `0fbdacf` | spec: add v0.03 with optional error codes, content_type, and capabilities |
| `7d3a22f` | docs: update documentation to reflect v0.03 |
| `d7c9dca` | docs: update spec references to v0.03 across all files |

---

## v0.04 待办事项

### 优先级：高

- [ ] **认证标准化**
  - 定义 `auth_methods` 字段
  - 定义认证失败的标准错误码
  - 凭证获取机制 (acquire_url)

### 优先级：中

- [ ] **ACK 消息确认**
  - POST 响应增强 (包含 ack_id)
  - 状态查询端点 (可选)

- [ ] **消息元数据**
  - priority 优先级字段
  - expires_at 过期时间

### 优先级：低

- [ ] E2EE 密钥交换细节
- [ ] 批量操作支持
- [ ] Rate Limiting 标准化

---

### 设计原则

1. **先兼容再扩展** - 不破坏现有实现 (如 Molten)
2. **最小可行** - 每次只加最关键的功能
3. **可选不强制** - 现有实现不受影响
4. **利于生态** - 考虑实际应用场景

---

### 参考资源

- **当前规范**: [spec/aap-v0.03.md](spec/aap-v0.03.md)
- **上一版本**: [spec/aap-v0.02.md](spec/aap-v0.02.md)
- **GitHub**: https://github.com/thomaszta/aap-protocol
- **讨论区**: https://github.com/thomaszta/aap-protocol/discussions

---

### 注意事项

1. Molten 当前不可用 (SSL 连接问题)，需确认服务恢复后再测试
2. v0.03 已完全向后兼容，Molen 无需改动
3. 每次迭代前先与现有 Adopter 沟通影响
