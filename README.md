# Astra-Pro - 生产级 AI 代理系统

一个生产就绪的 AI 代理系统模板，具备全面的工程能力。

**当前使用模型：通义千问（Qwen）**

## 特性

- **FastAPI 服务** - 带有 OpenAPI 文档的 RESTful API
- **结构化日志** - 带上下文的 JSON 日志
- **指标与监控** - Prometheus 集成
- **提示词管理** - 版本控制的提示词
- **工具调用** - 函数调用支持
- **速率限制** - 请求限流
- **健康检查** - 存活和就绪探针
- **单元测试** - 全面的测试覆盖

## 快速开始

```bash
# 1. 克隆项目
cd astra-pro

# 2. 安装依赖
pip install -e .

# 3. 配置环境
cp .env.example .env
# 编辑 .env 文件添加你的 DashScope API 密钥
# DASHSCOPE_API_KEY=your-api-key-here

# 4. 运行服务器
python -m astra_pro.main

# 5. 访问 API
# OpenAPI 文档: http://localhost:8000/docs
# 健康检查: http://localhost:8000/health
```

## 项目结构

```
astra-pro/
├── astra_pro/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config/              # 配置
│   │   ├── __init__.py
│   │   └── settings.py      # Pydantic 设置
│   ├── llm/                 # LLM 集成
│   │   ├── __init__.py
│   │   └── client.py        # 带重试的 LLM 客户端
│   ├── agents/              # 代理实现
│   │   ├── __init__.py
│   │   ├── base.py          # 代理基类
│   │   └── analyzer.py      # 示例分析代理
│   ├── prompts/             # 提示词模板
│   │   ├── __init__.py
│   │   └── templates.py     # 版本化提示词
│   ├── tools/               # 工具实现
│   │   ├── __init__.py
│   │   └── calculator.py    # 示例工具
│   ├── logging/             # 日志配置
│   │   ├── __init__.py
│   │   └── setup.py         # Structlog 设置
│   ├── metrics/             # 监控
│   │   ├── __init__.py
│   │   └── collector.py     # Prometheus 指标
│   ├── api/                 # API 端点
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py      # 聊天端点
│   │   │   └── agents.py    # 代理管理
│   │   └── deps.py          # 依赖
│   ├── schemas/             # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── request.py       # 请求模式
│   │   └── response.py      # 响应模式
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── rate_limiter.py  # 速率限制
├── tests/                   # 单元测试
│   ├── __init__.py
│   ├── test_llm_client.py
│   ├── test_agents.py
│   └── test_api.py
├── .env.example             # 环境变量模板
├── .gitignore
├── pyproject.toml           # 依赖配置
└── README.md
```

## API 端点

| 端点 | 方法 | 描述 |
|----------|--------|-------------|
| `/health` | GET | 健康检查 |
| `/api/v1/chat` | POST | 聊天完成 |
| `/api/v1/agents` | GET | 列出代理 |
| `/api/v1/agents/{name}` | GET | 获取代理信息 |
| `/api/v1/prompts` | GET | 列出提示词 |
| `/metrics` | GET | Prometheus 指标 |

## 开发

```bash
# 运行测试
pytest tests/ -v

# 热重载运行
uvicorn astra_pro.main:app --reload

# 代码检查
ruff check .

# 代码格式化
black .

# 类型检查
mypy .
```

## 许可证

MIT