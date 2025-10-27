from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlalchemy.orm import Session
from ...db import SessionLocal
from ...models import Candidate
import os, io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        from pdfminer.high_level import extract_text
        with io.BytesIO(file_bytes) as f:
            return extract_text(f) or ""
    except Exception:
        return ""

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        import docx
        tmp = "/tmp/_tmp_docx.docx"
        with open(tmp, "wb") as t: t.write(file_bytes)
        d = docx.Document(tmp)
        return "\n".join([p.text for p in d.paragraphs])
    except Exception:
        return ""

def guess_and_extract(filename: str, content: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"): return extract_text_from_pdf(content)
    if name.endswith(".docx"): return extract_text_from_docx(content)
    try: return content.decode("utf-8", errors="ignore")
    except Exception: return ""

router = APIRouter()

class CandidateOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    tags: str
    score: int
    summary: str
    class Config: from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/candidates/import")
async def import_candidate(file: UploadFile = File(...)):
    content = await file.read()
    text = guess_and_extract(file.filename, content)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Не успях да извлека текст от файла.")
    return {"ok": True, "filename": file.filename, "text": text[:15000]}

class CandidateIn(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    cv_text: str = ""
    tags: Optional[List[str]] = []
    company_id: Optional[int] = None

def score_with_ai(cv_text: str, role: Optional[str]) -> (int, str):
    try:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY","").strip()
        if not api_key: raise RuntimeError("no key")
        client = OpenAI(api_key=api_key)
        prompt = "Role: " + (role or "unknown") + "\nCV:\n" + cv_text[:6000]
        msgs = [
            {"role":"system","content":"You are an HR assistant. Score the candidate 0-100 and give a one-sentence summary."},
            {"role":"user","content": prompt},
            {"role":"system","content":"Return exactly: SCORE:<0-100>\nSUMMARY:<one sentence>"}
        ]
        r = client.chat.completions.create(model="gpt-4o-mini", messages=msgs, temperature=0.2, max_tokens=80)
        text = r.choices[0].message.content or ""
        score, summary = 0, "No summary."
        for line in text.splitlines():
            if line.strip().upper().startswith("SCORE:"):
                digits = ''.join([ch for ch in line if ch.isdigit()])
                score = int(digits) if digits else 0
            if line.strip().upper().startswith("SUMMARY:"):
                summary = line.split(":",1)[1].strip()
        score = max(0, min(100, score))
        return score, summary
    except Exception:
        words = len(cv_text.split())
        base = 40 + min(50, words // 80)
        return max(0, min(100, base)), "Демо оценка по извлечен текст."

@router.post("/candidates", response_model=CandidateOut)
def create_candidate(data: CandidateIn, db: Session = next(get_db())):
    score, summary = score_with_ai(data.cv_text, data.role)
    tags = ",".join(data.tags or [])
    cid = data.company_id or 1
    c = Candidate(company_id=cid, name=data.name, email=data.email or "", role=data.role or "", tags=tags, score=score, summary=summary, cv_text=data.cv_text or "")
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.get("/candidates", response_model=list[CandidateOut])
def list_candidates(db: Session = next(get_db())):
    items = db.query(Candidate).order_by(Candidate.id.desc()).limit(200).all()
    return items
