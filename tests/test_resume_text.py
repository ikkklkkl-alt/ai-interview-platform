import pytest

from app.resume_text import decode_resume_text

def test_decode_resume_text_preserves_formatting():
    text = "    项目经历\n用 FastAPI 写过接口\n"
    assert decode_resume_text(text.encode("utf-8")) == text
    assert decode_resume_text(text.encode("utf-8-sig")) == text

def test_decode_resume_text_rejects_invalid_utf8():
    with pytest.raises(UnicodeDecodeError):
        decode_resume_text(b"\xff")

def test_decode_resume_text_rejects_blank_text():
    with pytest.raises(ValueError, match="简历正文为空"):
        decode_resume_text(b"\n\t")