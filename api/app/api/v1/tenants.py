from fastapi import APIRouter
from pydantic import BaseModel, Field
import time

router = APIRouter()

class TenantIn(BaseModel):
    name: str = Field(..., min_length=2)
    admin_email: str
    plan: str = "Free"
    brand: str = "Premium Minimal (Mint)"

class TenantOut(BaseModel):
    id: int
    name: str
    subdomain: str
    plan: str
    created_at: float

TENANT_ID = 1

@router.post("/tenants", response_model=TenantOut)
def create_tenant(data: TenantIn):
    global TENANT_ID
    subdomain = f"{data.name.lower().replace(' ', '')}.hirehub.world"
    t = {"id": TENANT_ID, "name": data.name, "subdomain": subdomain, "plan": data.plan, "created_at": time.time()}
    TENANT_ID += 1
    return t
