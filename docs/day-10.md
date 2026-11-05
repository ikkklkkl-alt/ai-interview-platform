# Day 10 · 从简历原文提取候选画像

2026-11-04 开始，起点为 Day 9 收尾提交 `ab66620`。今天用一份虚构简历跑通命令行流程。DeepSeek 提供候选技能和项目，程序核对字段和引文，最后由人判断原句能否支持这项结论。

## 第一关 · 让一份模型正文走过 Day 9 的校验

简历原文是 `我用 FastAPI 实现了文件上传。`。假设模型返回的消息正文如下。程序拿到的 `content` 是包含这段 JSON 的字符串。

```json
{"skills":[{"name":"FastAPI","evidence":"我用 FastAPI 实现了文件上传。"}],"projects":[]}
```

在 `app/resume_profile.py` 里写 `parse_profile_content(content: str, source_text: str) -> ResumeProfile`。参照 Day 6 的 `parse_question_content`，先用 `json.loads` 解码，再调用已有的 `ResumeProfile.model_validate`。把画像对象和原文传给 `check_profile_evidence`，通过后返回画像对象。核对函数成功时返回 `None`。

保留原文，把模型正文里的“上传”改成“下载”。先预测这份数据会在哪一步失败，再运行验证。

## 第二关 · 固定输入，区分失败原因

给解析函数写离线测试。合法正文应返回包含 FastAPI 及原句的画像。依次只改一处输入，观察失败在哪一步发生。

| 改动 | 应观察到的结果 |
| --- | --- |
| 正文改成普通文字 | JSON 解码失败 |
| JSON 中只保留 `projects` | 画像校验报告缺少 `skills` |
| 技能引文只把“上传”换成“下载” | 字段校验通过，引文核对报错并指出 FastAPI |

## 第三关 · 把真实模型接到同一个函数

在 `scripts/extract_resume_profile.py` 写命令行入口。从 Day 4 脚本取用已有的模型配置和请求方式，把任务换成简历提取。系统消息约定输出 JSON，技能和项目都要有逐字引文，没有符合条件的条目就返回空列表。用户消息单独提供虚构简历原文。

可以复用 Day 9 的三句简历，其中既有实际使用的 FastAPI，也有“接下来想学 Redis”。先用模拟响应验证调用流程，包括 `finish_reason` 为 `length` 时拒绝截断的正文。正常结束时，将 `choices[0].message.content` 与发送前的同一份原文交给第一关的函数。

脚本写好后，在学习项目根目录用现有配置运行：

```bash
uv run --env-file .env python -m scripts.extract_resume_profile
```

读一遍候选条目和引文。特别检查 Redis 有没有被误收录，即使“接下来想学 Redis”可以逐字匹配，也要回到技能的收录条件判断。记录模型实际返回了什么、程序查出了什么，以及哪一步需要人来判断。最后运行 `uv run python -m pytest -q`，把真实调用和离线测试的结果分开记录。

## 11 月 5 日验收

画像测试共 9 个，其中本次新增 4 个解析用例。全套测试为 `33 passed, 1 warning`。助手还临时模拟了完整脚本的 5 个场景，确认合法画像能打印，正文 JSON 错误、缺字段、改写引文及截断分别退出并给出对应提示。

学习者运行真实模型后贴出了结果。HTTP 200，模型名为 `deepseek-flash`，结束原因为 `stop`，输入 267、输出 56、总计 323 Token。

| 提取条目 | 实际引文 |
| --- | --- |
| 技能 FastAPI | 我用 FastAPI 实现了文件上传 |
| 技能 pytest | 用 pytest 验证了空文件的处理 |
| 项目 简历预览工具 | 项目：简历预览工具。 |

这些引文都是原文中的连续片段，描述了实际使用或项目名称。模型正确排除了计划学习的 Redis，本次样例通过人工核对。
