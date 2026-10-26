from typing import Annotated
from fastapi import FastAPI,Query

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