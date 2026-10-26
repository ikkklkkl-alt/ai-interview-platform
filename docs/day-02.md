# Day 2：岗位方向列表、查询参数与校验

开始日期：2026-10-26。按实际掌握程度推进，预计 3–4 小时。今天使用固定的练习数据，不需要模型 Key 或数据库。

## 今天要解决的业务问题

用户开始模拟面试前，需要选择岗位方向。我们先让后端提供一个岗位列表，未来前端就能用它生成选择框。

数据先保存在 Python 列表中。后续接入数据库时，可以替换数据来源，保留接口约定。

## 开始前（10 分钟）

```bash
cd /Users/k/Documents/deepseek-projects/ai-interview-learning
git status --short --branch
```

准备任务单会产生 README 和 docs 的变化，这是今天尚未提交的文档工作。先看懂这些变化，再开始写代码。

如果昨天的服务已停止，在一个终端启动：

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

如果服务仍运行，继续使用它。先访问 `/health`，确认原接口可用。

## 第一关：返回岗位列表（约 40 分钟）

在已有 `app/main.py` 中，继续使用现有的 `app`，新增一个 GET 接口。

| 项目 | 约定 |
| --- | --- |
| 方法 | GET |
| 路径 | `/interview-directions` |
| 请求参数 | 第一关没有参数 |
| 成功状态码 | 200 |
| 响应正文 | JSON 数组，每个元素是一份岗位方向信息 |

先使用以下三条练习数据，保持这个顺序：

```json
[
  {"code": "python-backend", "name": "Python 后端开发"},
  {"code": "frontend", "name": "前端开发"},
  {"code": "ai-application", "name": "AI 应用开发"}
]
```

`code` 用作稳定标识，后续请求可以通过它指定方向；`name` 用于页面展示。这些只是练习数据，不表示已经实现三种岗位的面试能力。

实现提示：

1. 在模块中定义岗位列表，例如命名为 `DIRECTIONS`，每项用一个字典表示。
2. 注册路由，函数名可以叫 `list_interview_directions`。
3. 返回 Python 列表，由 FastAPI 转成 JSON 数组。这里不需要先调用 `json.dumps()`。
4. 原有 `/health` 应继续工作。

验收：

```bash
curl -i http://127.0.0.1:8002/interview-directions
curl -i http://127.0.0.1:8002/health
```

也可以在 http://127.0.0.1:8002/docs 找到新接口并执行。

思考：昨天返回字典，今天返回列表，响应正文分别以 `{` 和 `[` 开头。这两种结构适合表达什么数据？如果你返回的是 `json.dumps()` 产生的字符串，会与直接返回列表有什么区别？

**建议在这一关完成后先进行一次代码审查，再继续加参数。**

## 第二关：用查询参数限制数量（约 40 分钟）

希望以下请求仅返回前两条岗位：

```text
/interview-directions?limit=2
```

路径仍然是 `/interview-directions`，问号后的 `limit=2` 是查询参数。多个查询参数通过 `&` 连接。不要把 `?limit=2` 写进路由装饰器的路径中。

先在处理函数中增加参数声明：

```python
limit: int = 3
```

这里仅展示函数形参写法：把它放进你现有函数的括号中。

- `limit` 是查询参数名。
- `int` 告诉 FastAPI 按整数解析。
- `3` 是调用者没有传参数时使用的默认值。

根据传入数量，返回列表的前若干条。你可以利用 Python 切片，注意返回新列表，不要删除原列表中的数据。

验收：

```bash
curl -i 'http://127.0.0.1:8002/interview-directions?limit=1'
curl -i 'http://127.0.0.1:8002/interview-directions?limit=2'
curl -i http://127.0.0.1:8002/interview-directions
```

URL 用引号包起来，可以避免 zsh 把 `?` 等符号当成文件匹配语法。最后一次不传参数仍然应返回三条，证明前面的请求没有破坏原始数据。

此时尝试 `limit=0`、`limit=-1`，先记录你观察到的结果。Python 切片接受这些值，但它们是否符合我们想表达的业务规则？

## 第三关：声明参数约束（约 40 分钟）

给 `limit` 增加明确规则：整数，默认 3，允许 1–10，范围外返回 422。

使用 `typing.Annotated` 和 FastAPI 的 `Query` 表达约束。参数声明的语法提示：

```python
from typing import Annotated
from fastapi import Query

# 放进现有处理函数的形参列表中：
# limit: Annotated[int, Query(ge=1, le=10)] = 3
```

`Annotated` 将类型与附加信息放在一起；这里的基础类型是 `int`，附加信息是查询参数的取值约束。`ge` 表示大于等于，`le` 表示小于等于。

先预测，再实际验证以下请求：

| 请求 | 预期 |
| --- | --- |
| 不传 `limit` | 200，返回三条 |
| `limit=1` | 200，只返回第一条 |
| `limit=2` | 200，返回前两条 |
| `limit=10` | 200，仍然只有现有的三条 |
| `limit=0` | 422 |
| `limit=-1` | 422 |
| `limit=11` | 422 |
| `limit=abc` | 422 |
| `POST /interview-directions` | 405 |
| `GET /does-not-exist` | 404 |

```bash
curl -i 'http://127.0.0.1:8002/interview-directions?limit=0'
curl -i 'http://127.0.0.1:8002/interview-directions?limit=abc'
```

观察错误正文中的 `detail`：问题发生在哪个参数，输入是什么，触发了哪项约束？不要只观察 422 这个数字。

为了理解执行顺序，可以临时在函数体第一行打印一条固定文字。分别发合法和非法请求，观察终端：框架在调用处理函数前会进行请求参数校验。观察后移除临时打印。

当前应用中，404 表示没有匹配的路径，405 表示该路径不支持请求方法，422 表示请求参数未通过校验。

## 选做：按关键词筛选（约 30 分钟）

前三关通过后，再增加可选查询参数 `keyword`。约定：

- 未传、空字符串或仅含空白时，不筛选。
- 关键词匹配 `code` 或 `name` 中的连续文字，忽略英文大小写。
- 保持原始数据顺序，先筛选，再按 `limit` 截取。
- 没有匹配项时返回 200 和 `[]`，因为接口仍存在，只是没有匹配的数据。

提示：可选字符串类型可以写成 `str | None`，默认 `None`；使用字符串去空白、大小写归一化、成员判断和列表推导式。自行组合这些操作。

```bash
curl -i 'http://127.0.0.1:8002/interview-directions?keyword=AI&limit=1'
curl -i 'http://127.0.0.1:8002/interview-directions?keyword=not-found'
curl -i --get --data-urlencode 'keyword=后端' http://127.0.0.1:8002/interview-directions
```

第一条应返回第三个方向 AI 应用开发，这可以帮助发现“先截取再筛选”的顺序问题。筛选之后重新访问不带参数的接口，仍应返回原来的三条。

## 复盘与当天提交（约 20–30 分钟）

在学习记录的 Day 2 中，用自己的话回答：

1. Python 列表如何成为 HTTP 响应正文中的 JSON 数组？
2. 路径和查询参数有什么区别？
3. URL 里的 `limit=2` 怎样变成函数收到的整数？
4. `int` 类型声明与 `ge`、`le` 范围约束分别解决什么问题？
5. 为什么 `limit=10` 返回三条，`limit=11` 却返回 422？
6. 今天哪个失败用例帮助你发现了问题？

更新 README 的实际进度后，检查改动、提交并推送。仅提交已经完成且验证过的功能；选做部分可以另做一次提交。

```bash
git status --short
git --no-pager diff
git add app/main.py README.md docs/day-02.md docs/learning-log.md
git --no-pager diff --cached --stat
git commit -m "feat: add interview directions with query validation"
git -c http.version=HTTP/1.1 push
```

沿用昨天验证过的 HTTP/1.1 临时设置；`-c` 只作用于这一条命令。首次推送已经建立分支跟踪关系，因此这里无需再次写 `-u origin main`。

## 参考资料

- [FastAPI：查询参数](https://fastapi.tiangolo.com/tutorial/query-params/)
- [FastAPI：Query、Annotated 与校验](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)
- [FastAPI：数值约束 ge / le](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/)

阅读与你当前关卡相关的内容，然后回到自己的项目练习。
