# AAP 项目：Mac mini 本地提交与 Git 同步说明

## Mac mini 上的增强提交（OpenClaw 创建）

以下提交在 **Mac mini 本地** 创建，包含对 GitHub 仓库配置与文档的增强，**尚未推送到 origin**（或已推送则本机可拉取同步）。

```
commit 6b4f553c12b3edb8bebd815e0040e1a54e9c26f4
Author: openclaw openclaw@192.168.10.242
Date:   Sun Feb 8 11:22:49 2026 +0800

feat: enhance GitHub repository configuration and badges

- Add comprehensive GitHub configuration (CODEOWNERS, FUNDING, SECURITY)
- Implement CI/CD workflow with linting and validation
- Add issue and PR templates for better community management
- Enhance README with badges and improved documentation
- Create detailed CONTRIBUTING.md with contribution guidelines
- Add code examples in Python and JavaScript
- Improve project structure and developer experience
```

### 该提交涉及的文件（15 个文件，+1928 行）

| 路径 | 说明 |
|------|------|
| `.github/CODEOWNERS` | 代码责任人 |
| `.github/FUNDING.yml` | 赞助/资金链接 |
| `.github/SECURITY.md` | 安全策略与漏洞报告 |
| `.github/ISSUE_TEMPLATE/feature-request.md` | 功能请求模板 |
| `.github/ISSUE_TEMPLATE/question.md` | 提问模板 |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR 模板（增强） |
| `.github/labels.yml` | Issue/PR 标签配置 |
| `.github/markdown-link-check.json` | Markdown 链接检查配置 |
| `.github/workflows/ci.yml` | CI/CD：lint 与校验 |
| `CONTRIBUTING.md` | 贡献指南（增强） |
| `README.md` | 徽章与文档增强 |
| `examples/README.md` | 示例总览 |
| `examples/javascript/README.md` | JavaScript 示例说明 |
| `examples/python/README.md` | Python 示例说明 |
| `examples/python/aap_address.py` | Python AAP 地址示例代码 |

---

## 如何用该提交提交到 Git（推荐流程）

### 方式一：从 Mac mini 直接推送到 GitHub（推荐）

在 **Mac mini** 上，进入 aap 仓库目录后执行：

```bash
cd /path/to/aap   # 替换为 Mac mini 上 aap 仓库的实际路径

# 确认当前在包含 6b4f553 的分支上
git log -1 --oneline
# 应看到: 6b4f553 feat: enhance GitHub repository configuration and badges

# 推送到 origin
git push origin main
```

推送成功后，**本机（NewMolten）** 或其他克隆只需：

```bash
cd /Users/maomaoplanet/AIProjects/NewMolten/aap
git pull origin main
```

即可与 Mac mini 上的内容一致，并用于后续提交。

### 方式二：本机没有 Mac mini 的提交，需要从 Mac mini 拿代码

若本机 aap 仓库没有 commit 6b4f553，只能从 Mac mini 拿一次代码：

1. **在 Mac mini 上**：先 `git push origin main`（若尚未推送）。
2. **在本机**：`cd aap && git pull origin main`。

或通过 U 盘/网络把 Mac mini 上的 `aap` 目录拷到本机，覆盖本机 `NewMolten/aap`（注意保留本机未提交的修改前先备份），再在本机 `git push origin main`（若 Mac mini 未推送）。

---

## 小结

- **Mac mini 上的 6b4f553** 已包含完整的 GitHub 配置、CI、示例和文档增强，**可以用来提交 git**。
- **推荐**：在 Mac mini 上执行 `git push origin main`，在其他克隆中 `git pull origin main` 同步。
- 同步后，本机 aap 目录将出现 `examples/`、`.github/workflows/ci.yml`、`CODEOWNERS`、`FUNDING.yml`、`SECURITY.md` 等，与 Mac mini 一致。
