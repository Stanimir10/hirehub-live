from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ...db import SessionLocal, engine
from ...models import User, Company
from ...auth import hash_password, verify_password, make_token

router = APIRouter()

class RegisterIn(BaseModel):
    company_name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing_c = db.query(Company).filter(Company.name == data.company_name).first()
    if existing_c:
        raise HTTPException(status_code=400, detail="Company already exists")
    sub = data.company_name.lower().replace(" ", "")
    company = Company(name=data.company_name, subdomain=f"{sub}.hirehub.world", plan="Free")
    db.add(company); db.flush()
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password), role="admin", company_id=company.id)
    db.add(user); db.commit()
    token = make_token(user.id, user.email)
    return {"token": token, "company": {"id": company.id, "name": company.name, "subdomain": company.subdomain}}

@router.post("/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token(user.id, user.email)
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": user.role}}
