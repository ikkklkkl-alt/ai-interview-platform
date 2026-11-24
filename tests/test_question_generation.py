from unittest.mock import Mock

from fastapi.testclient import TestClient

from app import main as api
from app import question_generation
from app.question_generation import GeneratedQuestionSet,QuestionGenerationError
from app.resume_profile import ResumeProfile

import httpx
import pytest
import json

def test_generate_rejects_empty_profile(monkeypatch):
    generate = Mock()
    monkeypatch.setattr(api, "generate_questions", generate)

    with TestClient(api.app) as client:
        response = client.post(
            "/questions/generate",
            json={"profile": {"skills": [], "projects": []}},
        )

    assert response.status_code == 422
    generate.assert_not_called()

def test_generate_returns_503_when_service_fails(monkeypatch):
    generate = Mock(side_effect=QuestionGenerationError("出题请求超时"))
    monkeypatch.setattr(api, "generate_questions", generate)

    profile = {
        "skills": [{"name": "FastAPI", "evidence": "我用 FastAPI 实现了文件上传"}],
        "projects": [],
    }
    with TestClient(api.app) as client:
        response = client.post("/questions/generate", json={"profile": profile})

    assert response.status_code == 503
    assert response.json() == {"detail": "面试题生成暂时不可用，请稍后重试"}
    generate.assert_called_once()

def test_generate_returns_questions_for_selected_profile(monkeypatch):
    profile = {
        "skills": [{"name": "FastAPI", "evidence": "我用 FastAPI 实现了文件上传"}],
        "projects": [],
    }
    sample = {
        "questions": [
            {"question": "你怎样用 FastAPI 接收上传的文件？", "difficulty": "easy", "knowledge_points": ["FastAPI"]},
            {"question": "收到一个空文件时你会怎样处理？", "difficulty": "easy", "knowledge_points": ["输入校验"]},
            {"question": "你会怎样限制单个上传文件的大小？", "difficulty": "medium", "knowledge_points": ["文件上传"]},
        ]
    }
    generate = Mock(return_value=GeneratedQuestionSet.model_validate(sample))
    monkeypatch.setattr(api, "generate_questions", generate)

    with TestClient(api.app) as client:
        response = client.post("/questions/generate", json={"profile": profile})

    assert response.status_code == 200
    assert response.json() == sample
    generate.assert_called_once_with(ResumeProfile.model_validate(profile))

def test_generate_rejects_empty_question_set(monkeypatch):
    profile = ResumeProfile.model_validate({
        "skills": [{"name": "FastAPI","evidence": "我用 FastAPI 实现了文件上传"}],
        "projects": [],
    })
    response = httpx.Response(
        200,
        request=httpx.Request("POST", "https://example.invalid/chat/completions"),
        json={"choices": [{
            "finish_reason": "stop",
            "message": {"content": '{"questions": []}'},
        }]},
    )
    monkeypatch.setattr(question_generation.httpx,"post",Mock(return_value=response))

    with pytest.raises(QuestionGenerationError,match="题目正文不符合题组格式"):
        question_generation.generate_questions(profile)

def test_generate_sends_selected_profile_and_returns_three_questions(monkeypatch):
    profile = ResumeProfile.model_validate({
        "skills": [{"name": "FastAPI","evidence": "我用 FastAPI 实现了文件上传"}],
        "projects": [],
    })
    sample = {
        "questions": [
            {"question": "你怎样用 FastAPI 接收上传的文件？", "difficulty": "easy", "knowledge_points": ["FastAPI"]},
            {"question": "收到一个空文件时你会怎样处理？", "difficulty": "easy", "knowledge_points": ["输入校验"]},
            {"question": "你会怎样限制单个上传文件的大小？", "difficulty": "medium", "knowledge_points": ["文件上传"]},
        ]
    }
    response = httpx.Response(
        200,
        request=httpx.Request("POST", "https://example.invalid/chat/completions"),
        json={"choices": [{
            "finish_reason": "stop",
            "message": {"content": json.dumps(sample,ensure_ascii=False)},
        }]},
    )
   

    post = Mock(return_value=response)
    monkeypatch.setattr(question_generation.httpx,"post",post)

    result = question_generation.generate_questions(profile)

    post.assert_called_once()
    messages = post.call_args.kwargs["json"]["messages"]
    assert json.loads(messages[1]["content"]) == profile.model_dump()
    assert result.model_dump() == sample