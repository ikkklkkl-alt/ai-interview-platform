"""Day 5 第三、四关：使用模拟响应测试调用流程。"""

import json

import httpx
import pytest

from scripts import structured_question


def test_main_prints_valid_question(monkeypatch, capsys):
    question_data = {
        "question": "Python 中列表和字典有什么区别?",
        "difficulty": "medium",
        "knowledge_points": ["列表","字典","索引方式"],
    }


    response_body = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": json.dumps(
                        question_data, ensure_ascii=False
                    )
                },
            }
        ],
        "model": "mock-response-model",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }
    calls = []

    def fake_post(url,**kwargs):
        calls.append({"url": url,"kwargs": kwargs})

        request = httpx.Request("POST",url)
        return httpx.Response(200,request=request,json=response_body,)

    monkeypatch.setattr(structured_question.httpx,"post",fake_post)

    structured_question.main()
    output = capsys.readouterr().out

    assert len(calls) == 1
    assert question_data["question"] in output
    assert response_body["model"] in output

    sent_request = calls[0]
    assert sent_request["url"] == ("https://example.invalid/chat/completions")
    assert sent_request["kwargs"]["json"]["response_format"]["type"] == "json_object"
    assert "stop" in output
    #构造完整响应，替换外部请求，调用 main 并检查打印结果。
    

def test_main_rejects_invalid_json(monkeypatch, capsys):
    response_body = {
        "choices":[
            {
                "finish_reason":"stop",
                "message":{"content":"这是一道关于Python的面试题"},
            }
        ],
    }
    def fake_post(url,**kwargs):
        request = httpx.Request("POST",url)
        return httpx.Response(200,request=request,json=response_body)
    monkeypatch.setattr(structured_question.httpx,"post",fake_post)

    with pytest.raises(SystemExit) as exc_info:
        structured_question.main()

    output = capsys.readouterr().out
    
    assert "模型返回的内容不是有效的 JSON" in exc_info.value.code
    assert exc_info.value.code != 0
    assert "转成字典:" not in output
    
    #外层响应合法，finish_reason 为 stop，content 使用普通文字。


def test_main_rejects_truncated_response(monkeypatch, capsys):
    question_data = {
        "question": "Python 中列表和字典有什么区别？",
        "difficulty": "medium",
        "knowledge_points": ["列表", "字典", "索引方式"],
    }
    response_body = {
        "choices":[
            {
            "finish_reason":"length",
            "message":{"content":json.dumps(question_data,ensure_ascii=False)},
            }
        ],
    }

    def fake_post(url,**kwargs):
        request = httpx.Request("POST",url)
        return httpx.Response(200,request=request,json=response_body)
    monkeypatch.setattr(structured_question.httpx,"post",fake_post)
    with pytest.raises(SystemExit) as exc_info:
        structured_question.main()

    output = capsys.readouterr().out

    assert "内容可能被截断" in exc_info.value.code
    assert exc_info.value.code != 0
    assert "转成字典:" not in output

    #使用完整的 JSON 正文，但将 finish_reason 设为 length。
