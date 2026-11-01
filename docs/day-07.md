# Day 7 · 用 HTTP 预览一道面试题

2026-11-01。起点为 Day 6 提交 `cdec64d`，开工时完整测试得到 `11 passed`。完成四个 HTTP 用例后，运行 `uv run python -m pytest -q` 对应的项目测试集，结果为 `15 passed, 1 warning`。警告来自 Starlette 测试客户端对当前 HTTPX 依赖的弃用提示。

## 一段正文，两种入口

拿脚本生成过的一段题目正文，在 `/docs` 中提交给 `POST /questions/preview`。预览成功时，网页拿到题干、难度和知识点。本地使用固定正文即可完成练习。

| 步骤 | 负责者 | 交给下一步的数据 |
| --- | --- | --- |
| 接收 HTTP 请求 | FastAPI 和请求模型 `QuestionPreviewRequest` | 客户端提交的 `content` 字符串 |
| 解码 JSON 并校验题目 | 昨天写的 `parse_question_content()` | `InterviewQuestion` 对象，或具体的解析异常 |
| 回应这次请求 | Web 路由 | 成功返回题目对象，失败返回 HTTP 状态码和提示 |

可直接粘贴进 Swagger UI 的请求体：

```json
{
  "content": "{\"question\":\"Python 中列表和字典如何查找元素？\",\"difficulty\":\"easy\",\"knowledge_points\":[\"列表\",\"字典\"]}"
}
```

预期状态为 `200`，响应体如下：

```json
{
  "question": "Python 中列表和字典如何查找元素？",
  "difficulty": "easy",
  "knowledge_points": ["列表", "字典"]
}
```

请求里的 `\"` 用来在 JSON 字符串中表示引号。FastAPI 读完外层请求后，`payload.content` 就是可以传给解析函数的正文。

## 第一关 · 跑通一份合法输入

1. 在 [Web 入口](../app/main.py) 顶部从 `pydantic` 导入 `BaseModel`、`Field`，从 `scripts.structured_question` 导入 `InterviewQuestion`、`parse_question_content`。脚本由 `if __name__ == "__main__"` 守住命令行入口，导入这两个定义时不会调用模型。
2. 在文件末尾顶格定义 `class QuestionPreviewRequest(BaseModel):`，给它一个必填字段 `content: str = Field(min_length=1)`。路由使用这个类型作为参数，FastAPI 会读取并校验 JSON 请求体。[FastAPI 请求体](https://fastapi.tiangolo.com/tutorial/body/)
3. 用 `@app.post("/questions/preview", response_model=InterviewQuestion)` 注册路由。函数签名为 `def preview_question(payload: QuestionPreviewRequest):`。取出 `payload.content`，调用昨天的解析函数，把得到的对象返回给 FastAPI。

在项目根目录启动服务。已经在 8002 运行且带 `--reload` 时，保存后刷新页面即可。

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

打开 `http://127.0.0.1:8002/docs`，展开 `POST /questions/preview`，点 **Try it out**，粘贴请求体，再点 **Execute**。观察状态码和响应中的 `difficulty`。在浏览器地址栏直接输入接口路径会发送 GET 请求。

## 第二关 · 解释失败原因

| 谁先发现问题 | 请求样例 | 预期行为 |
| --- | --- | --- |
| 请求模型 | `{}`，缺少 `content` | FastAPI 自动返回 422，错误位置包含 `body` 和 `content` |
| 正文解码 | `{"content":"这是一道面试题"}` | 路由返回 422，`detail` 为 `题目正文不是有效的 JSON` |
| 题目字段校验 | 只将合法样例的难度改成 `expert` | 路由返回 422，`detail` 为 `题目字段不符合规则` |

只围绕解析函数调用写 `try`，分别捕获 `json.JSONDecodeError` 和 `pydantic.ValidationError`。用 `raise HTTPException(status_code=422, detail=...)` 返回对应提示。这里的 422 表示客户端可以修改刚提交的内容再试。命令行和 Web 处理同一种解析异常时，一个用退出提示结束脚本，一个结束当前请求并继续提供服务。[FastAPI 错误处理](https://fastapi.tiangolo.com/tutorial/handling-errors/)

## 第三关 · 从 HTTP 入口验收

在 `tests/test_question_preview.py` 中通过 `TestClient(app)` 提交请求。用四个测试覆盖一个成功响应和表中的三个失败响应。[FastAPI 接口测试](https://fastapi.tiangolo.com/tutorial/testing/)

成功用例可以用 Python 构造请求，省去手写转义引号。先准备题目字典 `sample`，再发送：

```python
response = client.post(
    "/questions/preview",
    json={"content": json.dumps(sample, ensure_ascii=False)},
)
```

检查状态码和 `response.json() == sample`。缺少字段的用例检查错误位置，其余两个失败用例分别检查状态码和 `detail`，确认错误来自预期步骤。

```bash
uv run python -m pytest tests/test_question_preview.py -q
uv run python -m pytest -q
```

验收目标是四个接口用例与原有十一个用例合计 `15 passed`。完成时用 `expert` 样例说明请求模型、解析函数和路由各做了什么，再按实际结果写学习记录、检查改动并提交。
