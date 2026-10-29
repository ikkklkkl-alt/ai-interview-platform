"""Day 5 第一、二关：面试题字段校验测试。"""

import pytest
from pydantic import ValidationError

from scripts.structured_question import InterviewQuestion


def test_valid_question():
    sample_data = {
        "question": "Python 中列表和元组有什么区别？",
        "difficulty": "easy",
        "knowledge_points": ["列表", "元组", "可变性"],
    }
    question = InterviewQuestion.model_validate(sample_data)

    assert question.question == "Python 中列表和元组有什么区别？"
    assert question.difficulty == "easy"
    assert question.knowledge_points == ["列表", "元组", "可变性"]
    # 调用 model_validate，检查题目、难度和知识点是否符合预期。


def test_invalid_difficulty():
    sample_data = {
        "question": "Python 中列表和元组有什么区别？",
        "difficulty": "expert",
        "knowledge_points": ["列表", "元组", "可变性"],
    }
    with pytest.raises(ValidationError) as exc_info:
        InterviewQuestion.model_validate(sample_data)

    errors = exc_info.value.errors()

    assert len(errors) == 1
    assert errors[0]["loc"] == ("difficulty",)
    assert errors[0]["type"] == "literal_error"

    # 构造 difficulty 为 expert 的数据，检查异常字段和错误类型。


def test_missing_difficulty():
    sample_data = {
        "question": "Python 中列表和元组有什么区别？",
        "knowledge_points": ["列表", "元组", "可变性"],
    }
    with pytest.raises(ValidationError) as exc_info:
        InterviewQuestion.model_validate(sample_data)

    errors = exc_info.value.errors()

    assert len(errors) == 1
    assert errors[0]["loc"] == ("difficulty",)
    assert errors[0]["type"] == "missing"


def test_blank_question():
    sample_data = {
        "question": "            ",
        "difficulty": "easy",
        "knowledge_points": ["列表", "元组", "可变性"],
    }
    with pytest.raises(ValidationError) as exc_info:
        InterviewQuestion.model_validate(sample_data)

    errors = exc_info.value.errors()

    assert len(errors) == 1
    assert errors[0]["loc"] == ("question",)
    assert errors[0]["type"] == "string_too_short"


def test_extra_field():
    sample_data = {
        "question": "Python 中列表和元组有什么区别？",
        "difficulty": "easy",
        "knowledge_points": ["列表", "元组", "可变性"],
        "answer": "测试一下",
    }
    with pytest.raises(ValidationError) as exc_info:
        InterviewQuestion.model_validate(sample_data)

    errors = exc_info.value.errors()

    assert len(errors) == 1
    assert errors[0]["loc"] == ("answer",)
    assert errors[0]["type"] == "extra_forbidden"
