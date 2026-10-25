"""Day 1：请根据 docs/day-01.md，亲自实现第一个 HTTP 接口。"""

# TODO 1：从 fastapi 导入 FastAPI。
# TODO 2：创建一个 FastAPI 实例，变量名为 app。
# TODO 3：给 GET /health 注册处理函数。
# TODO 4：让函数返回 Python 字典 {"status": "ok"}。
# TODO 5：启动服务后，在浏览器和终端分别验证结果。
from fastapi import FastAPI

app = FastAPI()

@app.get("/health",status_code=200)


async def root():
    return {"status":"ok"}