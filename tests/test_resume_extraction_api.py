from fastapi.testclient import TestClient

from app import main as api
from app.resume_extraction import ResumeExtractionResult,ResumeExtractionError

def test_extract_returns_profile(monkeypatch):
    source_text = "  我用 FastAPI 实现了文件上传。\n"
    sample = {
        "skills": [
            {"name": "FastAPI","evidence": "我用 FastAPI 实现了文件上传。"}
        ],
        "projects": [],
    }
    received_texts = []

    def fake_extract(text):
        received_texts.append(text)
        return ResumeExtractionResult(
            profile=sample,
            status_code=200,
            finish_reason="stop",
            model="mock-model",
            usage={"total_tokens": 12},
        )

    monkeypatch.setattr(api,"extract_resume_profile",fake_extract)

    with TestClient(api.app) as client:
        response = client.post(
            "/resumes/extract",
            json={"text": source_text},
        )

    assert response.status_code == 200
    assert response.json() == sample
    assert received_texts == [source_text]

def test_extract_returns_503_when_extraction_fails(monkeypatch):
    def fake_extract(text):
        raise ResumeExtractionError("请求超时，请稍后再试")

    monkeypatch.setattr(api,"extract_resume_profile",fake_extract)

    with TestClient(api.app) as client:
        response = client.post(
            "/resumes/extract",
            json={"text": "我用 FastAPI 实现了文件上传。"}
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "简历画像提取暂时不可用，请稍后重试"}


def test_extract_rejects_missing_text(monkeypatch):
    received_texts = []

    def fake_extract(text):
        received_texts.append(text)
        raise AssertionError("缺少正文时，不应该调用提取函数")

    monkeypatch.setattr(api,"extract_resume_profile",fake_extract)

    with TestClient(api.app) as client:
        response = client.post("/resumes/extract",json={})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body","text"]
    assert received_texts == []


def test_extract_rejects_empty_text(monkeypatch):
    received_texts = []

    def fake_extract(text):
        received_texts.append(text)
        raise AssertionError("缺少正文时，不应该调用提取函数")

    monkeypatch.setattr(api,"extract_resume_profile",fake_extract)

    with TestClient(api.app) as client:
        response = client.post("/resumes/extract",json={"text": ""})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body","text"]
    assert received_texts == []

def test_extract_rejects_blank_text(monkeypatch):
    received_texts = []

    def fake_extract(text):
        received_texts.append(text)
        raise AssertionError("缺少正文时，不应该调用提取函数")

    monkeypatch.setattr(api,"extract_resume_profile",fake_extract)

    with TestClient(api.app) as client:
        response = client.post("/resumes/extract",json={"text": " \n\t"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body","text"]
    assert received_texts == []