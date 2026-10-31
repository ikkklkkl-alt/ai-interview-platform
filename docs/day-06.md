# Day 6 · 把模型正文解析成可复用的题目对象

2026-10-31。起点为 Day 5 提交 `f404d29`，开工时运行完整测试得到 `8 passed`。接好新函数并写完三个直接调用它的用例后，再次运行完整测试得到 `11 passed`。

## 先跟着一段数据走

假设将来网页和命令行都要展示一道题。命令行需要打印题目，网页接口需要拿到三个字段。两处可以共用“把模型正文转换成合格题目”这一步。今天先把这一步提取到同一个脚本里的独立函数，等出现第二个调用者时，再决定它适合放在哪个模块。

| 数据经过的位置 | 输入 | 输出或处理方式 |
| --- | --- | --- |
| `main()` 读取模型响应 | HTTP 响应 | 检查状态、外层 JSON、choices、结束原因和非空正文，取出 `message.content` |
| 新函数 `parse_question_content()` | 正文字符串 `content` | 解码 JSON 并按现有字段规则校验，返回一个 `InterviewQuestion` 对象 |
| 命令行展示 | 题目对象或解析异常 | 成功时打印题目和用量，失败时使用已有中文提示退出 |

先预测两种情况。“这是一道题”这段普通文本会在哪一步失败？如果正文是合法 JSON，只有 difficulty 写成 expert，又会在哪一步失败？

## 第一关 · 写一个有明确输入和输出的函数

打开 [出题脚本](../scripts/structured_question.py)，在 `InterviewQuestion` 定义之后、`main()` 之前写下签名。

```python
def parse_question_content(content: str) -> InterviewQuestion:
    """解析模型正文，返回通过字段校验的题目。"""
```

由你补上函数体。参考 Day 5 版本的 `main()` 里使用 `json.loads(content)` 和 `InterviewQuestion.model_validate(...)` 的两行。想清楚第一行产生的数据交给谁，以及调用者最终需要拿到什么。异常可以先沿着函数调用返回给调用者处理。

写完并保存后，在项目根目录粘贴下面的命令，自测一次。它在本地创建一段模型正文并调用新函数。

```bash
uv run python - <<'PY'
import json
from scripts.structured_question import InterviewQuestion, parse_question_content

sample = {
    "question": "Python 中列表和字典如何查找元素？",
    "difficulty": "easy",
    "knowledge_points": ["列表", "字典"],
}
question = parse_question_content(json.dumps(sample, ensure_ascii=False))
assert isinstance(question, InterviewQuestion)
assert question.model_dump() == sample
print(question.question)
PY
```

预期打印样例题目。由调用者执行这里的 `print`，以后调用者也可以直接访问 `question.difficulty`。

## 第二关 · 让命令行走新函数

在 `main()` 中找到处理正文的两段 `try`。用一次 `data = parse_question_content(content)` 替代其中的两次转换，把两个异常分支接到这次调用上。

| 触发条件 | 新函数向调用者抛出的异常 | `main()` 继续提供的行为 |
| --- | --- | --- |
| 正文的 JSON 语法错误 | `json.JSONDecodeError` | 带着“模型返回的内容不是有效的 JSON”退出 |
| 解码成功，字段未通过校验 | `ValidationError` | 带着“题目数据校验失败”和错误详情退出 |

外层 `response.json()` 解析的是服务的 HTTP 响应体，它有自己的错误提示。改完后顺着成功路径读一遍，确认打印语句使用新函数返回的对象，每次请求只转换一次正文。

```bash
uv run python -m pytest tests/test_model_call.py -q
```

这三个已有测试验证成功、非法正文和截断时的命令行行为。再检查实现里 `main()` 确实调用了新函数，避免仅新增一个闲置函数也误以为重构完成。

## 第三关 · 直接验证新函数的约定

在 `tests/test_question_content.py` 自己写三个测试，每个都直接调用新函数。

| 输入 | 要验证的结果 |
| --- | --- |
| 第一关的合法正文 | 返回类型是 `InterviewQuestion`，字段值与输入一致 |
| 一段普通文本 | `pytest.raises(json.JSONDecodeError)` 捕获正文解码异常 |
| 合法题目仅将 difficulty 改为 expert，再编码成 JSON 字符串 | `pytest.raises(ValidationError)` 捕获一条字段错误，位置是 `("difficulty",)`，类型为 `literal_error`。分别断言数量、位置和类型 |

这组测试只需构造字符串。Day 5 的流程测试负责构造完整 HTTP 响应，两组测试分别定位正文规则与调用流程的问题。

```bash
uv run python -m pytest -q
```

完成标准是原有 8 个测试与新增 3 个测试全部通过，并能指着代码解释普通文本和非法难度各自走了哪条错误路径。最后按实际结果填写学习记录，检查 diff，再提交当天成果。
