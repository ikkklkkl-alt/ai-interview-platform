# Day 4：结构化面试题与 Pydantic 校验

开始日期：2026-10-28。今天的目标是让模型返回固定字段，并检查这些数据能否被程序使用。

Day 3 的真实调用已提交并推送，提交编号是 `965c27e`。今天继续使用独立脚本，先完成本地练习，再接模型。

## 准备情况

- 已将 Pydantic 声明为直接依赖，沿用环境中已有的 2.14.1 版本。
- `scripts/structured_question.py` 从练习骨架和手写样例开始，现已完成真实结构化调用及校验；下面保留分步过程供回顾。
- Day 3 的 `scripts/first_model_call.py` 保留，第三关可以参考其中的请求和异常处理。
- 当前完整脚本会调用真实模型，运行时使用 `--env-file .env`，不需要启动 Uvicorn。第一、二关的本地练习说明对应接入请求之前的版本。

## 今天最终要得到什么

下面是自己设计的题目格式，不是真实模型返回记录：

```json
{
  "question": "Python 中列表和元组有什么区别？",
  "difficulty": "easy",
  "knowledge_points": ["列表", "元组", "可变性"]
}
```

| 字段 | 类型与要求 |
| --- | --- |
| `question` | 字符串，长度 10～300 |
| `difficulty` | 只能是 `easy`、`medium`、`hard` 之一 |
| `knowledge_points` | 字符串列表，包含 1～5 个知识点 |

三个字段都必填。这些长度和数量是本练习自己制定的业务规则，后续可以调整。

## 第一关：先校验自己写的数据

预计 30～45 分钟。打开 `scripts/structured_question.py`，先补全 `InterviewQuestion` 类。

Pydantic 的 `BaseModel` 是用来定义数据结构的 Python 类，与 DeepSeek 这种大语言模型不是同一个概念。

第一个字段的提示：

```python
question: str = Field(min_length=10, max_length=300)
```

将它放进类里面，再自己写另外两个字段。用到的语法：

- `Literal["easy", "medium", "hard"]`：限定可接受的具体值。
- `list[str]`：元素是字符串的列表。
- 对列表使用 `Field(min_length=1, max_length=5)`：限制列表元素数量。

没有给默认值的字段需要调用方提供；`Field(min_length=...)` 也没有给字段设置默认值。[字段说明](https://docs.pydantic.dev/latest/concepts/fields/)

接着，在 `main()` 中用 `InterviewQuestion.model_validate(sample_data)` 得到校验后的对象，保存到变量里。打印：

1. 对象的 `question` 属性。
2. 对象的 `model_dump()` 结果。

`model_validate()` 接收 Python 数据并校验；`model_dump()` 将对象转成字典。[模型说明](https://docs.pydantic.dev/latest/concepts/models/)

第一关只含手写样例时，在学习目录运行：

```bash
uv run python scripts/structured_question.py
```

预期能看到题目和三个字段组成的字典。第一关完成后先检查一次，再继续。

## 第二关：故意给它错误的数据

预计 30～45 分钟。每次只改样例中的一处，先预测，再运行；验证完恢复正确样例。

| 修改 | 预期结果 |
| --- | --- |
| 删除 `difficulty` | 缺少必填字段 |
| 把 `difficulty` 改成 `expert` | 不在允许值中 |
| 把 `question` 改成空字符串 | 长度不够 |
| 把 `knowledge_points` 改成 `[]` | 列表元素太少 |
| 把 `knowledge_points` 改成字符串 `"列表"` | 类型不符合要求 |

这些问题会触发 `pydantic.ValidationError`。先读一次错误，找出字段位置和错误原因，再练习用 `try/except` 捕获它。脚本应提示并退出，不继续把不合格数据当作成功结果。

加一个小实验：给正确样例增加 `answer` 字段，观察默认行为。Pydantic 默认会忽略未声明的字段。如果希望发现多余字段，从 `pydantic` 导入 `ConfigDict`，在类内加入：

```python
model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

`extra="forbid"` 拒绝多余字段；`str_strip_whitespace=True` 去除字符串首尾空白。再验证多余字段和全为空格的题目是否被拒绝。[配置说明](https://docs.pydantic.dev/latest/api/config/)

当前对知识点列表只规定了元素类型和数量，还没有禁止空白知识点，也不能判断知识点是否准确。先知道这条边界；为每个知识点加非空约束可作为选做练习。

## 第三关：让真实模型输出这个格式

预计 45～60 分钟。本地校验通过后，保留类定义，将 `main()` 中的手写输入换成真实模型返回的内容。请求代码参考 Day 3，由自己迁移。

继续使用已有的 `.env`，保留 Key 检查、超时、HTTP 状态检查及错误处理。在 payload 中新增：

```python
"response_format": {"type": "json_object"}
```

自己写 system 提示词，明确要求：生成一道 Python 入门面试题，以 JSON 对象输出，只包含表格中的三个字段；说明类型、长度、数量与难度取值，并给出上面的 JSON 示例。user 消息指定本次考察主题。

保留 `stream=False` 和非思考模式，本次将 `max_tokens` 设为 512，给 JSON 留出输出空间。JSON 模式需要提示词明确提到 JSON，并给出示例；仍需检查空内容和输出截断。[DeepSeek JSON Output](https://api-docs.deepseek.com/guides/json_mode/)

今天先把解析过程拆开：

```text
HTTP 响应正文
    ↓ response.json()
包含 choices、usage 等字段的 Python 字典
    ↓ 取 choices[0].message.content
模型生成的 JSON 字符串
    ↓ json.loads(content)
题目数据的 Python 字典
    ↓ InterviewQuestion.model_validate(...)
校验后的面试题对象
```

需要导入 Python 自带的 `json`。`response.json()` 解析外层 HTTP 正文，并不会自动把 `content` 字符串再解析一遍。

完成请求部分后，以下命令会调用真实模型：

```bash
uv run --env-file .env python scripts/structured_question.py
```

打印通过校验的题目数据，同时保留 `finish_reason`、模型名和 Token 用量，方便记录真实结果。

## 第四关：区分失败发生在哪一步

预计 30～45 分钟。给处理流程补上检查，失败时明确提示并退出：

| 情况 | 处理方式 |
| --- | --- |
| 请求超时、连接失败、HTTP 错误 | 沿用 Day 3 的处理 |
| 外层响应不是 JSON | 捕获外层解析错误，提示响应格式异常 |
| 外层数据结构异常，如缺少结果或 choices 为空 | 检查结构再读取，提示没有可用的模型结果 |
| `finish_reason` 不是 `stop` | 本练习先停止处理；`length` 时提示可能被截断 |
| `content` 不是非空字符串 | 提示模型未返回可解析文本 |
| `json.loads()` 失败 | 捕获 `json.JSONDecodeError`，提示模型内容不是有效 JSON |
| 字段不符合要求 | 捕获 `ValidationError`，指出不合格的字段 |

先用本地样例或模拟响应验证失败情况，真实模型用于验证正常调用。不要在校验失败时凭空补题目或难度，也先不加自动重试。

JSON 模式解决输出格式问题，Pydantic 按你声明的规则校验数据；题目是否正确、难度是否合适，仍需要人检查。通过校验不代表语义一定正确。

## 本次实际结果

2026-10-28，学习者运行真实模型后返回的题目数据：

```json
{
  "question": "请解释 Python 列表的 append() 和 extend() 方法的区别，并举例说明。",
  "difficulty": "easy",
  "knowledge_points": ["列表方法", "append", "extend"]
}
```

响应中的模型名为 `deepseek-flash`，结束原因为 `stop`。输入 169、输出 52、总计 221 Token，缓存命中为 0，题目通过 Pydantic 校验。

助手另用假 Key 和模拟响应验证了 24 个场景，全部通过，覆盖成功路径、请求失败、响应结构异常、截断、正文解析和字段校验。这些检查在本地完成，没有额外调用模型；尚未整理成仓库内的自动化测试文件。

## 验收和提交

- 能解释 JSON 字符串、Python 字典、Pydantic 对象的区别。
- 能解释为什么今天有两次 JSON 解析。
- 本地正确样例通过，错误样例能定位到字段。
- 完成一次真实结构化调用，并记录结束原因和用量。
- 对空内容、截断和校验失败给出清楚提示。
- 更新 README 和学习记录，保留“小标题＋段落”的格式，如实记录 AI 辅助。

完成后由自己提交：

```bash
git add pyproject.toml uv.lock scripts/structured_question.py README.md docs/day-04.md docs/learning-log.md
git --no-pager diff --cached --stat
git commit -m "feat: validate structured interview questions"
git -c http.version=HTTP/1.1 push
git status --short --branch
```

如果仍需使用昨天的 Clash 代理，并确认它仍开启、端口仍为 7897，可以使用：

```bash
git -c http.proxy=http://127.0.0.1:7897 -c http.version=HTTP/1.1 push
```

## 选做：理解后再尝试

- 用 `model_validate_json(content)` 合并模型内容的 JSON 解析与校验，观察报错有何变化。
- 用 `model_json_schema()` 查看模型定义的数据规则。
- 给知识点列表的每个字符串增加非空限制。
