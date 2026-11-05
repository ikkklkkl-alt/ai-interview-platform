import pytest
import json

from pydantic import ValidationError
from app.resume_profile import ResumeProfile,check_profile_evidence,parse_profile_content

def test_rejects_skill_evidence_missing_from_source():
    source_text = "我用 FastAPI 实现了文件上传。"

    profile = ResumeProfile.model_validate({
        "skills": [{"name": "FastAPI",
                    "evidence":"我用 FastAPI 实现了文件下载。"}],
        "projects": [],
    })

    with pytest.raises(ValueError,match="FastAPI"):
        check_profile_evidence(profile,source_text)

def test_accepts_skill_evidence_found_in_source():
    source_text = "我用 FastAPI 实现了文件上传。"

    profile = ResumeProfile.model_validate({
        "skills": [{"name": "FastAPI",
                    "evidence":"我用 FastAPI 实现了文件上传。"}],
        "projects": [],
    })

    assert profile.skills[0].name == "FastAPI"
    assert profile.skills[0].evidence == source_text

    assert check_profile_evidence(profile,source_text) is None

def test_accept_empty_profile():
    data = {"skills": [], "projects": []}

    profile = ResumeProfile.model_validate(data)

    assert profile.model_dump() == data

def test_rejects_missing_skills():
    data = {"projects": []}

    with pytest.raises(ValidationError) as exc:
        ResumeProfile.model_validate(data)

    error = exc.value.errors()[0]
    assert error["loc"] == ("skills",)
    assert error["type"] == "missing"

def test_rejects_blank_skill_evidence():
    data = {"skills": [{"name": "FastAPI","evidence":"   "}],
            "projects": [],}

    with pytest.raises(ValidationError) as exc:
        ResumeProfile.model_validate(data)

    error = exc.value.errors()[0]
    assert error["loc"] == ("skills",0,"evidence")
    assert error["type"] == "string_too_short"

def test_parse_valid_profile_content():
    source_text = "我用 FastAPI 实现了文件上传。"
    sample = {
        "skills": [{"name": "FastAPI","evidence": source_text}],
        "projects": [],
    }

    content = json.dumps(sample,ensure_ascii=False)
    profile = parse_profile_content(content,source_text)

    assert isinstance(profile,ResumeProfile)
    assert profile.model_dump() == sample

def test_parse_invalid_profile_json():
    source_text = "我用 FastAPI 实现了文件上传。"

    with pytest.raises(json.JSONDecodeError):
        parse_profile_content("这是一份简历画像",source_text)

def test_parse_profile_missing_skills():
    source_text = "我用 FastAPI 实现了文件上传。"
    content = json.dumps({"projects": []})
    with pytest.raises(ValidationError) as exc:
        parse_profile_content(content,source_text)
    error = exc.value.errors()[0]
    assert error["loc"] == ("skills",)
    assert error["type"] == "missing"

def test_parse_profile_rejects_changed_evidence():
    source_text = "我用 FastAPI 实现了文件上传。"
    sample = {
        "skills": [{"name": "FastAPI","evidence": "我用 FastAPI 实现了文件下载。"}],
        "projects": [],
    }

    content = json.dumps(sample,ensure_ascii=False)
    with pytest.raises(ValueError,match="FastAPI"):
        parse_profile_content(content,source_text)