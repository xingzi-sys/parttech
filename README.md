# PartTech - 智算生态合作商管理系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

智算生态合作商管理系统，用于管理智算行业的合作商信息，包括企业、联系人、产品、项目、合同等模块。

## 功能模块

| 模块 | 说明 |
|------|------|
| 仪表盘 | 合作商分布、项目漏斗、合同趋势、资质预警、动态流 |
| 企业管理 | 合作商基本信息、类型、等级、状态、标签 |
| 联系人管理 | 关联企业的关键联系人、角色、决策链 |
| 产品管理 | 合作商的主要产品、类别、适配场景 |
| 合作项目管理 | 项目阶段、预算、负责人、协同人 |
| 合同管理 | 合同信息、付款里程碑、附件上传 |
| 跟进记录 | 交流/拜访记录时间线 |
| 商务条件库 | 各厂家的商务条款（垫资/返点/账期等） |
| 资质证照管理 | 资质到期预警 |
| 用户管理 | RBAC权限管理 |

## 技术栈

- **后端**: Flask + SQLAlchemy + Flask-JWT-Extended
- **数据库**: SQLite (开发) / MySQL (生产)
- **前端**: Vue 3 + Element Plus + Pinia + Vue Router
- **构建**: Vite

## 快速开始

### 后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python seed.py

# 启动服务
python run.py
```

后端运行在 http://localhost:5000

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:5173

### 启停脚本

```bash
# 启动所有服务
./parttech.sh start

# 查看状态
./parttech.sh status

# 停止服务
./parttech.sh stop

# 重启服务
./parttech.sh restart
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
| 部门管理员 | manager | manager123 |
| 项目经理 | user | user123 |

## 项目结构

```
PartTech/
├── backend/                 # Flask后端
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── api/            # REST API接口
│   │   └── utils/          # 工具函数
│   ├── seed.py             # 初始化数据
│   └── run.py              # 启动入口
├── frontend/               # Vue3前端
│   └── src/
│       ├── views/          # 页面组件
│       ├── api/            # API调用封装
│       ├── stores/         # Pinia状态管理
│       └── router/         # 路由配置
├── parttech.sh             # 启停脚本
└── README.md
```

## 合作商类型

- 机房设备
- 智算平台
- 行业产品
- 整体方案
- 资金方
- 其他

## 合作等级

- 战略
- 核心
- 普通
- 潜在

## 许可证

MIT License