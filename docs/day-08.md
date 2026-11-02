# Day 8 · 上传 TXT / Markdown 简历，预览原文

2026-11-02。起点是 Day 7 提交 `e6babf7`，开工时完整测试为 `15 passed, 1 warning`。本地验收已完成，新增 9 个用例后，完整测试为 `24 passed, 1 warning`。

## 先从用户看到的结果出发

在 `/docs` 选择一份用 UTF-8 保存的 `demo.md`，提交给 `POST /resumes/preview`。如果文件有两行，第一行是“# 项目经历”，第二行是“用 FastAPI 写过接口”，就应该能从响应里读回这两行：

```json
{"filename": "demo.md", "text": "# 项目经历\n用 FastAPI 写过接口"}
```

原文预览让用户先看清系统读到了什么。以后加上“从简历提取技能”时，若原文已经不对，就应该先排查上传和解码；若原文正确但漏提了技能，再检查模型输入和提取逻辑。今天完成到用户能看到原文为止。

| 谁负责 | 输入 | 输出 |
| --- | --- | --- |
| Web 路由 | 表单中名为 `file` 的上传文件 | 检查文件后缀、大小，把文件字节交给解码函数 |
| `decode_resume_text` | 一段 `bytes` | 保留换行和缩进的 `str`，或说明解码、正文校验失败的异常 |
| Web 路由 | 正文或异常 | 文件名和正文，或能帮助用户改正问题的 HTTP 响应 |

## 第一关 · 在终端把字节还原成正文

新建 `app/resume_text.py`，自己实现 `def decode_resume_text(raw: bytes) -> str:`。先只做成功路径：调用字节对象的 `decode` 方法，使用 `utf-8-sig` 编码，返回得到的字符串。这个编码也能读普通 UTF-8；文件开头带有 UTF-8 标记（BOM）时，它会去掉标记。保留正文中的空格和换行，尤其是 Markdown 里的缩进。

从学习项目根目录执行：

```bash
uv run python -c 'from app.resume_text import decode_resume_text; raw = "# 项目经历\n用 FastAPI 写过接口".encode("utf-8-sig"); print(decode_resume_text(raw))'
```

预期输出：

```text
# 项目经历
用 FastAPI 写过接口
```

接下来再补失败情况：遇到无法解码的字节（例如 `b"\xff"`），让 Python 抛出 `UnicodeDecodeError`；对于空文件或只有空白的正文，主动抛出 `ValueError`。可以用 `text.strip()` **判断** 是否为空，通过时仍返回原来的 `text`。试想一下：如果直接返回 `text.strip()`，以四个空格开头的 Markdown 代码会发生什么？

## 第二关 · 让浏览器上传一个文件

做到这里再运行 `uv add python-multipart`。上传文件使用 `multipart/form-data`，和 Day 7 的 JSON 请求体不同。参考 [FastAPI 文件上传](https://fastapi.tiangolo.com/tutorial/request-files/) 中的 `UploadFile` 示例，在 `app/main.py` 添加路由。测试时使用虚构简历即可。

| 传入什么 | 预期的 HTTP 响应 |
| --- | --- |
| 非空、合法的 UTF-8（可带 BOM）文件，扩展名为 `.txt` 或 `.md`，忽略扩展名大小写 | 200，返回 `filename` 和 `text` |
| 文件扩展名不支持，如 `demo.pdf` | 415，提示只支持 TXT / Markdown |
| 文件超过 256 KiB（262144 字节） | 413，提示文件太大 |
| `demo.txt` 含非法 UTF-8 字节 | 422，提示使用 UTF-8 保存 |
| `demo.md` 只有空白或没有内容 | 422，提示简历正文为空 |

在异步路由里读取 `await file.read(上限 + 1)`。恰好到上限是允许的，多读一个字节就能区分“恰好等于”和“已经超过”。这里控制的是路由读入并处理的文件字节数；如果将来要限制整个 HTTP 请求，要在更早的入口再做限制。路由捕获异常时，把较具体的 `UnicodeDecodeError` 放在 `ValueError` 前面，因为前者也是后者的子类。

启动现有服务，在 `http://127.0.0.1:8002/docs` 展开新接口，点 **Try it out → Choose File → Execute**。用有中文和换行的 TXT、Markdown 各试一次，对照原文。

## 第三关 · 留下能发现回归的测试

- 直接测解码函数：用一段带中文、换行和缩进的字符串构造 UTF-8 和带 BOM 的字节，两种结果都应与原字符串完全相等。再分别用坏字节和纯空白验证两个失败原因。
- 从 HTTP 入口测：沿用 Day 7 的 `TestClient`，把 `json=...` 换成 `files={"file": ("demo.md", raw, "text/markdown")}`。按上表检查响应，尤其要分别核对两个 422 的提示。测大小边界时，用相同的文件名，分别传入恰好 262144 和 262145 个 ASCII 字节，其他条件保持有效。
- 最后运行 `uv run python -m pytest -q`。用自己的话记下：如果以后把上传入口换成命令行，哪段代码可以原样拿来用？把实际测试结果和遇到的问题记入学习记录，再检查差异并提交。

## 验收结果

3 个解码用例验证了普通 UTF-8 和带 BOM 的 UTF-8 都能保留正文格式，坏字节和纯空白分别触发预期异常。6 个接口用例覆盖 Markdown 原文预览、不支持的后缀、两种不同提示的 422，以及 256 KiB 边界两侧。恰好 262144 字节的 TXT 原样返回，再加 1 字节就返回 413。全套测试中的 1 条警告来自 Starlette 测试客户端对 HTTPX 的弃用提示。
