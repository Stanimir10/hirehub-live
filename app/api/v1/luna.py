from fastapi import APIRouter, HTTPException
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
    "Ако кандидатът споделя лични данни, не ги съхранявай, а само обобщи умения и опит. "
    "Отговаряй на български, когато входът е на български, иначе на английски."
)

INSTRUCTION = (
    "Върни резултат в следния формат (без други символи):\n"
    "REPLY: <кратък приятелски отговор към кандидата>\n"
    "SUMMARY: <едно изречение обобщение за HR>"
)

def _parse_model_output(text: str):
    reply, summary = "", ""
    for line in text.splitlines():
        if line.strip().startswith("REPLY:"):
            reply = line.split("REPLY:",1)[1].strip()
        elif line.strip().startswith("SUMMARY:"):
            summary = line.split("SUMMARY:",1)[1].strip()
    if not reply:
        reply = text.strip()
    if not summary:
        summary = "Кратко обобщение не е открито."
    return reply, summary

@router.post("/luna/chat", response_model=ChatOut)
def luna_chat(data: ChatIn):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if OpenAI is None or not api_key:
        latest_user = ""
        for m in reversed(data.messages):
            if m.role == "user":
                latest_user = m.content
                break
        reply = "Здравей! Благодаря ти за информацията. Разбирам следното: " + (latest_user[:200] + ("..." if len(latest_user) > 200 else "")) + " 😊"
        summary = "Демо режим: извлечен е текст от кандидата."
        return {"reply": reply, "summary": summary}

    try:
        client = OpenAI(api_key=api_key)
        msgs = [{"role":"system","content":SYSTEM_PROMPT_BG}]
        for m in data.messages:
            role = "user" if m.role not in ("user","assistant") else m.role
            msgs.append({"role": role, "content": m.content})
        msgs.append({"role":"system","content":INSTRUCTION})

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            temperature=0.3,
            max_tokens=300
        )
        text = resp.choices[0].message.content or ""
        reply, summary = _parse_model_output(text)
        return {"reply": reply, "summary": summary}
    except Exception as e:
        latest_user = ""
        for m in reversed(data.messages):
            if m.role == "user":
                latest_user = m.content
                break
        reply = "Здравей! Благодаря ти за информацията. Ето кратък прочит: " + (latest_user[:200] + ("..." if len(latest_user) > 200 else "")) + " 😊"
        summary = "Временен fallback (неуспешен AI повик)."
        return {"reply": reply, "summary": summary}
