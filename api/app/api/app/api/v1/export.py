from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from ...db import SessionLocal
from ...models import Candidate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io, smtplib, os
from email.message import EmailMessage

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/candidates/{cid}/pdf")
def export_pdf(cid: int, db: Session = next(get_db())):
    c = db.query(Candidate).filter(Candidate.id==cid).first()
    if not c: raise HTTPException(404, "Not found")
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    y = h - 20*mm
    p.setFont("Helvetica-Bold", 16); p.drawString(20*mm, y, "HireHub — Candidate Report"); y -= 12*mm
    p.setFont("Helvetica", 11)
    p.drawString(20*mm, y, f"Name: {c.name}"); y -= 8*mm
    p.drawString(20*mm, y, f"Email: {c.email}"); y -= 8*mm
    p.drawString(20*mm, y, f"Role: {c.role}"); y -= 8*mm
    p.drawString(20*mm, y, f"Score: {c.score}/100"); y -= 8*mm
    p.drawString(20*mm, y, "Summary:"); y -= 7*mm
    text_obj = p.beginText(20*mm, y); text_obj.setFont("Helvetica", 10)
    for line in (c.summary or "").splitlines():
        text_obj.textLine(line)
    p.drawText(text_obj); y = text_obj.getY() - 6*mm
    p.drawString(20*mm, y, "Extracted CV:"); y -= 7*mm
    text_obj = p.beginText(20*mm, y); text_obj.setFont("Helvetica", 9)
    for line in (c.cv_text or "")[:6000].splitlines():
        text_obj.textLine(line[:120])
    p.drawText(text_obj)
    p.showPage(); p.save()
    pdf = buffer.getvalue(); buffer.close()
    headers = {"Content-Type":"application/pdf", "Content-Disposition":"attachment; filename=hirehub_report.pdf"}
    from starlette.responses import Response
    return Response(content=pdf, media_type="application/pdf", headers=headers)

def send_email_smtp(to_email: str, subject: str, body: str, attachment_bytes: bytes, filename: str):
    host = os.environ.get("SMTP_HOST","")
    port = int(os.environ.get("SMTP_PORT","587"))
    user = os.environ.get("SMTP_USER","")
    pwd  = os.environ.get("SMTP_PASS","")
    sender = os.environ.get("FROM_EMAIL", user or "noreply@hirehub.world")
    if not (host and user and pwd):
        raise RuntimeError("SMTP not configured")
    msg = EmailMessage(); msg["From"]=sender; msg["To"]=to_email; msg["Subject"]=subject
    msg.set_content(body)
    msg.add_attachment(attachment_bytes, maintype="application", subtype="pdf", filename=filename)
    with smtplib.SMTP(host, port) as s:
        s.starttls(); s.login(user, pwd); s.send_message(msg)

@router.get("/candidates/{cid}/send")
def send_report(cid: int, to: str, db: Session = next(get_db())):
    c = db.query(Candidate).filter(Candidate.id==cid).first()
    if not c: raise HTTPException(404, "Not found")
    # tiny pdf
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=A4); p.setFont("Helvetica",12)
    p.drawString(50,800,f"Candidate: {c.name}"); p.drawString(50,780,f"Score: {c.score}/100"); p.showPage(); p.save()
    pdf = buffer.getvalue(); buffer.close()
    try:
        send_email_smtp(to, f"HireHub Report — {c.name}", f"Auto-generated report for {c.name}", pdf, f"{c.name.replace(' ','_')}_report.pdf")
        return {"ok": True, "sent_to": to}
    except Exception as e:
        return {"ok": False, "error": str(e), "hint": "Set SMTP_* env vars to enable sending."}
