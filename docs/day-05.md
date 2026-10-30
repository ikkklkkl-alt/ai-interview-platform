# Day 5：用 pytest 编写自动化测试

开始日期：2026-10-29。Day 4 已提交并推送，提交编号是 `b3c1dce`。

Day 4 助手临时模拟了 24 个场景，仓库里没有对应的完整测试集。Day 5 开始把关键行为写成自己能解释、能重复运行的测试。

## 当前进度与复盘

2026-10-29 完成第一、二关并推送阶段成果 `26eacc0`，当时完整测试结果为 `5 passed, 3 skipped`。2026-10-30 完成第三、四关，完整测试结果为 `8 passed`，没有跳过的用例。本次仍属于 Day 5，未创建 Day 6。

- 已完成：正确样例、非法难度、缺少 difficulty、空白题目、多余 answer 五个字段测试；体验断言失败、恢复通过以及预期异常被捕获。
- 第三关已完成：用 fake_post 返回模拟响应，调用真实 main，检查请求次数、URL、JSON 输出格式，以及题目、响应模型名和结束原因的输出。
- 第四关已完成：分别验证正文不是 JSON、结束原因为 length 时提示并退出，不继续打印成功结果。截断测试使用完整、合格的题目 JSON。
- 已练习：monkeypatch 替换外部请求，capsys 读取输出，pytest.raises 捕获 SystemExit，区分请求体与响应体。
- 已排查：URL 期望值把点号误写成逗号；json.dumps 漏传对象；编辑器修改未保存。第一、二关整理时还纠正过把逗号误当作第二个断言条件的问题。
- 待收尾：复盘测试边界，提交并推送本次续学成果。下面保留分步练习说明，供回顾使用。

复盘时尝试不看示例解释：为什么只替换 httpx.post、为什么截断测试使用合法 JSON、为什么预期异常被正确抛出也是测试通过。只有注释的函数体会导致语法错误；仅写 pass 虽可消除语法错误，却没有验证行为。以后尚未开始的测试仍可用 skip 如实标记进度。

## 准备情况

- 已添加 pytest 开发依赖，锁定版本为 9.2.0。项目运行依赖与开发依赖分开记录。
- `scripts/__init__.py` 将学习脚本目录明确作为包，方便导入。
- `tests/test_question_schema.py` 放字段校验测试，`tests/test_model_call.py` 放调用流程测试。
- `tests/conftest.py` 已准备假配置，并默认阻止测试直接使用 `httpx.post` 发请求。第三关由自己的模拟函数替代它。
- 最初提供了 5 个带 skip 的测试入口；目前已扩充并完成 8 个测试，所有 skip 均已移除。

pytest 会找到 `test_*.py` 中以 `test_` 开头的函数。今天在学习项目根目录使用 `uv run python -m pytest`，它使用项目的 Python 环境运行测试，也能从根目录导入脚本包。[pytest 入门](https://docs.pytest.org/en/stable/getting-started.html)

## 第一关：写一个能判断对错的测试

预计 30～45 分钟。打开 `tests/test_question_schema.py`，只完成 `test_valid_question()`。

1. 删除该函数里的 `pytest.skip(...)`，保留其他未完成测试的 skip。
2. 使用已准备的 `sample_data` 调用 `InterviewQuestion.model_validate()`，把返回对象保存到变量。
3. 用 `assert` 检查题目文本、难度和知识点列表是否与预期一致。

假设返回对象命名为 `question`，一条断言可以这样写：

```python
assert question.difficulty == "easy"
```

自己补上另外两条。`assert` 后面的条件为假时，测试失败，pytest 会显示实际值与期望值的差异。仅打印结果不会自动判断对错。[断言说明](https://docs.pytest.org/en/stable/how-to/assert.html)

只运行这个测试：

```bash
uv run python -m pytest tests/test_question_schema.py::test_valid_question -q
```

预期 `1 passed`。如果仍是 `1 skipped`，检查是否删除了对应的 skip，并保存文件。

再做一次实验：把断言中期望的 `"easy"` 临时改成 `"hard"`，运行后应看到失败；再恢复成 `"easy"`，重新运行通过。只改测试的期望值，体会失败报告如何指出问题。

第一关的收获是解释清楚：输入是什么、调用了什么、用哪些断言判断结果。

## 第二关：预期报错，也可以是测试通过

预计 45～60 分钟。完成 `test_invalid_difficulty()`，输入使用 `expert`。

应用中的 `try/except` 负责处理错误；测试中的 `pytest.raises()` 用于确认确实发生了预期异常。语法提示：

```python
with pytest.raises(ValidationError) as exc_info:
    InterviewQuestion.model_validate(sample_data)
```

如果没有抛出预期异常，测试会失败。`exc_info.value` 是捕获的异常对象。[异常断言](https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions)

继续检查 `exc_info.value.errors()` 中的字段位置 `loc` 和错误类型 `type`，例如非法难度对应 `("difficulty",)` 与 `literal_error`。这比只判断“发生了任何异常”更准确。

理解后再增加以下测试，每个测试重新准备一份正确样例，只改要验证的一处：

| 场景 | 要检查的字段 / 错误类型 |
| --- | --- |
| 缺少 difficulty | difficulty / missing |
| question 全为空格 | question / string_too_short |
| 多出 answer | answer / extra_forbidden |

知识点为空列表、知识点类型错误等场景可以继续补充。写出独立测试后，可选用 `@pytest.mark.parametrize` 整理重复结构；先理解每个案例，再合并。[参数化说明](https://docs.pytest.org/en/stable/how-to/parametrize.html)

运行全部字段测试：

```bash
uv run python -m pytest tests/test_question_schema.py -q
```

## 续学：先画流程，再确定测试边界

本次目标：给程序一份确定的模型响应，验证它能正确提取、校验和输出面试题。

当前 `scripts/structured_question.py` 的 `main()` 承担以下职责。这是已有代码的执行流程，还没有拆成独立的服务层、客户端层：

```text
读取配置 → 组装请求 → httpx.post → 检查状态码、解析外层响应
                                    ↓
                       检查结束原因、提取 content
                                    ↓
                       解析题目 JSON → Pydantic 校验 → 打印结果
```

| 职责 | 当前代码 | 本次测试怎么处理 |
| --- | --- | --- |
| 配置 | os.getenv | conftest.py 提供假配置 |
| 与外部服务通信 | httpx.post | 用 fake_post 返回预先准备的响应 |
| 解析和校验 | response.json、json.loads、model_validate | 执行已有真实代码 |
| 展示结果 | print | 用 capsys 读取输出并断言 |

`httpx.post` 是这次的外部依赖边界：正常运行时在这里访问模型服务，测试时从这里接入模拟响应。这样可以稳定复现成功、错误 JSON 和截断，不依赖网络或模型每次生成的内容。

边界也限定了结论：测试通过能说明程序会怎样处理这些预设响应，不能证明真实服务可用、Key 有效或面试题质量足够好；真实调用需要另外验证。

当前先保留脚本结构，弄清各部分职责。将来接入 FastAPI、出现复用需求时，再考虑让客户端负责通信、解析函数负责校验、接口或命令行负责展示。这是后续设计方向，尚未实现。拆分的依据是职责和变化原因，不是文件数量。

动手前试着解释：如果把整个 `main()` 替换为直接返回成功的假函数，哪些已有逻辑就无法被这次测试验证了？

相关面试问答仅供本地复习，不纳入 Git 版本管理；每题都区分当前进度和后续设计。

## 第三关：用模拟响应测试 main

预计 45～60 分钟。打开 `tests/test_model_call.py`，完成 `test_main_prints_valid_question()`。

这次调用真实的 `main()`，保留它的解析、校验与异常处理逻辑；将外部依赖 `httpx.post` 替换为自己写的函数。

先理解已准备的测试环境：pytest 自动加载 `conftest.py`。其中的 fixture 会在每个测试前设置假 Key、`https://example.invalid` 地址和 `test-model` 模型名；测试结束后恢复原来的环境。它不会修改 `.env` 文件。

`monkeypatch` 和 `capsys` 是 pytest 提供的 fixture，写进测试函数参数就可以使用。前者临时替换函数或配置，后者读取程序打印的内容。[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)、[输出捕获](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html)

按顺序完成：

1. 准备一份符合字段规则的题目字典。
2. 用 `json.dumps(question_data, ensure_ascii=False)` 将它转成 JSON 字符串，放入外层响应的 `choices[0].message.content`。设置 `finish_reason="stop"`，并给出模拟的 `model` 与 `usage`。
3. 定义 `fake_post(url, **kwargs)`，记录收到的请求，然后返回 `httpx.Response`。
4. 用 monkeypatch 替换请求函数，再调用 `structured_question.main()`。
5. 检查请求参数和捕获的输出。

模拟函数返回响应的语法提示：

```python
request = httpx.Request("POST", url)
return httpx.Response(200, request=request, json=response_body)
```

`httpx.Response(...)` 只是构造对象，不会发网络请求。附上 `request`，后面的 `raise_for_status()` 才能正常工作。

替换与读取输出的语法提示：

```python
monkeypatch.setattr(structured_question.httpx, "post", fake_post)
# 在这里调用 main()
output = capsys.readouterr().out
```

可以用一个列表记录 fake_post 收到的请求，确认只调用了一次；检查 URL、`response_format` 是否符合预期。输出中应包含模拟题目、结束原因和模拟响应中的模型名。断言关键值即可，不必绑定整段输出的空格排版。

注意：`response_body` 是外层 Python 字典，其中的 `content` 应为 JSON 字符串。这里会再次用到 Day 4 的两层数据结构。

## 第四关：证明失败时不会继续输出成功结果

预计 30～45 分钟。继续完成调用流程文件中的两个测试：

| 场景 | 模拟内容 | 预期行为 |
| --- | --- | --- |
| 模型正文不是 JSON | 外层合法，stop 结束，content 为普通文字 | SystemExit，提示正文不是有效 JSON |
| 生成被截断 | 正文是完整且合格的 JSON，finish_reason 为 length | SystemExit，提示可能被截断 |

第二个测试刻意使用能解析的正文，确保程序确实检查了结束原因。

使用 `pytest.raises(SystemExit)` 捕获退出，再检查 `exc_info.value.code` 包含预期提示且不是 0。调用后使用 capsys 检查没有打印 `转成字典:`，证明程序没有继续输出成功结果。

根据进度，可继续增加缺少 Key、超时、HTTP 401、空 choices 等测试。缺少 Key 时可以使用 `monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)`；默认阻止真实请求的函数应保持有效，以发现不该发生的请求。

## 运行与验收

在学习项目根目录运行：

```bash
uv run python -m pytest -q
```

这些测试使用假配置和模拟响应，不需要 `--env-file .env`，也不需要启动 Uvicorn。mock 测试验证的是本地程序行为，真实服务的模型质量与可用性需要另外验证。

2026-10-30 完成代码后的实际验证结果：`8 passed`。README 和学习记录已同步当前进度，面试问答另行保留在本地。

今天完成的标准：

- 正确样例、非法难度、缺少字段、空白题目、多余字段均有有效断言。
- 成功调用、非法 JSON、截断三个流程场景有模拟测试。
- 亲眼看到过一次断言失败，能解释失败原因，并恢复正确断言。
- 能解释 assert、pytest.raises、monkeypatch、capsys 各自负责什么。
- 必做测试全部通过，已完成的测试不再保留 skip。不要用删除断言或无条件通过来处理失败。
- 更新 README 和学习记录，如实记录完成情况及 AI 辅助。

## 提交和推送

第一、二关已通过 `26eacc0` 保存并推送，提交说明为 `test: add question validation tests and Day 5 checkpoint`。第三、四关和本次文档更新尚未提交，可在检查改动后执行：

```bash
git add .gitignore tests/test_model_call.py README.md docs/day-05.md docs/learning-log.md
git --no-pager diff --cached --stat
git commit -m "test: cover model response success and failures"
git -c http.version=HTTP/1.1 push
git status --short --branch
```

如果仍使用已开启的 Clash 且端口仍为 7897，可将推送命令换成：

```bash
git -c http.proxy=http://127.0.0.1:7897 -c http.version=HTTP/1.1 push
```
