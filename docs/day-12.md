# Day 12 · 通过 HTTP 获取简历画像

2026-11-09 开始，起点为 Day 11 提交 `1a8ffbd`。上一天的全套测试为 `39 passed, 1 warning`。今天通过 FastAPI 复用画像提取函数，在 `/docs` 中提交原文并查看候选画像。

## 第一关 · 约定输入和输出

新增 `POST /resumes/extract`。请求体包含一个必填的字符串字段 `text`，例如下面这份虚构简历。

```json
{
  "text": "项目：简历预览工具。\n我用 FastAPI 实现了文件上传，用 pytest 验证了空文件的处理。\n接下来想学 Redis。"
}
```

在 `app/main.py` 中定义 `ResumeExtractionRequest`，先使用已有的 `BaseModel` 和 `Field` 声明 `text`，最小长度为 1。再练习用字段校验器拒绝只含空格、换行或制表符的文本。用 `text.strip()` 判断是否为空，校验通过后返回原文，保留用于引文核对的缩进和换行。

成功响应为 `ResumeProfile`，包含 `skills` 和 `projects`。例如下面是一份符合响应结构的画像。

```json
{
  "skills": [
    {"name": "FastAPI", "evidence": "我用 FastAPI 实现了文件上传"}
  ],
  "projects": [
    {"name": "简历预览工具", "evidence": "项目：简历预览工具。"}
  ]
}
```

## 第二关 · 让路由调用提取函数

导入已有的 `extract_resume_profile`、`ResumeExtractionError` 和 `ResumeProfile`。路由读取 `payload.text`，调用提取函数，取得 `ResumeExtractionResult`，将其中的 `profile` 返回。装饰器使用 `response_model=ResumeProfile` 描述接口的成功响应。

提取函数使用同步的 `httpx.post`，这个路由使用普通 `def`。调用链为“请求模型校验 → 提取函数 → 画像解析与引文核对 → 路由返回画像”。

捕获 `ResumeExtractionError` 后，由路由抛出 `HTTPException`，本课将提取失败统一映射为 HTTP 503，detail 固定为“简历画像提取暂时不可用，请稍后重试”。请求体自身缺字段、类型错误或正文为空，由 FastAPI 返回 422。

| 情况 | HTTP 结果 | 负责处理的位置 |
| --- | --- | --- |
| 提取成功 | 200，响应中有 skills 和 projects | 路由返回 result.profile |
| 缺少 text、类型错误或正文为空 | 422，响应中有校验错误 | 请求模型 |
| 提取函数报告失败 | 503，响应中有统一的 detail | 路由捕获提取异常 |

## 第三关 · 从 HTTP 入口验证

在 `tests/test_resume_extraction_api.py` 使用 `TestClient`，模拟路由实际使用的提取函数。

成功用例提交带缩进和换行的简历，确认函数收到完整原文，响应状态为 200，响应体与预期画像一致。失败用例让提取函数抛出带具体原因的 `ResumeExtractionError`，检查 HTTP 503 和固定提示。

分别提交 `{}`、`{"text": ""}` 和 `{"text": "  \n\t"}`，确认返回 422，错误位置指向 `text`，且这些请求在校验阶段就结束。可以让假的提取函数记录调用次数，检查它在非法输入时没有被调用。

## 第四关 · 在网页里调用真实模型

先完成模拟测试，再在学习项目根目录加载配置并启动服务。

```bash
uv run --env-file .env uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

打开 [接口文档](http://127.0.0.1:8002/docs)，找到 `POST /resumes/extract`，点击 Try it out，填入第一关的 JSON，再点击 Execute。核对返回的技能和项目，逐条对照原文，并判断学习计划中的 Redis 是否被正确排除。

Day 8 的上传预览返回正文后，也可以把那个 `text` 值交给今天的接口。最后运行 `uv run python -m pytest -q`，分别记录自动化测试和真实网页调用的结果，再整理提交。

## 本次完成情况

2026-11-10 完成本地验收，待提交和推送。

新增的 5 个接口测试全部通过，全套测试为 `44 passed, 1 warning`。警告来自已有的测试客户端依赖。接口测试替换 `app.main` 实际使用的提取函数，保留请求校验、路由和响应处理，不发送模型请求。

| 用例 | 检查内容 |
| --- | --- |
| 提取成功 | 返回 200 和预期画像，提取函数只调用一次，收到含缩进和换行的完整原文 |
| 提取失败 | 提取函数抛出异常后，返回 503 和统一的 detail |
| 缺少 text | 返回 422，错误位置为 `["body", "text"]`，提取函数没有被调用 |
| 空字符串 | 返回 422，错误位置为 `["body", "text"]`，提取函数没有被调用 |
| 纯空白正文 | 返回 422，错误位置为 `["body", "text"]`，提取函数没有被调用 |

学习者在 `/docs` 中提交第一关的虚构简历，提供的服务日志显示 `POST /resumes/extract` 返回 HTTP 200，响应如下：

```json
{
  "skills": [
    {
      "name": "FastAPI",
      "evidence": "我用 FastAPI 实现了文件上传"
    },
    {
      "name": "pytest",
      "evidence": "用 pytest 验证了空文件的处理"
    }
  ],
  "projects": [
    {
      "name": "简历预览工具",
      "evidence": "项目：简历预览工具。"
    }
  ]
}
```

三条引文都能在原文中连续找到，计划学习的 Redis 没有被提取。助手另用现有解析函数复核了这份响应的字段和引文；这次复核没有发送模型请求，也不计入仓库的 44 个测试。

## 回顾本次的职责划分

请求模型先检查输入，再把完整原文交给提取函数。提取函数完成模型调用、响应检查和画像校验，返回结果对象。路由从中取出画像，生成 HTTP 响应。

同一个 `ResumeExtractionError` 在命令行入口被转换成退出提示，在 HTTP 入口被转换成 503。提取函数可以被两个入口复用，因为它返回数据或报告异常，由入口决定展示和错误响应。
