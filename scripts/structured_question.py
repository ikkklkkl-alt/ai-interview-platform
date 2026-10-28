"""Day 4：按 docs/day-04.md 从本地校验开始练习结构化输出。"""
import json
import os

import httpx

from typing import Literal

from pydantic import BaseModel, ConfigDict,Field, ValidationError

class InterviewQuestion(BaseModel):
    """一道面试题的数据结构，字段由学习者补全。"""

    model_config = ConfigDict(extra="forbid",str_strip_whitespace=True,)

    question: str = Field(min_length=10,max_length=300)
    difficulty: Literal["easy","medium","hard"]
    knowledge_points: list[str] = Field(min_length=1,max_length=5)

    # TODO：声明 question、difficulty、knowledge_points 三个必填字段。
    pass

def main():
    api_key = os.getenv("DEEPSEEK_API_KEY","").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL","").strip()
    model = os.getenv("DEEPSEEK_MODEL","").strip()

    print("服务地址:",base_url)
    print("模型:",model)
    print("是否读到key:",bool(api_key))
    
    if not api_key:
            raise SystemExit("请在.env中填写DEEPSEEK_API_KEY")

    url = f"{base_url.rstrip('/')}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": 
                """你是 Python 面试官，生成一道入门面试题，不提供答案。
                只返回 JSON 对象，三个字段都必须提供，不允许额外字段：
                - question：字符串，长度为 10～300 个字符。
                - difficulty：只能是 "easy"、"medium" 或 "hard"。
                - knowledge_points：字符串列表，包含 1～5 个知识点。
                
                输出格式示例：
                {
                  "question": "Python 中列表和元组有什么区别？",
                  "difficulty": "easy",
                  "knowledge_points": ["列表", "元组", "可变性"]
                }
                """
            },

            {
                "role": "user",
                "content": "请出一道关于 Python 列表的面试题。"
            }
        ],
        "stream": False,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
        "max_tokens": 512
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

    try:
        response_data = response.json()
    except json.JSONDecodeError:
        raise SystemExit("接口响应不是有效的 JSON") from None
    if not isinstance(response_data,dict):
        raise SystemExit("接口响应结构异常：最外层应为对象")
    
    choices = response_data.get("choices")
    if not isinstance(choices,list) or not choices:
        raise SystemExit("接口没有返回可用的 choices 列表")

    choice =choices[0]
    if not isinstance(choice,dict):
        raise SystemExit("接口响应结构异常：第一个结果应为对象")

    finish_reason = choice.get("finish_reason")
    if finish_reason == "length":
        raise SystemExit("模型输出达到长度限制，内容可能被截断")
    if finish_reason != "stop":
        raise SystemExit(f"模型未正常结束，结束原因:{finish_reason}")

    message = choice.get("message")
    if not isinstance(message,dict):
        raise SystemExit("接口响应结构异常：message 应为对象")

    content = message.get("content")
    if not isinstance(content,str) or not content.strip():
        raise SystemExit("模型没有返回非空的文本内容")

    try:
        question_data = json.loads(content)
    except json.JSONDecodeError:
        raise SystemExit("模型返回的内容不是有效的 JSON") from None
    
    
    try:
        data = InterviewQuestion.model_validate(question_data)
    except ValidationError as exc:
        raise SystemExit(f"题目数据校验失败: \n{exc}") from None
    
    print("题目:",data.question)
    print("转成字典:",data.model_dump())
    
    print("结束原因：", finish_reason)
    print("响应中的模型名：", response_data.get("model"))
    print("Token 用量：", response_data.get("usage"))

if __name__ == "__main__":
    main()
