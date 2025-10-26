from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import os
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatIn(BaseModel):
    messages: List[Message]

class ChatOut(BaseModel):
    reply: str
    summary: str

SYSTEM_PROMPT_BG = (
    "Ти си LUNA — емпатичен HR асистент. Говориш кратко, приятелски и професионално. "
    "Отговаряй на български, когато входът е на български, иначе на английски."
)

INSTRUCTION = (
    "Върни резултат така:\nREPLY: <кратък отговор към кандидата>\nSUMMARY: <едно изречение за HR>"
)

def _parse(text: str):
    reply, summary = "", ""
    for line in text.splitlines():
        if line.strip().startswith("REPLY:"):
            reply = line.split("REPLY:",1)[1].strip()
        elif line.strip().startswith("SUMMARY:"):
            summary = line.split("SUMMARY:",1)[1].strip()
    return reply or text, summary or "Кратко обобщение не е открито."

@router.post("/luna/chat", response_model=ChatOut)
def luna_chat(data: ChatIn):
    api_key = os.environ.get("OPENAI_API_KEY","").strip()
    last_user = ""
    for m in reversed(data.messages):
        if m.role == "user":
            last_user = m.content; break
    if not api_key or OpenAI is None:
        return {"reply": f"Здравей! Благодаря ти. Разбирам: {last_user[:160]}...", "summary": "Демо режим."}
    try:
        client = OpenAI(api_key=api_key)
        msgs = [{"role":"system","content":SYSTEM_PROMPT_BG}]
        msgs += [{"role":m.role,"content":m.content} for m in data.messages]
        msgs.append({"role":"system","content":INSTRUCTION})
        r = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.3, max_tokens=300)
        text = r.choices[0].message.content or ""
        reply, summary = _parse(text)
        return {"reply": reply, "summary": summary}
    except Exception as e:
        return {"reply": f"Временен fallback. Прочит: {last_user[:160]}...", "summary": "AI повикът не успя."}
