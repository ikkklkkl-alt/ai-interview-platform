# AI 模拟面试平台：从零学习版

这是一个按日推进的独立学习项目。现有完整面试系统作为参考，本仓库逐步实现自己的版本。

## 当前进度

- Day 1 已完成：亲自实现 `GET /health`，验证 HTTP 响应，创建本地提交并推送至 GitHub。
- 首次提交：`6a30d07`。远程仓库：[ai-interview-platform](https://github.com/ikkklkkl-alt/ai-interview-platform)。
- Day 2 必做部分已完成并推送（`8a33bc4`）：岗位列表、`limit` 数量限制和 1～10 的范围校验。关键词筛选暂时没做。
- Day 3 已完成并推送（`965c27e`）：独立脚本读取配置，用 `httpx` 调用真实 DeepSeek 模型，打印回答、结束原因和 Token 用量，并处理常见请求错误。
- Day 4 已完成并推送（`b3c1dce`）：模型以 JSON 格式生成面试题，使用 Pydantic 校验字段，并处理响应结构异常、空正文、截断和解析失败。
- Day 5 已完成并推送（`26eacc0`、`f404d29`）。5 个字段校验测试和 3 个模型调用流程测试全部通过。
- Day 6 已提取 `parse_question_content()` 并在 `main()` 中使用。新增 3 个测试直接验证合法题目、正文解码失败和非法难度，全套测试结果为 `11 passed`。
- 目前 Web 接口尚未接入模型、数据库、用户系统或前端。

今天的练习见 [Day 6 任务单](docs/day-06.md)。回顾之前的内容可阅读 [Day 1](docs/day-01.md)、[Day 2](docs/day-02.md)、[Day 3](docs/day-03.md)、[Day 4](docs/day-04.md) 和 [Day 5](docs/day-05.md)。

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
| `scripts/first_model_call.py` | 独立调用 DeepSeek，读取回答与用量，处理超时、连接及 HTTP 状态错误 |
| `scripts/structured_question.py` | 调用模型生成 JSON 面试题，检查响应并校验题目、难度和知识点 |
| `scripts/__init__.py` | 将学习脚本目录作为包，供测试导入 |
| `tests/conftest.py` | 准备假配置，默认阻止测试直接发送模型请求 |
| `tests/test_question_schema.py` | 5 个字段校验测试：正确样例、非法难度、缺少字段、空白题目、多余字段 |
| `tests/test_model_call.py` | 模拟成功响应、非法 JSON 和截断；检查请求参数、输出和退出提示 |
| `tests/test_question_content.py` | 直接验证解析函数返回的题目对象和两类异常 |
| `.env.example` | 模型配置模板，不含真实 Key；复制为被忽略的 `.env` 后在本机填写 |
| `.gitignore` | 告诉 Git 哪些本机文件不应跟踪 |
| `docs/day-01.md` | 第一天的步骤和验收标准 |
| `docs/day-02.md` | 岗位列表、查询参数和参数校验练习 |
| `docs/day-03.md` | 配置读取、模型 HTTP 请求与响应练习 |
| `docs/day-04.md` | JSON 结构化输出、Pydantic 字段校验及失败情况练习 |
| `docs/day-05.md` | pytest 断言、异常检查和模拟请求练习 |
| `docs/day-06.md` | 提取正文解析函数，练习分配解析与命令行展示的职责 |
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

## Day 3 独立脚本

首次使用时，将 `.env.example` 复制为本目录的 `.env`，在本机填写 Key。然后运行：

```bash
uv run --env-file .env python scripts/first_model_call.py
```

`--env-file .env` 负责加载配置，`os.getenv()` 本身不会读取文件。Key 不提交，执行脚本会产生正常的模型调用用量。

本次真实调用返回 `deepseek-flash`，结束原因为 `stop`，输入 30、输出 94、合计 124 Token。成功响应、缺少 Key、超时、连接失败和 HTTP 401 / 429 / 500 分支已通过本地模拟检查。

## Day 4 结构化出题

使用本目录已有的 `.env`，运行：

```bash
uv run --env-file .env python scripts/structured_question.py
```

当前脚本会实际调用模型，并打印通过校验的题目数据、结束原因、模型名和 Token 用量。分步练习过程保留在 [Day 4 任务单](docs/day-04.md)。

本次真实调用生成了关于 `append()` 和 `extend()` 区别的题目，模型返回 `deepseek-flash`，结束原因为 `stop`，输入 169、输出 52、合计 221 Token。24 个本地模拟场景通过，覆盖请求错误、响应结构异常、截断、JSON 解析和字段校验。

校验通过表示数据符合已声明的规则，题目内容与难度仍需人工检查。知识点目前检查元素类型和列表数量，尚未限制每个知识点字符串必须非空。

## Day 5 自动化测试

在学习项目根目录执行：

```bash
uv run python -m pytest -q
```

2026-10-30 验证结果为 `8 passed`，没有跳过的测试。包括 5 个字段校验测试，以及成功响应、非法 JSON 和截断 3 个流程测试。Day 4 的 24 个模拟场景是助手的临时检查，不是当前仓库已有的 pytest 测试。

成功场景检查调用次数、URL、请求中的 JSON 输出格式，以及题目、模型名和结束原因的打印。两个失败场景检查退出提示、非零退出值，并确认没有打印成功的题目字典。截断场景特意使用合法题目正文，单独验证结束原因检查。

Day 5 通过模拟请求测试整个命令行流程。Day 6 又把正文解码与字段校验提取成独立函数，命令行负责打印成功结果或将异常转换成退出提示。[Day 5 任务单](docs/day-05.md) · [Day 6 任务单](docs/day-06.md)

测试环境使用假配置，默认阻止 `httpx.post` 发真实请求；流程测试由自己提供模拟响应。测试命令不需要加载 `.env` 或启动服务。

## 学习方式

先描述输入、输出、失败情况，再自己实现。使用 AI 解释概念、审查实现、设计反例；记录哪些部分得到了辅助，以及自己如何验证。完成一个模块后，应能独立解释和修改它。

从 Day 5 续学开始，同时梳理数据流、职责边界和设计取舍，结合实际实现准备面试回答。后续设计与已完成能力分开记录。
