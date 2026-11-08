import pytest

from app.resume_extraction import ResumeExtractionError,ResumeExtractionResult
from scripts import extract_resume_profile as cli

def test_main_exits_when_extraction_fails(monkeypatch,capsys):
    def fake_extract(source_text):
        assert source_text == cli.source_text
        raise ResumeExtractionError("请求超时，请稍后再试")

    monkeypatch.setattr(cli,"extract_resume_profile",fake_extract)

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == "请求超时，请稍后再试"
    assert capsys.readouterr().out == ""

def test_main_prints_extraction_result(monkeypatch,capsys):
    result = ResumeExtractionResult(
        profile={
            "skills": [
                {"name": "FastAPI","evidence": "我用 FastAPI 实现了文件上传。"}
            ],
            "projects": [],
        },
        status_code=200,
        finish_reason="stop",
        model="mock-model",
        usage={"total_tokens": 12},
    )
    def fake_extract(source_text):
        assert source_text == cli.source_text
        return result

    monkeypatch.setattr(cli,"extract_resume_profile",fake_extract)

    cli.main()
    output = capsys.readouterr().out

    assert "FastAPI" in output
    assert "mock-model" in output
    assert "结束原因: stop" in output
    assert "'total_tokens': 12" in output
