from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    subdomain = Column(String, unique=True, index=True)
    plan = Column(String, default="Free")
    users = relationship("User", back_populates="company")
    candidates = relationship("Candidate", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="admin")
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="users")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String, index=True)
    email = Column(String, index=True)
    role = Column(String, index=True)
    tags = Column(String, default="")
    score = Column(Integer, default=0)
    summary = Column(Text, default="")
    cv_text = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    company = relationship("Company", back_populates="candidates")
