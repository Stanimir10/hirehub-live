
from fastapi import FastAPI
from app.api.v1.tenants import router as tenants_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.luna import router as luna_router

app = FastAPI(title="HireHub API — Live Demo", version="0.3.0")

app.include_router(tenants_router, prefix="/v1")
app.include_router(metrics_router, prefix="/v1")
app.include_router(luna_router, prefix="/v1")

@app.get("/")
def root():
    return {"status":"ok","service":"hirehub-api-live"}
