# Agent Demo (Python)

一个“最小但结构严谨”的本地 Agent Demo：
- 将推理函数封装为可注册 tools
- 用 planner 自动选择和串联 tools
- 通过状态机执行多步骤任务
- 带状态持久化、JSONL 事件日志、错误处理

## 目录结构

```text
agent_demo/
  app.py
  state.py
  tools.py
  executor.py
  planner.py
  workflow.py
  storage.py
  README.md
```

## 环境要求

- Python 3.10+

## 运行方式

在仓库根目录执行：

```bash
cd agent_demo
python app.py
```

运行后会自动：
1. 生成一个假图片文件 `sample_data/bearing_defect_sample.jpg`
2. 创建一个任务并进入 Agent 工作流
3. 顺序执行 `detect_defect -> classify_part`
4. 输出最终状态 JSON

## 运行产物

每个任务会在 `runs/<task_id>/` 下产生：
- `state.json`：最新完整状态
- `tool_events.jsonl`：工具调用事件流（每行一个事件）

## 模块职责

- `tools.py`：工具定义与注册（name/description/parameters/fn）
- `executor.py`：`run_tool()` 执行层（参数校验、异常捕获、统一返回）
- `planner.py`：FakePlanner（可替换为 LLM function calling）
- `workflow.py`：状态机主循环 `INIT -> PLAN -> RUN_TOOL -> VALIDATE -> ... -> SUMMARIZE -> DONE`
- `state.py`：`AgentState`、`ToolEvent`、history 事件模型
- `storage.py`：JSON/JSONL 持久化
- `app.py`：本地可运行 demo 入口

## 可扩展建议

- **替换 Planner**：实现新的 `BasePlanner` 子类（对接 OpenAI function calling / Agents SDK）
- **新增 Tools**：在 `tools.py` 新增 `ToolSpec` 并注册到 `TOOL_REGISTRY`
- **增加重试与 Guardrails**：在 `workflow.py` 的 RUN_TOOL 分支加入 retry/backoff/策略拦截
- **多 Agent 协作**：将 `AgentWorkflow` 提升为 orchestrator，按子任务路由给不同 planner/tool 集合

## 快速自检

```bash
cd agent_demo
python app.py
python -m py_compile *.py
```
