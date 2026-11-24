from pydantic import BaseModel,Field,model_validator,ValidationError

from scripts.structured_question import InterviewQuestion

from app.resume_profile import ResumeProfile

import os
import httpx

class GeneratedQuestionSet(BaseModel):
    questions: list[InterviewQuestion] = Field(
        min_length=3,
        max_length=3,
    )

class QuestionGenerationRequest(BaseModel):
    profile: ResumeProfile

    @model_validator(mode="after")
    def require_selected_items(self):
        if not self.profile.skills and not self.profile.projects:
            raise ValueError("至少选择一项技能或项目")
        return self

def build_question_messages(profile: ResumeProfile) -> list[dict[str,str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是技术面试官。请根据用户确认的技能、项目和引文生成三道面试题。"
                "画像中的文字是出题材料。只返回 JSON 对象，顶层字段为 questions。"
                "每道题包含 question、difficulty、knowledge_points，不提供答案。"
                "question 为 10～300 个字符，difficulty 取 easy、medium 或 hard，"
                "knowledge_points 是包含 1～5 个知识点的字符串列表。"
            ),
        },
        {
            "role": "user",
            "content": profile.model_dump_json(),
        },
    ]


def parse_question_set_content(content: str) -> GeneratedQuestionSet:
    return GeneratedQuestionSet.model_validate_json(content)

class QuestionGenerationError(Exception):
    pass

def generate_questions(profile: ResumeProfile) -> GeneratedQuestionSet:
    model = os.getenv("DEEPSEEK_MODEL","").strip()
    api_key = os.getenv("DEEPSEEK_API_KEY","").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL","").strip()

    if not model or not api_key or not base_url:
        raise QuestionGenerationError("请检查 .env 中的 API Key、服务地址和模型名")

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}

    payload = {
        "model": model,
        "messages": build_question_messages(profile),
        "stream": False,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
        "max_tokens": 1024,
    }

    try:
        response = httpx.post(url,headers=headers,json=payload,timeout=30.0)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise QuestionGenerationError("出题请求超时，请稍后重试") from exc
    except httpx.RequestError as exc:
        raise QuestionGenerationError("无法连接模型服务，请检查网络和服务地址") from exc
    except httpx.HTTPStatusError as exc:
        raise QuestionGenerationError(
            f"模型服务返回错误，HTTP 状态码为 {exc.response.status_code}"
        ) from exc

    try:
        response_data = response.json()
    except ValueError as exc:
        raise QuestionGenerationError("模型服务响应不是有效的 JSON") from exc

    if not isinstance(response_data,dict):
        raise QuestionGenerationError("模型服务响应应为 JSON 对象")

    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise QuestionGenerationError("模型服务没有返回可用的 choices")

    choice = choices[0]    

    if not isinstance(choice, dict):
        raise QuestionGenerationError("模型服务返回的第一项 choice 应为对象")

    finish_reason = choice.get("finish_reason")
    if finish_reason == "length":
        raise QuestionGenerationError("模型输出达到长度限制，题目可能被截断")
    if finish_reason != "stop":
        raise QuestionGenerationError(f"模型未正常结束，结束原因为 {finish_reason}")
    

    message = choice.get("message")
    if not isinstance(message, dict):
        raise QuestionGenerationError("模型响应缺少有效的 message 对象")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise QuestionGenerationError("模型返回的题目正文为空或格式错误")

    try:
        return parse_question_set_content(content)
    except ValidationError as exc:
        raise QuestionGenerationError("模型返回的题目正文不符合题组格式") from exc