
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatIn(BaseModel):
    messages: List[Message]

class ChatOut(BaseModel):
    reply: str
    summary: str

@router.post("/luna/chat", response_model=ChatOut)
def luna_chat(data: ChatIn):
    latest = ""
    for m in data.messages[::-1]:
        if m.role == "user":
            latest = m.content
            break
    reply = "Здравей! Благодаря за информацията. Разказа ми: " + (latest[:160] + ("..." if len(latest)>160 else "")) + " 😊"
    summary = "Кандидатът спомена: " + (latest[:140] + ("..." if len(latest)>140 else ""))
    return {"reply": reply, "summary": summary}
