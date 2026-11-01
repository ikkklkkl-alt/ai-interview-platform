import json
from fastapi.testclient import TestClient
from app.main import app

def test_preview_valid_question():
    sample = {
        "question": "Python 中列表和字典如何查找元素?",
        "difficulty": "easy",
        "knowledge_points": ["列表","字典"],
    }

    with TestClient(app) as client:
        response = client.post(
            "/questions/preview",
            json={"content": json.dumps(sample,ensure_ascii=False)},
        )

    assert response.status_code == 200
    assert response.json() == sample

def test_preview_missing_content():
    with TestClient(app) as client:
        response = client.post("/questions/preview",json={})

    assert response.status_code == 422
    errors =response.json()["detail"]
    assert errors[0]["loc"] == ["body","content"]

def test_preview_rejects_invalid_json():
    with TestClient(app) as client:
        response = client.post(
            "/questions/preview",
            json={"content": "这是一道面试题"},
        )
    assert response.status_code == 422
    assert response.json()["detail"] == "题目正文不是有效的 JSON"

def test_preview_rejects_invalid_difficulty():
    sample = {
        "question": "Python 中列表和字典如何查找元素?",
        "difficulty": "expert",
        "knowledge_points": ["列表","字典"],
    }

    with TestClient(app) as client:
        response = client.post(
            "/questions/preview",
            json={"content": json.dumps(sample,ensure_ascii=False)},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "题目字段不符合规则"