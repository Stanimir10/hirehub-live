from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .api.v1.auth import router as auth_router
from .api.v1.tenants import router as tenants_router
from .api.v1.metrics import router as metrics_router
from .api.v1.luna import router as luna_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="HireHub API — Live", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/v1")
app.include_router(tenants_router, prefix="/v1")
app.include_router(metrics_router, prefix="/v1")
app.include_router(luna_router, prefix="/v1")

@app.get("/")
def root():
    return {"ok": True, "service": "hirehub-api", "version": "1.0.0"}
