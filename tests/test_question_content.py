import json
import pytest

from scripts.structured_question import InterviewQuestion,parse_question_content
from pydantic import ValidationError

def test_parse_valid_question_content():
    sample = {
        "question": "Python 中列表和字典有什么区别？",
        "difficulty": "medium",
        "knowledge_points": ["列表", "字典"],
    }

    content = json.dumps(sample,ensure_ascii=False)
    question = parse_question_content(content)


    assert isinstance(question,InterviewQuestion)
    assert question.model_dump() == sample

def test_parse_invalid_json_content():
    with pytest.raises(json.JSONDecodeError):
        parse_question_content("这是一道面试题")


def test_parse_invalid_difficulty():
    sample = {
        "question": "Python 中列表和字典有什么区别？",
        "difficulty": "expert",
        "knowledge_points": ["列表", "字典"],
    }
    content = json.dumps(sample,ensure_ascii=False)
    with pytest.raises(ValidationError) as exc_info:
        parse_question_content(content)

    errors = exc_info.value.errors()

    assert len(errors) == 1
    assert errors[0]["loc"] == ("difficulty",)
    assert errors[0]["type"] == "literal_error"

