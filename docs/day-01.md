# Day 1：第一个接口与第一次提交

预计 2–3 小时，余下时间用于提问、调试和记录。今天不用模型 Key，不产生模型调用费用。

## 1. 认识目录和环境（约 20 分钟）

在终端执行以下命令。后续所有 Git 操作都在这个学习目录内执行。

```bash
cd /Users/k/Documents/deepseek-projects/ai-interview-learning
pwd
ls -la
uv run python --version
```

`pwd` 显示当前目录；`ls -la` 包含以点开头的隐藏文件。`uv run` 使用本项目的 Python 环境，版本应为 3.13.x。

阅读 `pyproject.toml`、`.python-version`、`.gitignore`，尝试说明：项目需要什么依赖？为什么 `.venv` 不提交，而 `uv.lock` 要提交？

## 2. 用 Git 观察文件（约 20 分钟）

Git 保存本地修改历史；GitHub 托管远程仓库。今天先掌握本地操作，再上传 GitHub。

```bash
git init -b main
git status --short
```

初始化后出现 `.git` 目录，主分支名为 `main`。`??` 表示 Git 尚未跟踪的文件。此时先观察，等接口验收完成后再提交。

## 3. 亲自实现接口（约 30–45 分钟）

打开 `app/main.py`，完成其中的 TODO。契约如下：

| 项目 | 要求 |
| --- | --- |
| 请求方法 | GET |
| 路径 | `/health` |
| 请求参数 | 无 |
| HTTP 状态码 | 200 |
| 响应类型 | JSON |
| 响应正文 | `{"status": "ok"}` |

可以参考 [FastAPI First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)。先认识导入、应用实例、路由装饰器、处理函数、返回值这五部分，再尝试独立写出。

第一版用普通 `def` 即可。今天的处理函数没有外部 I/O，不需要先解决异步编程。

提示：创建的实例命名为 `app`；路由装饰器需要同时描述请求方法与路径；返回 Python 字典，让框架完成 JSON 序列化。

## 4. 启动并验证（约 20–30 分钟）

完成实现后，在终端 A 执行：

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

这条命令的含义：

- `uv run`：在本项目环境中运行命令。
- `uvicorn`：启动能够接收 HTTP 请求的 ASGI 服务程序。
- `app.main:app`：加载 `app/main.py` 模块中的 `app` 对象。
- `--reload`：开发时修改代码后重新加载。
- `127.0.0.1`：只在本机监听。
- `8001`：本次练习使用的端口。

打开 http://127.0.0.1:8001/health，查看结果。再打开 http://127.0.0.1:8001/docs，找到 GET /health 并执行。

在另一个终端 B 执行：

```bash
curl -i http://127.0.0.1:8001/health
curl -i http://127.0.0.1:8001/does-not-exist
curl -i -X POST http://127.0.0.1:8001/health
```

分别观察 200、404、405。区分 HTTP 状态码、响应头与响应正文，不只看页面有没有文字。

把正文中的 `"ok"` 暂时改为 `"learning"` 并刷新，观察自动重载，再改回 `"ok"`。这时应能描述完整路径：客户端请求 → Uvicorn → FastAPI 路由 → 处理函数 → JSON 响应。

排查提示：连接被拒绝通常先检查服务是否已启动；找不到 `app` 属性时检查 TODO 2；端口占用时换端口并同步修改请求地址。按 Ctrl+C 可停止服务。

这个接口现在只说明应用能够响应请求，不检查数据库、Redis 或模型服务。

## 5. 保存第一次本地提交（约 20 分钟）

先填写 `docs/learning-log.md` 的 Day 1 部分，并把 README 的当前进度改为真实状态。随后执行：

```bash
git status --short
git add .gitignore .python-version pyproject.toml uv.lock README.md app docs
git diff --cached --stat
git diff --cached
```

如果差异较长，Git 可能进入分页器；按 q 返回终端。确认暂存的都是本项目应提交的内容后，执行：

```bash
git commit -m "feat: add first health endpoint"
git log --oneline -1
git status --short
```

`git add` 把当前文件内容放进暂存区；`git commit` 将暂存内容记录为本地历史。提交后再次编辑文件，需要重新 add 才会进入下一次提交。commit 此时还没有上传 GitHub。

`.venv`、`.env`、`__pycache__` 等不应出现在提交里。不要在上一级参考项目目录执行 `git add .`。

## 6. GitHub 检查点

完成本地验收后，再一起创建或选择远程仓库、理解 origin 和 push，并上传当天成果。当前骨架没有远程地址；第一次上传前需要确定你使用的 GitHub 账号、仓库名称和可见性。

## 今天的验收

- [ ] 用自己的话说明 FastAPI 与 Uvicorn 的职责。
- [ ] GET /health 返回 200 和约定的 JSON。
- [ ] 能说明访问不存在路径为什么返回 404、用 POST 访问 GET 接口为什么返回 405。
- [ ] 完成一次本地提交，理解工作区、暂存区和提交的区别。
- [ ] 完成学习记录，区分亲自完成与工具辅助的工作。
- [ ] 解释为何这时还没有调用大模型。

提交学习结果时，提供你的 `app/main.py` 实现、GET /health 的响应和一两句自己的解释。遇到报错时提供相关错误文字即可，先一起定位原因。

参考：[Git 中文文档：记录更新](https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库)、[uv 项目指南](https://docs.astral.sh/uv/guides/projects/)。
