def decode_resume_text(raw: bytes) -> str:
    text = raw.decode("utf-8-sig")
    if not text.strip():
        raise ValueError("简历正文为空")
    return text