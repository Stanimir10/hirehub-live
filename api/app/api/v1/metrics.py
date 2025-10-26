from fastapi import APIRouter
router = APIRouter()

@router.get("/metrics")
def metrics():
    return {"companies": 1, "users": 1, "ai_analyses": 42, "mrr_bgn": 0}
