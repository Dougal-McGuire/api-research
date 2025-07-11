from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.api.main import router as main_router
import os

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

# Static files for frontend assets
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Serve frontend index.html for all non-API routes (SPA routing)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Check if the file exists in static directory
    file_path = os.path.join("static", full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # For all other routes, serve the React app's index.html (SPA routing)
    return FileResponse("static/index.html")