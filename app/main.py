from typing import Annotated
from fastapi import FastAPI,Query,HTTPException,UploadFile

from pydantic import BaseModel,Field,ValidationError
from scripts.structured_question import InterviewQuestion,parse_question_content
from app.resume_text import decode_resume_text

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

@app.post("/resumes/preview")
async def preview_resume(file: UploadFile):
    filename = file.filename or ""
    if not filename.lower().endswith((".txt",".md")):
        raise HTTPException(status_code=415,detail="只支持 TXT 或 Markdown文件")
    limit = 256 * 1024
    raw = await file.read(limit + 1)
    if len(raw) > limit:
        raise HTTPException(status_code=413,detail="简历文件太大")
    try:
        text = decode_resume_text(raw)
    except UnicodeDecodeError:
        raise HTTPException(status_code=422,detail="请使用 UTF-8 编码保存简历") from None
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc))
    return {"filename": file.filename,"text": text}