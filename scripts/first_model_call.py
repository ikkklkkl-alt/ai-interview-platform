"""Day 3：按 docs/day-03.md 逐步完成第一次模型调用。"""

import os

import httpx


def main():
    api_key = os.getenv("DEEPSEEK_API_KEY","").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL","").strip()
    model = os.getenv("DEEPSEEK_MODEL","").strip()

    print("服务地址:",base_url)
    print("模型:",model)
    print("是否读到key:",bool(api_key))
    
    if not api_key:
        raise SystemExit("请在.env中填写DEEPSEEK_API_KEY")
    

    # 第一关：读取三个环境变量，打印地址、模型名和是否读到了 Key。
    # Key 为空时给出提示并退出，不打印 Key 本身。

    url = f"{base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是 Python 面试官，只出一道入门题，不提供答案。"
            },
            {
                "role": "user",
                "content": "请出一道关于 Python 列表的面试题。"
            }
        ],
        "stream": False,
        "thinking": {"type": "disabled"},
        "max_tokens": 256
    }
    try:
        response = httpx.post(
            url,
            headers=headers,
            json=payload,
            timeout=30.0
            )
        print("HTTP状态码:",response.status_code)
        response.raise_for_status()

    except httpx.TimeoutException:
        raise SystemExit("请求超时，请稍后再试") from None

    except httpx.RequestError:
        raise SystemExit("请求发送失败，请检查网络和服务地址") from None

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        raise SystemExit(f"模型服务返回错误，HTTP状态码:{status_code}") from None

    data = response.json()
    choice = data["choices"][0]
    message = choice["message"]
    print("模型回答:",message["content"])
    print("结束原因:",choice["finish_reason"])
    print("响应中的模型名:",data.get("model"))
    print("Token 用量:",data.get("usage"))

        # 第二关：组装 URL、headers 和 payload，发送一次有超时的 POST 请求。
        # 先检查 HTTP 状态，再把响应正文解析成 Python 数据。

        # 第三关：取出回答正文、结束原因与用量信息，处理常见调用错误。
    pass


if __name__ == "__main__":
    main()
