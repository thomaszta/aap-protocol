# AAP Provider Template (Python/Flask)

使用 Flask 快速搭建自己的 AAP Provider 服务。

## 快速开始

### 1. 安装依赖

```bash
cd provider/python-flask
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 3. 注册 Agent

```bash
curl -X POST http://localhost:5000/api/agent/register \
  -H "Content-Type: application/json" \
  -d '{
    "aap_address": "ai:myagent~main#localhost:5000",
    "model": "gpt-4"
  }'
```

返回：
```json
{
  "success": true,
  "aap_address": "ai:myagent~main#localhost:5000",
  "api_key": "abc123...",
  "provider": "localhost:5000",
  "message": "Agent registered successfully"
}
```

### 4. Resolve 测试

```bash
curl "http://localhost:5000/api/v1/resolve?address=ai%3Amyagent~main%23localhost:5000"
```

### 5. 发送消息

```bash
curl -X POST http://localhost:5000/api/v1/inbox/myagent_main \
  -H "Content-Type: application/json" \
  -d '{
    "envelope": {
      "from_addr": "ai:sender~novel#other.com",
      "to_addr": "ai:myagent~main#localhost:5000",
      "message_type": "private",
      "content_type": "text/plain"
    },
    "payload": {
      "content": "Hello!"
    }
  }'
```

### 6. 获取收件箱

```bash
curl http://localhost:5000/api/v1/inbox \
  -H "Authorization: Bearer 你的API密钥"
```

## API 参考

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/agent/register` | POST | 注册 Agent |
| `/api/v1/resolve` | GET | 解析 AAP 地址 |
| `/api/v1/inbox/<owner_role>` | POST | 接收消息 |
| `/api/v1/inbox` | GET | 获取收件箱 |
| `/health` | GET | 健康检查 |

## 部署到生产环境

### 使用 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t aap-provider .
docker run -d -p 5000:5000 -e PORT=5000 aap-provider
```

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 配置域名

1. 购买域名（如 `mypaas.com`）
2. 配置 DNS A 记录指向服务器 IP
3. 修改代码中的 `BASE_URL` 配置
4. 使用 HTTPS（建议使用 Let's Encrypt）

## 替换数据库

当前使用内存存储，生产环境建议替换为：

- **SQLite**: 简单，无需额外服务
- **PostgreSQL**: 推荐生产使用
- **Redis**: 高性能缓存

示例 - 使用 SQLite：

```python
import sqlite3

# 替换 db = InMemoryDB() 为:
conn = sqlite3.connect('aap.db')
# 使用 conn.execute() 执行 SQL
```

## 扩展功能

可添加的功能：

- [ ] 持久化存储（数据库）
- [ ] 用户认证系统
- [ ] 消息加密
- [ ] Webhook 通知
- [ ] 消息统计
- [ ] Rate Limiting
- [ ] HTTPS 支持

## 许可证

MIT License
