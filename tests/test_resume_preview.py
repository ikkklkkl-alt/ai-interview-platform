from fastapi.testclient import TestClient
from app.main import app

def test_preview_rejects_invalid_utf8():
    with TestClient(app) as client:
        response = client.post("/resumes/preview", files={"file": ("demo.txt",b"\xff","text/plain")},)

    assert response.status_code == 422
    assert response.json()["detail"] == "请使用 UTF-8 编码保存简历"


def test_preview_rejects_blank_resume():
    with TestClient(app) as client:
        response = client.post("/resumes/preview", files={"file": ("demo.txt",b"\n\t","text/plain")},)

    assert response.status_code == 422
    assert response.json()["detail"] == "简历正文为空"

def test_preview_returns_markdown_text():
    text = "# 项目经历\n    用 FastAPI 写过接口\n"
    raw = text.encode("utf-8-sig")

    with TestClient(app) as client:
        response = client.post("/resumes/preview", files={"file": ("demo.MD",raw,"text/markdown")},)

    assert response.status_code == 200
    assert response.json() == {"filename": "demo.MD","text": text}

def test_preview_rejects_unsupported_extension():
    text = "# 项目经历\n    用 FastAPI 写过接口\n"
    raw = text.encode("utf-8-sig")

    with TestClient(app) as client:
        response = client.post("/resumes/preview", files={"file": ("demo.pdf",raw,"text/markdown")},)

    assert response.status_code == 415
    assert response.json()["detail"] == "只支持 TXT 或 Markdown文件"

def test_preview_accepts_file_at_size_limit():
    raw = b"a" * (256 * 1024)

    with TestClient(app) as client:
        response = client.post("/resumes/preview", files={"file": ("demo.txt",raw,"text/plain")},)

    assert response.status_code ==200
    assert response.json()["text"] == raw.decode("ascii")

def test_preview_accepts_file_over_size_limit():
    raw = b"a" * (256 * 1024 + 1)

    with TestClient(app) as client:
        response = client.post("/resumes/preview", files={"file": ("demo.txt",raw,"text/plain")},)

    assert response.status_code ==413
    assert response.json()["detail"] == "简历文件太大"