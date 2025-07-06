# Multi-Agent 协作软件工程团队系统

## 项目简介
本项目基于多智能体（Multi-Agent）协作理念，模拟软件工程团队的自动化开发流程。系统集成了需求分析、代码生成、代码审查、代码整合、文档生成、测试等多种Agent，支持前后端分离开发，具备用户登录与权限管理、交互式Agent协作可视化等功能。

- **后端**：基于 FastAPI，模块化实现各类Agent与API服务。
- **前端**：原生 HTML/JavaScript/CSS，支持用户登录、Agent协作可视化。
- **用户系统**：支持登录、权限管理。
- **可扩展性**：每个Agent均为独立模块，便于扩展和维护。

## 主要功能
- 多Agent协作（需求分析、代码生成、审查、整合、文档、测试）
- 用户登录与权限管理
- 前后端分离，API接口自动生成文档
- 交互式Agent协作可视化界面

## 目录结构
```
multi-agent/
├── backend/                # FastAPI后端
│   ├── agents/             # 各类Agent模块
│   ├── api/                # API路由
│   ├── core/               # 核心配置
│   ├── services/           # 业务服务层
│   ├── models/             # 数据模型
│   └── auth/               # 认证与权限
├── frontend/               # 前端页面
│   ├── public/             # 静态资源
│   └── src/
│       ├── components/     # 组件
│       ├── pages/          # 页面
│       └── assets/         # 样式/图片
```

## 启动指南

### 1. 安装依赖
后端需安装 Python 3.8+，并安装依赖：
```bash
pip install fastapi uvicorn pydantic
```

### 2. 启动后端服务
```bash
uvicorn backend.main:app --reload
```
默认监听 http://127.0.0.1:8000

### 3. 启动前端页面
直接访问 [http://127.0.0.1:8000](http://127.0.0.1:8000) 即可体验前端页面与全部功能。

### 4. 访问与体验
- 访问首页，使用内置账号登录（如 admin/admin123）。
- 可体验多Agent协作可视化、用户登录、代码生成等功能。

## 账号信息（示例）
- 管理员：admin / admin123
- 普通用户：user / user123

## 备注
- 可根据实际需求扩展Agent能力、完善前端交互。
- 如需API文档，可访问 http://127.0.0.1:8000/docs

---
如有问题欢迎反馈！
