import json

from app.resume_extraction import (
    ResumeExtractionError,
    extract_resume_profile,
)


source_text = """项目：简历预览工具。
我用 FastAPI 实现了文件上传，用 pytest 验证了空文件的处理。
接下来想学 Redis。"""


def main():
    try:
        result = extract_resume_profile(source_text)
    except ResumeExtractionError as exc:
        raise SystemExit(str(exc)) from None

    print("HTTP 状态码:", result.status_code)
    print("候选画像:")
    print(json.dumps(result.profile.model_dump(), ensure_ascii=False, indent=2))
    print("结束原因:", result.finish_reason)
    print("响应中的模型名:", result.model)
    print("Token 用量:", result.usage)


if __name__ == "__main__":
    main()