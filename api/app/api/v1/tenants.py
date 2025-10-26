
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
import time

router = APIRouter()

class TenantIn(BaseModel):
    name: str = Field(..., min_length=2)
    admin_email: str
    plan: str = "Free"
    brand: str = "Premium Minimal (Blue)"

class TenantOut(BaseModel):
    id: int
    name: str
    subdomain: str
    plan: str
    created_at: float

TENANTS = []
TENANT_ID = 1

@router.post("/tenants", response_model=TenantOut)
def create_tenant(data: TenantIn):
    global TENANT_ID
    sub = data.name.lower().replace(" ", "").replace("&","and")
    subdomain = f"{sub}.hirehub.app"
    t = {"id": TENANT_ID, "name": data.name, "subdomain": subdomain, "plan": data.plan, "created_at": time.time()}
    TENANTS.append(t)
    TENANT_ID += 1
    return t

@router.get("/tenants", response_model=List[TenantOut])
def list_tenants():
    return TENANTS
