from typing import Annotated
from fastapi import FastAPI,Query,HTTPException

from pydantic import BaseModel,Field,ValidationError
from scripts.structured_question import InterviewQuestion,parse_question_content

import json

app = FastAPI()

@app.get("/health",status_code=200)


async def root():
    return {"status":"ok"}

directions = [
  {"code": "python-backend", "name": "Python 后端开发"},
  {"code": "frontend", "name": "前端开发"},
  {"code": "ai-application", "name": "AI 应用开发"}
]

@app.get("/interview-directions",status_code=200)
def list_interview_directions(limit: Annotated[int,Query(ge=1,le=10)] = 3):
    return directions[:limit]

class QuestionPreviewRequest(BaseModel):
    content: str = Field(min_length=1)

@app.post("/questions/preview",response_model=InterviewQuestion)
def preview_question(payload: QuestionPreviewRequest):
    try:
        return parse_question_content(payload.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422,detail="题目正文不是有效的 JSON",) from None
    except ValidationError:
        raise HTTPException(status_code=422,detail="题目字段不符合规则")