# AI 模拟面试平台：从零学习版

这是一个按日推进的独立学习项目。现有完整面试系统作为参考，本仓库逐步实现自己的版本。

## 当前进度

- Day 1 已完成：亲自实现 `GET /health`，验证 HTTP 响应，创建本地提交并推送至 GitHub。
- 首次提交：`6a30d07`。远程仓库：[ai-interview-platform](https://github.com/ikkklkkl-alt/ai-interview-platform)。
- Day 2 必做部分已完成：返回岗位列表，用 `limit` 控制数量，限制参数在 1～10 之间。已验证，还没提交和推送；关键词筛选暂时没做。
- 尚未接入模型、数据库、用户系统或前端。

今天的练习见 [Day 2 任务单](docs/day-02.md)，基础三关已完成。回顾基础时可阅读 [Day 1 任务单](docs/day-01.md)。

## 第一版范围

面向 Python 后端方向，逐步实现：

1. 上传 TXT / Markdown 简历并确认解析画像。
2. 基于画像生成一组面试题。
3. 保存回答，展示分项评分和反馈依据。
4. 汇总报告，通过简单网页使用。
5. 加入登录、资源归属校验、关键测试，并部署到自己的服务器。

后续再根据掌握程度引入题库 RAG、后台任务、任务恢复与有限追问。

## 文件作用

| 文件 | 作用 |
| --- | --- |
| `pyproject.toml` | 声明项目信息、Python 范围和依赖 |
| `.python-version` | 指定本地开发使用的 Python 次版本 |
| `uv.lock` | 记录解析出的确切依赖版本，应提交到 Git |
| `.venv/` | 本机虚拟环境，不提交到 Git |
| `app/main.py` | 健康检查、岗位列表和查询参数校验 |
| `.gitignore` | 告诉 Git 哪些本机文件不应跟踪 |
| `docs/day-01.md` | 第一天的步骤和验收标准 |
| `docs/day-02.md` | 岗位列表、查询参数和参数校验练习 |
| `docs/learning-log.md` | 用自己的话填写学习记录 |

## 本地运行

在学习项目目录执行：

```bash
uv sync --locked
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

8001 被其他服务占用，目前使用 8002。打开：

- http://127.0.0.1:8002/health
- http://127.0.0.1:8002/interview-directions
- http://127.0.0.1:8002/docs

`/health` 返回健康检查结果，`/interview-directions?limit=2` 返回前两条岗位数据。根路径 `/` 没有定义接口，访问它返回 404。

## 学习方式

先描述输入、输出、失败情况，再自己实现。使用 AI 解释概念、审查实现、设计反例；记录哪些部分得到了辅助，以及自己如何验证。完成一个模块后，应能独立解释和修改它。
