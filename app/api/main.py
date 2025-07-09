from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def api_root():
    return {"message": "api-research API is running"}

@router.get("/status")
async def api_status():
    return {"status": "ok", "message": "API is healthy"}