from fastapi import APIRouter
from .research import router as research_router
from .diagnostics import router as diagnostics_router

router = APIRouter()

# Include research endpoints
router.include_router(research_router, prefix="/research", tags=["research"])

# Include diagnostics endpoints
router.include_router(diagnostics_router, prefix="/diagnostics", tags=["diagnostics"])

@router.get("/")
async def api_root():
    return {"message": "api-research API is running"}

@router.get("/status")
async def api_status():
    return {"status": "ok", "message": "API is healthy"}