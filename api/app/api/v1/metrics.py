
from fastapi import APIRouter
from typing import Dict

router = APIRouter()

STATE = {
    "companies": 3,
    "users": 12,
    "ai_analyses": 19,
    "mrr_bgn": 349
}

@router.get("/metrics", response_model=Dict[str,int])
def metrics():
    return STATE
