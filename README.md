# Astra-Pro — 教培 AI Agent 系统

基于通义千问（Qwen）的智能教辅后端服务，提供辅导答疑、作业批改、学习规划三类 AI Agent。

## 快速开始

```bash
# 安装依赖
pip install -e .

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入阿里云 DashScope API Key：
#   DASHSCOPE_API_KEY=sk-xxxxxxxx

# 启动服务
python -m astra_pro.main
# → http://localhost:8000/docs
```

## 使用示例

### 辅导答疑

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "因式分解 x²-9 怎么算？", "agent_type": "tutor"}'
```

```json
{
  "response": "x²-9 是平方差形式，公式 a²-b²=(a+b)(a-b)...",
  "agent_type": "tutor"
}
```

### 作业批改

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "homework_grader",
       "message": "题目：解方程 2x+3=7\n我的答案是 x=2，请批改"}'
```

### 学习规划

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "study_planner",
       "message": "高三，数学目前 90 分，目标 120，每天可用 2 小时"}'
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/chat` | POST | 向 Agent 发送消息 |
| `/api/v1/agents` | GET | 列出所有 Agent |
| `/api/v1/agents/{type}` | GET | 获取指定 Agent 详情 |
| `/api/v1/prompts` | GET | 列出所有提示词模板 |
| `/api/v1/tools` | GET | 列出可用工具 |
| `/metrics` | GET | Prometheus 指标 |

### Chat 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 用户输入 |
| `agent_type` | string | 否 | `tutor` / `homework_grader` / `study_planner`，默认 `tutor` |
| `history` | ChatMessage[] | 否 | 对话历史，每条含 `role` 和 `content` |

## 三类 Agent

| Agent | 类型名 | 适用场景 |
|-------|--------|---------|
| 学习辅导老师 | `tutor` | 学科答疑、概念解释、解题思路 |
| 作业批改老师 | `homework_grader` | 批改答案、指出错误、给出改进建议 |
| 学习规划师 | `study_planner` | 制定学习计划、推荐资源、时间安排 |

## 工具（Function Calling）

| 工具 | 功能 |
|------|------|
| `calculator` | 数学表达式计算，支持 `math` 模块函数 |
| `knowledge_base` | 按学科/分类查询知识点（数学/英语/物理） |

## 项目结构

```
astra-pro/
├── astra_pro/
│   ├── main.py                 # FastAPI 入口
│   ├── config/settings.py      # pydantic-settings 配置
│   ├── llm/client.py           # 通义千问客户端（重试、同步/异步、工具调用）
│   ├── agents/
│   │   ├── base.py             # Agent 基类（prompt 构建 → LLM 调用 → 响应处理）
│   │   └── tutor.py            # Tutor / HomeworkGrader / StudyPlanner
│   ├── prompts/templates.py    # System prompt 模板
│   ├── tools/
│   │   ├── calculator.py       # 数学计算工具
│   │   └── knowledge_base.py   # 知识点查询工具
│   ├── api/v1/
│   │   ├── chat.py             # POST /api/v1/chat
│   │   ├── agents.py           # GET /api/v1/agents
│   │   ├── prompts.py          # GET /api/v1/prompts
│   │   └── tools.py            # GET /api/v1/tools
│   ├── schemas/                # Pydantic 请求/响应模型
│   ├── logging/                # structlog 结构化日志
│   ├── metrics/                # Prometheus 指标收集
│   └── utils/rate_limiter.py   # 请求限流
├── tests/
│   ├── test_agents.py
│   ├── test_api.py
│   └── test_llm_client.py
├── .github/workflows/ci.yml
├── pyproject.toml
└── Dockerfile
```

## 技术栈

| 组件 | 选型 |
|------|------|
| 框架 | FastAPI + Uvicorn |
| LLM | 通义千问（DashScope），兼容 OpenAI SDK |
| 配置 | pydantic-settings（`.env` 文件） |
| 日志 | structlog（JSON 格式） |
| 监控 | prometheus-client + prometheus-fastapi-instrumentator |
| 重试 | tenacity（指数退避） |
| 限流 | 自研滑动窗口限流器 |

## 开发

```bash
pytest tests/ -v          # 运行测试
ruff check .              # 代码检查
black .                   # 格式化
mypy .                    # 类型检查
```

## 许可证

MIT
