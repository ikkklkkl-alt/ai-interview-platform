import json
import httpx
import pytest

from app import resume_extraction

def test_extracts_profile_from_supplied_text(monkeypatch,capsys):
    source_text = "我用 SQLite 保存面试记录。"
    sample = {
        "skills": [{"name": "SQLite","evidence":source_text}],
        "projects": [],
    }

    response_body = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": json.dumps(sample,ensure_ascii=False)
                },
            }
        ],
        "model": "mock-model",
        "usage": {"total_tokens": 12},
    }

    sent_texts = []

    def fake_post(url,**kwargs):
        sent_texts.append(kwargs["json"]["messages"][1]["content"])
        return httpx.Response(
            200,
            request=httpx.Request("POST",url),
            json=response_body,
        )

    monkeypatch.setattr(resume_extraction.httpx,"post",fake_post)

    result = resume_extraction.extract_resume_profile(source_text)

    assert sent_texts == [source_text]
    assert result.profile.model_dump() == sample
    assert result.usage == response_body["usage"]
    assert capsys.readouterr().out == ""

def test_extract_reports_timeout(monkeypatch):
    def fake_post(url,**kwargs):
        raise httpx.ReadTimeout("模拟请求超时")

    monkeypatch.setattr(resume_extraction.httpx,"post",fake_post)

    with pytest.raises(
        resume_extraction.ResumeExtractionError,
        match="请求超时",
    ):
        resume_extraction.extract_resume_profile(
            "我用 SQLite 保存面试记录。"
        )

def test_extract_rejects_truncated_response(monkeypatch,capsys):
    source_text = "我用 SQLite 保存面试记录。"
    sample = {
        "skills": [{"name": "SQLite","evidence":source_text}],
        "projects": [],
    }

    response_body = {
        "choices": [
            {
                "finish_reason": "length",
                "message": {
                    "content": json.dumps(sample,ensure_ascii=False)
                },
            }
        ],
        "model": "mock-model",
        "usage": {"total_tokens": 12},
    }

    sent_texts = []

    def fake_post(url,**kwargs):
        sent_texts.append(kwargs["json"]["messages"][1]["content"])
        return httpx.Response(
            200,
            request=httpx.Request("POST",url),
            json=response_body,
        )

    monkeypatch.setattr(resume_extraction.httpx,"post",fake_post)

    with pytest.raises(
        resume_extraction.ResumeExtractionError,
        match="内容可能被截断",
    ):
        resume_extraction.extract_resume_profile(source_text)

    assert sent_texts == [source_text]
    assert capsys.readouterr().out == ""


def test_extract_rejects_changed_evidence(monkeypatch,capsys):
    source_text = "我用 SQLite 保存面试记录。"
    sample = {
        "skills": [
            {
                "name": "SQLite",
                "evidence": "我用 SQLite 删除面试记录。",
            }
        ],
        "projects": [],
    }

    response_body = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": json.dumps(sample,ensure_ascii=False)
                },
            }
        ],
        "model": "mock-model",
        "usage": {"total_tokens": 12},
    }

    sent_texts = []

    def fake_post(url,**kwargs):
        sent_texts.append(kwargs["json"]["messages"][1]["content"])
        return httpx.Response(
            200,
            request=httpx.Request("POST",url),
            json=response_body,
        )

    monkeypatch.setattr(resume_extraction.httpx,"post",fake_post)

    with pytest.raises(
        resume_extraction.ResumeExtractionError,
        match="画像引文与原文不符，条目：SQLite",
    ):
        resume_extraction.extract_resume_profile(source_text)

    assert sent_texts == [source_text]
    assert capsys.readouterr().out == ""
