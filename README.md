# AI 模拟面试平台：从零学习版

这是一个按日推进的独立学习项目。现有完整面试系统作为参考，本仓库逐步实现自己的版本。

## 当前进度

- Day 1 已完成：亲自实现 `GET /health`，验证 HTTP 响应，创建本地提交并推送至 GitHub。
- 首次提交：`6a30d07`。远程仓库：[ai-interview-platform](https://github.com/ikkklkkl-alt/ai-interview-platform)。
- Day 2 必做部分已完成并推送（`8a33bc4`）：岗位列表、`limit` 数量限制和 1～10 的范围校验。关键词筛选暂时没做。
- Day 3 已完成并推送（`965c27e`）：独立脚本读取配置，用 `httpx` 调用真实 DeepSeek 模型，打印回答、结束原因和 Token 用量，并处理常见请求错误。
- Day 4 已完成并推送（`b3c1dce`）：模型以 JSON 格式生成面试题，使用 Pydantic 校验字段，并处理响应结构异常、空正文、截断和解析失败。
- Day 5 已完成并推送（`26eacc0`、`f404d29`）。5 个字段校验测试和 3 个模型调用流程测试全部通过。
- Day 6 已完成并推送（`cdec64d`）。已提取 `parse_question_content()` 并在 `main()` 中使用。新增 3 个测试验证合法题目、正文解码失败和非法难度，全套测试结果为 `11 passed`。
- Day 7 已完成并推送（`e6babf7`）。`POST /questions/preview` 接收已有题目正文，复用 Day 6 的解析函数，成功时返回题目，输入错误时返回 422。新增 4 个接口用例，全套测试结果为 `15 passed, 1 warning`。
- Day 8 已完成并推送（`ec4609c`）。`POST /resumes/preview` 接受不超过 256 KiB 的 UTF-8 TXT / Markdown 简历，返回文件名与原文，保留缩进和换行。新增 3 个解码用例和 6 个接口用例，全套测试为 `24 passed, 1 warning`。
- Day 9 已完成并推送（`c72347b`、`ab66620`）。用手工样例验证简历画像的字段和引文，5 个画像测试通过，全套测试为 `29 passed, 1 warning`。
- Day 10 已完成并推送（`1ab8087`）。命令行调用 DeepSeek 提取虚构简历的候选画像，再校验字段和引文。新增 4 个解析测试，全套测试为 `33 passed, 1 warning`。本次真实调用提取出 FastAPI、pytest 和简历预览工具，正确排除了计划学习的 Redis。
- Day 11 已完成并推送（`1a8ffbd`）。画像提取函数接收原文，返回画像及调用信息，用 `ResumeExtractionError` 报告失败。命令行负责打印和退出提示。新增 4 个提取函数测试和 2 个命令行测试，全套测试为 `39 passed, 1 warning`。
- Day 12 已完成并推送（`19be12f`）。`POST /resumes/extract` 接收简历正文，复用提取函数返回画像。无效输入返回 422，提取失败返回 503。新增 5 个接口用例，全套测试为 `44 passed, 1 warning`。已在 `/docs` 中验证真实提取，返回 HTTP 200，三条引文均与原文一致。
- Day 13 已通过本地功能验收。首页支持提交原文、查看引文和勾选画像条目。Edge 实测一次提取请求返回 HTTP 200，随后两次确认都使用页面上已有的数据。

今天的练习见 [Day 13 任务单](docs/day-13.md)。回顾之前的内容可阅读 [Day 1](docs/day-01.md)、[Day 2](docs/day-02.md)、[Day 3](docs/day-03.md)、[Day 4](docs/day-04.md)、[Day 5](docs/day-05.md)、[Day 6](docs/day-06.md)、[Day 7](docs/day-07.md)、[Day 8](docs/day-08.md)、[Day 9](docs/day-09.md)、[Day 10](docs/day-10.md)、[Day 11](docs/day-11.md) 和 [Day 12](docs/day-12.md)。

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
| `app/main.py` | 健康检查、岗位列表、题目预览、简历上传预览和画像提取接口 |
| `app/static/index.html` | 简历输入框、画像提取按钮、候选项和确认结果 |
| `app/resume_text.py` | 将简历字节解码为原文，保留格式并拒绝纯空白正文 |
| `app/resume_profile.py` | 解析画像 JSON，校验技能和项目字段，逐项核对引文是否出现在原文中 |
| `app/resume_extraction.py` | 请求模型并校验响应，返回提取结果或抛出提取异常 |
| `scripts/first_model_call.py` | 独立调用 DeepSeek，读取回答与用量，处理超时、连接及 HTTP 状态错误 |
| `scripts/structured_question.py` | 调用模型生成 JSON 面试题，检查响应并校验题目、难度和知识点 |
| `scripts/extract_resume_profile.py` | 准备虚构简历，调用提取函数，打印结果并将失败转换为退出提示 |
| `scripts/__init__.py` | 将学习脚本目录作为包，供测试导入 |
| `tests/conftest.py` | 准备假配置，默认阻止测试直接发送模型请求 |
| `tests/test_question_schema.py` | 5 个字段校验测试：正确样例、非法难度、缺少字段、空白题目、多余字段 |
| `tests/test_model_call.py` | 模拟成功响应、非法 JSON 和截断；检查请求参数、输出和退出提示 |
| `tests/test_question_content.py` | 直接验证解析函数返回的题目对象和两类异常 |
| `tests/test_question_preview.py` | 从 HTTP 入口检查预览成功、缺少正文、正文解码错误和非法难度 |
| `tests/test_resume_text.py` | 直接检查简历解码、原文格式和异常原因 |
| `tests/test_resume_preview.py` | 从上传入口检查成功响应、文件后缀、大小边界以及两种正文错误 |
| `tests/test_resume_profile.py` | 5 个画像规则用例和 4 个解析用例，覆盖正常结果及解码、字段和引文错误 |
| `tests/test_resume_extraction.py` | 模拟 HTTP 请求，检查传入原文、返回数据、超时、截断和引文错误 |
| `tests/test_resume_extraction_cli.py` | 模拟提取函数，检查命令行成功输出和失败退出 |
| `tests/test_resume_extraction_api.py` | 模拟提取函数，检查画像响应、503 提示，以及三种无效输入在调用前被拒绝 |
| `.env.example` | 模型配置模板，不含真实 Key；复制为被忽略的 `.env` 后在本机填写 |
| `.gitignore` | 告诉 Git 哪些本机文件不应跟踪 |
| `docs/day-01.md` | 第一天的步骤和验收标准 |
| `docs/day-02.md` | 岗位列表、查询参数和参数校验练习 |
| `docs/day-03.md` | 配置读取、模型 HTTP 请求与响应练习 |
| `docs/day-04.md` | JSON 结构化输出、Pydantic 字段校验及失败情况练习 |
| `docs/day-05.md` | pytest 断言、异常检查和模拟请求练习 |
| `docs/day-06.md` | 提取正文解析函数，练习分配解析与命令行展示的职责 |
| `docs/day-07.md` | 题目预览接口的请求样例、响应约定和验收步骤 |
| `docs/day-08.md` | 简历原文解码、文件上传和预览验收练习 |
| `docs/day-09.md` | 简历画像的字段设计、原文依据和校验练习 |
| `docs/day-10.md` | 从模型消息正文解析候选画像，对照原文验证提取结果 |
| `docs/day-11.md` | 提取函数与命令行的职责划分，以及返回值、异常和复用测试 |
| `docs/day-12.md` | 简历画像 HTTP 接口的请求校验、异常转换和网页验收 |
| `docs/day-13.md` | 首页的简历提取、勾选确认和 Edge 验收记录 |
| `docs/learning-log.md` | 用自己的话填写学习记录 |

## 本地运行

首次运行时，将 `.env.example` 复制为本目录的 `.env`，在本机填写模型配置；已有配置可以继续使用。在学习项目目录执行：

```bash
uv sync --locked
uv run --env-file .env uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

8001 被其他服务占用，目前使用 8002。打开：

- [简历画像确认首页](http://127.0.0.1:8002/)
- [健康检查](http://127.0.0.1:8002/health)
- [岗位列表](http://127.0.0.1:8002/interview-directions)
- [接口文档](http://127.0.0.1:8002/docs)

`/health` 返回健康检查结果，`/interview-directions?limit=2` 返回前两条岗位数据。打开首页 `/`，填写简历并点击“读取简历”。看到技能和项目后，勾选想保留的条目，点击“确认画像”查看结果。

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

## Day 10 简历画像提取

在学习项目根目录执行以下命令，使用本机配置处理脚本里的虚构简历。

```bash
uv run --env-file .env python -m scripts.extract_resume_profile
```

2026-11-05 的真实调用返回 HTTP 200，模型名为 `deepseek-flash`，结束原因为 `stop`。输入 267、输出 56、合计 323 Token。返回的两项技能和一个项目均带有原文引文。

解析函数负责 JSON 解码、字段校验和引文核对。Day 11 已把模型请求和响应检查移到提取函数，命令行负责打印结果和转换退出提示。人工结合上下文判断原句是否支持提取出的结论。

本次另有 5 个完整脚本的临时模拟场景通过，覆盖合法画像、无效正文 JSON、缺少 skills、引文被改写，以及正文合法但被标记截断。仓库中的 `33` 个 pytest 用例单独统计。

## Day 12 通过 HTTP 提取画像

按“本地运行”启动服务，在 `/docs` 中展开 `POST /resumes/extract`，点击 Try it out，填写请求体并 Execute：

```json
{
  "text": "项目：简历预览工具。\n我用 FastAPI 实现了文件上传，用 pytest 验证了空文件的处理。\n接下来想学 Redis。"
}
```

成功时返回包含 `skills` 和 `projects` 的画像。缺少 `text`、类型错误、空字符串或纯空白正文返回 422；提取函数报告失败时，接口统一返回 503 和“简历画像提取暂时不可用，请稍后重试”。有效请求会使用本机配置调用真实模型。

2026-11-10 的网页验收返回 HTTP 200，提取出 FastAPI、pytest 和简历预览工具，排除了计划学习的 Redis。三条引文均与原文一致。这是本次样例的验证结果，后续仍需结合上下文检查候选画像。

新增 5 个接口用例覆盖成功、提取失败、缺少正文、空字符串和纯空白正文。全套离线测试为 `44 passed, 1 warning`，警告来自测试客户端依赖。步骤和实际响应见 [Day 12 任务单](docs/day-12.md)。

## 学习方式

先描述输入、输出、失败情况，再自己实现。使用 AI 解释概念、审查实现、设计反例；记录哪些部分得到了辅助，以及自己如何验证。完成一个模块后，应能独立解释和修改它。

从 Day 5 续学开始，同时梳理数据流、职责边界和设计取舍，结合实际实现准备面试回答。后续设计与已完成能力分开记录。
