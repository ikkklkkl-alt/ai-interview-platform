# Day 3：第一次真实模型调用

开始日期：2026-10-27。今天用一个独立 Python 脚本，请模型出一道 Python 面试题。

昨天是浏览器请求你的 FastAPI；今天是 Python 脚本作为客户端，请求 DeepSeek。

## 准备情况

- 已添加 `httpx`，更新了 `pyproject.toml` 和 `uv.lock`。
- `scripts/first_model_call.py` 最初只有 TODO；当前已完成真实调用、响应读取和基本请求异常处理。下面保留分步练习，方便回顾。
- `.env.example` 是配置模板，没有真实 Key。
- 脚本直接运行，不需要启动 Uvicorn，也不占用 8002 端口。

文档核对日期为 2026-10-27。DeepSeek 当前推荐 `deepseek-flash`；旧名 `deepseek-v4-flash` 仍接受，但已经映射到新版 Flash。学习配置使用当前名称。来源：[DeepSeek 入门文档](https://api-docs.deepseek.com/)。

## 第一关：读取配置

在学习目录执行：

```bash
cd /Users/k/Documents/deepseek-projects/ai-interview-learning
cp -n .env.example .env
git check-ignore .env
```

`cp -n` 不覆盖已有文件。最后一条命令预期显示 `.env`，表示它会被 Git 忽略。

用编辑器打开本目录的 `.env`，填写可用的 DeepSeek Key，地址和模型先保留模板值。可以用原项目已能调用 DeepSeek 的 Key，只在本机填写，不放到代码或聊天中。

| 变量 | 作用 |
| --- | --- |
| `DEEPSEEK_API_KEY` | 调用服务的凭据 |
| `DEEPSEEK_BASE_URL` | 服务地址：`https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名：`deepseek-flash` |

在脚本的 `main()` 中读取配置。单个值的语法提示：

```python
api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
```

`os.getenv` 读取环境变量；第二个参数是变量不存在时的默认值，`.strip()` 去掉首尾空白。按同样方式读取地址和模型。

只打印地址、模型名和 `bool(api_key)`，不打印 Key 本身。Key 为空时提示并退出，可以使用 `raise SystemExit("请在 .env 中填写 DEEPSEEK_API_KEY")`。

运行：

```bash
uv run --env-file .env python scripts/first_model_call.py
```

`--env-file` 让 uv 加载这个文件中的配置，`os.getenv` 本身不会自动读取文件。代码写在 `main()` 里，文件底部已经负责调用它。

你自己写的打印结果应能表达以下内容，这只是预期格式：

```text
服务地址：https://api.deepseek.com
模型：deepseek-flash
是否读到 Key：True
```

`True` 只说明 Key 字符串非空，还不能证明它通过了服务端认证。第一关先不写网络请求，完成后检查一次，再继续。

## 第二关：发送一次请求

请求方法是 POST，地址由服务地址和 `/chat/completions` 组成。拼接前可以用 `.rstrip("/")` 去掉服务地址末尾的斜杠。

自己定义两个字典：

- `headers`：包含 `Authorization`，值为 `Bearer ` 加上 Key。不要打印这个请求头。
- `payload`：包含以下字段。

| 字段 | 本次使用的值 |
| --- | --- |
| `model` | 环境变量中的模型名 |
| `messages` | 两条消息组成的列表，每条含 `role` 和 `content` |
| `stream` | Python 的 `False`，一次接收完整结果 |
| `thinking` | `{"type": "disabled"}`，本次使用非思考模式 |
| `max_tokens` | 256，限制本次输出长度 |

system 消息说明任务要求，例如“你是 Python 面试官，只出一道入门题，不附答案”。user 消息写本次要求，例如“请出一道关于 Python 列表的面试题”。

发送请求的语法提示：

```python
response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
```

其中的三个变量由你在前面定义。`json=payload` 把 Python 数据编码成 JSON，并设置对应的内容类型。超时限制网络操作的等待，不是整次请求严格的总时长上限。

执行到这里会产生正常的 API 用量。先用固定练习内容手动调用一次，不加循环和自动重试。

## 第三关：取出模型回答

先打印 `response.status_code`，用 `response.raise_for_status()` 检查请求是否成功，再调用 `response.json()` 解析响应正文。

下面只是简化的结构示意，不是真实调用记录：

```json
{
  "choices": [
    {
      "message": {"content": "这里是模型生成的题目"},
      "finish_reason": "stop"
    }
  ]
}
```

尝试从解析后的字典取出 `choices`，再取第一个元素，找到 `message` 中的 `content` 并打印。继续查看：

- `finish_reason`：如果是 `length`，需要检查回答是否被输出长度限制截断。
- `model`：响应报告的模型名。
- `usage`：本次用量；token 不能简单等同于汉字数。

今天 HTTP 响应正文是 JSON，但模型回答的 `content` 是文本。让模型按照指定 JSON 格式回答，是后面的练习。

## 第四关：理解错误

给请求加上简单错误处理，先能分清问题发生在哪一层：

| 现象 | 先排查什么 |
| --- | --- |
| 本地读到空 Key | `.env` 是否填写、命令是否带 `--env-file` |
| `httpx.TimeoutException` | 网络或服务响应等待超时 |
| `httpx.RequestError` | 连接、DNS 等问题，可能还没有 HTTP 响应 |
| HTTP 400 / 422 | 请求格式或参数 |
| HTTP 401 | 凭据认证失败 |
| HTTP 402 | 账户余额不足 |
| HTTP 429 | 请求频率或并发限制 |
| HTTP 500 / 503 | 服务端异常或繁忙 |

`raise_for_status()` 对非成功状态抛出 `httpx.HTTPStatusError`，可以通过异常对象的 `response.status_code` 查看状态码。先打印错误类别和状态码即可。

超时异常属于请求错误的一种。如果分别捕获，先处理具体的超时分支，再处理较宽泛的请求错误分支。先分析实际遇到的错误，不必为了凑齐错误码而发送失败请求；后面可以用模拟响应练习。

## 验收和提交

- 能说明地址、Key、模型名的区别。
- 缺少 Key 时在本地停止并提示。
- 完成一次真实请求，取出一道非空题目，检查结束原因。
- 能解释怎样从 `choices` 列表里拿到回答正文。
- 记录实际结果和遇到的问题，未成功调用时如实记录。

完成后更新 README 和学习记录，再提交：

```bash
git status --short
git add pyproject.toml uv.lock .env.example scripts/first_model_call.py README.md docs/day-03.md docs/learning-log.md
git --no-pager diff --cached --stat
git commit -m "feat: add first DeepSeek model call"
git -c http.version=HTTP/1.1 push
```

## 按需查阅

- [DeepSeek 参数与响应](https://api-docs.deepseek.com/api/create-chat-completion/)
- [DeepSeek 错误码](https://api-docs.deepseek.com/quick_start/error_codes/)
- [HTTPX：请求、JSON、状态码与异常](https://www.python-httpx.org/quickstart/)

环境文件参数也可以运行 `uv run --help` 查阅。
