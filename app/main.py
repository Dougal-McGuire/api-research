from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import router as main_router

app = FastAPI(title="api-research API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(main_router, prefix="/api")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "api-research API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}