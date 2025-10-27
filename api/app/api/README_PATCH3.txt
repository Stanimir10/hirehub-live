Merge instructions for backend:
- Add new routers in app/main.py:
    from app.api.v1.candidates import router as candidates_router
    from app.api.v1.export import router as export_router
    app.include_router(candidates_router, prefix="/v1")
    app.include_router(export_router, prefix="/v1")
- Replace app/models.py with included file (adds Candidate).
- Ensure requirements.txt includes: python-docx, pdfminer.six, reportlab.
- Deploy with "Clear build cache & deploy".
