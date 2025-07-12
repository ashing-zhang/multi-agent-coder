# Multi-Agent 协作平台 API 文档

## 概述

Multi-Agent 协作平台提供了一套完整的API，支持多种AI Agent的协作开发。每个Agent都有独立的API端点，支持流式响应和会话历史记录。

## 认证

所有API都需要Bearer Token认证。获取token的方式：

1. 注册用户：`POST /auth/register`
2. 登录获取token：`POST /auth/token`

在请求头中添加：
```
Authorization: Bearer <your_token>
```

## API 端点

### 1. 认证相关

#### 用户注册
- **端点**: `POST /auth/register`
- **描述**: 注册新用户
- **请求体**:
```json
{
    "username": "string",
    "password": "string",
    "email": "string",
    "full_name": "string"
}
```

#### 用户登录
- **端点**: `POST /auth/token`
- **描述**: 用户登录获取访问令牌
- **请求体**:
```json
{
    "username": "string",
    "password": "string"
}
```
- **响应**:
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

#### 获取用户信息
- **端点**: `GET /auth/userinfo`
- **描述**: 获取当前用户信息（包含API Key状态）
- **认证**: 需要Bearer Token
- **响应**:
```json
{
    "username": "string",
    "email": "string",
    "full_name": "string",
    "api_key": "string"
}
```

### 2. Agent 相关

#### 获取Agent列表
- **端点**: `GET /agent/list`
- **描述**: 获取所有可用的Agent类型
- **认证**: 需要Bearer Token
- **响应**:
```json
[
    "需求分析Agent",
    "代码生成Agent", 
    "代码审查Agent",
    "代码整合Agent",
    "文档Agent",
    "测试Agent"
]
```

### 3. 需求分析 Agent

#### 流式需求分析
- **端点**: `POST /requirements/stream`
- **描述**: 分析用户需求并生成详细的需求文档
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "description": "string"
}
```
- **响应**: 流式文本响应
- **功能**: 自动保存到会话历史

### 4. 文档生成 Agent

#### 流式文档生成
- **端点**: `POST /agent/doc/stream`
- **描述**: 为代码生成README文档
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "requirement": "string"
}
```
- **响应**: 流式文本响应
- **功能**: 自动保存到会话历史

### 5. 代码生成 Agent

#### 流式代码生成
- **端点**: `POST /agent/coder/stream`
- **描述**: 根据需求描述生成代码
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "requirement": "string"
}
```
- **响应**: 流式文本响应
- **功能**: 自动保存到会话历史

### 6. 代码审查 Agent

#### 流式代码审查
- **端点**: `POST /agent/reviewer/stream`
- **描述**: 对代码进行审查并提供优化建议
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "requirement": "string"
}
```
- **响应**: 流式文本响应
- **功能**: 自动保存到会话历史

### 7. 测试生成 Agent

#### 流式测试生成
- **端点**: `POST /agent/test/stream`
- **描述**: 为代码生成测试用例
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "requirement": "string"
}
```
- **响应**: 流式文本响应
- **功能**: 自动保存到会话历史

### 8. 代码整合 Agent

#### 流式代码整合
- **端点**: `POST /agent/finalizer/stream`
- **描述**: 根据代码和优化建议修改代码
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "requirement": "string",
    "suggestions": "string"
}
```
- **响应**: 流式文本响应
- **功能**: 自动保存到会话历史

### 9. Agent Workflow

#### 流式工作流执行
- **端点**: `POST /workflow/stream`
- **描述**: 端到端执行完整的Agent协作工作流
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "requirement": "string"
}
```
- **响应**: 流式文本响应
- **功能**: 自动保存到会话历史

### 10. 会话历史

#### 获取历史消息
- **端点**: `GET /messages/`
- **描述**: 获取用户的历史会话记录（最新10个会话）
- **认证**: 需要Bearer Token
- **响应**:
```json
[
    {
        "session_id": 1,
        "session_name": "string",
        "messages": [
            {
                "id": 1,
                "content": "string",
                "role": "user|assistant",
                "created_at": "datetime"
            }
        ]
    }
]
```

### 11. API Key 管理

#### 设置API Key
- **端点**: `POST /set_key`
- **描述**: 设置用户的DeepSeek API Key
- **认证**: 需要Bearer Token
- **请求体**:
```json
{
    "api_key": "string"
}
```

## 错误处理

所有API都遵循标准的HTTP状态码：

- `200`: 成功
- `400`: 请求参数错误
- `401`: 未认证或认证失败
- `404`: 资源不存在
- `500`: 服务器内部错误

错误响应格式：
```json
{
    "detail": "错误描述"
}
```

## 流式响应

所有以`/stream`结尾的端点都支持流式响应：

1. 响应类型为 `text/plain`
2. 数据以流式方式返回
3. 客户端需要处理流式数据
4. 响应完成后自动保存到数据库

## 会话管理

- 每次调用流式API都会创建新的会话
- 会话名称自动生成（基于输入内容的前30个字符）
- 用户消息和AI回复都会保存到数据库
- 支持查看历史会话记录

## 使用示例

### Python 示例

```python
import requests

# 1. 登录获取token
login_data = {"username": "user", "password": "pass"}
response = requests.post("http://localhost:8000/auth/token", data=login_data)
token = response.json()["access_token"]

# 2. 调用代码生成API
headers = {"Authorization": f"Bearer {token}"}
data = {"requirement": "创建一个Python函数来计算斐波那契数列"}

response = requests.post(
    "http://localhost:8000/agent/coder/stream",
    json=data,
    headers=headers,
    stream=True
)

# 3. 处理流式响应
for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
    if chunk:
        print(chunk, end='')
```

### JavaScript 示例

```javascript
// 1. 登录获取token
const loginResponse = await fetch('/auth/token', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'username=user&password=pass'
});
const {access_token} = await loginResponse.json();

// 2. 调用代码生成API
const response = await fetch('/agent/coder/stream', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        requirement: '创建一个Python函数来计算斐波那契数列'
    })
});

// 3. 处理流式响应
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value, {stream: true});
    console.log(chunk);
}
```

## 注意事项

1. 所有API都需要有效的DeepSeek API Key才能正常工作
2. 流式响应可能需要较长时间，请确保客户端有足够的超时设置
3. 会话历史记录限制为每个用户最新的10个会话
4. API Key存储在数据库中，请确保数据库安全
5. 建议在生产环境中使用HTTPS 