import os
import zipfile
import tempfile
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse, PlainTextResponse
from pydantic import BaseModel
import logging

# Configure logging to show on console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

from app.schemas.research import SearchRequest, SearchResponse, FilesListResponse
from app.services.openai_research_service import OpenAIResearchService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global research service instance
research_service = None

async def get_research_service():
    global research_service
    if research_service is None:
        try:
            research_service = OpenAIResearchService()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAIResearchService: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": f"Service initialization failed: {str(e)}",
                    "error_type": type(e).__name__,
                    "debug_info": {
                        "working_directory": os.getcwd(),
                        "template_file_exists": os.path.exists("app/core/research_prompt_template.txt"),
                        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
                        "template_file_path": os.path.abspath("app/core/research_prompt_template.txt") if os.path.exists("app/core/research_prompt_template.txt") else "File not found"
                    }
                }
            )
    return research_service

@router.get("/health")
async def health_check():
    """
    Health check endpoint to diagnose production issues
    """
    import os
    import sys
    
    health_info = {
        "status": "healthy",
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "template_file_exists": os.path.exists("app/core/research_prompt_template.txt"),
        "template_file_path": os.path.abspath("app/core/research_prompt_template.txt"),
        "app_directory_contents": os.listdir("app") if os.path.exists("app") else "app directory not found",
        "core_directory_contents": os.listdir("app/core") if os.path.exists("app/core") else "app/core directory not found"
    }
    
    # Try to initialize the service to see what fails
    try:
        service = OpenAIResearchService()
        health_info["service_initialization"] = "success"
    except Exception as e:
        health_info["service_initialization"] = "failed"
        health_info["service_error"] = str(e)
        health_info["service_error_type"] = type(e).__name__
    
    return health_info

@router.get("/test-openai")
async def test_openai_connection():
    """
    Test OpenAI API connection
    """
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"status": "error", "message": "OPENAI_API_KEY not set"}
        
        client = OpenAI(api_key=api_key)
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        return {
            "status": "success", 
            "message": "OpenAI API connection successful",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"OpenAI API connection failed: {str(e)}",
            "error_type": type(e).__name__
        }

@router.post("/test-search")
async def test_search_simple():
    """
    Test search with a simple prompt to isolate the issue
    """
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        
        # Simple research prompt
        simple_prompt = "Research the drug ibuprofen. Provide a brief summary of its regulatory status."
        
        logger.info("Starting simple test search")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use faster model for testing
            messages=[{"role": "user", "content": simple_prompt}],
            max_tokens=500
        )
        
        return {
            "status": "success",
            "substance": "ibuprofen",
            "research_content": response.choices[0].message.content,
            "model_used": "gpt-3.5-turbo"
        }
    except Exception as e:
        logger.error(f"Error in test search: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Test search failed: {str(e)}",
            "error_type": type(e).__name__
        }

@router.post("/search")
async def search_pharmaceutical_documents(request: SearchRequest):
    """
    Research pharmaceutical substances using OpenAI's deep research capabilities
    """
    if not request.api_name or not request.api_name.strip():
        raise HTTPException(status_code=400, detail="API name is required")
    
    logger.info(f"Received research request for substance: {request.api_name}")
    
    try:
        logger.info(f"Starting research for: {request.api_name}")
        service = await get_research_service()
        logger.info(f"Service initialized successfully")
        
        result = await service.research_substance(request.api_name, debug=request.debug, model=request.model)
        logger.info(f"Research completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in research endpoint: {e}", exc_info=True)
        error_detail = {
            "error": str(e),
            "error_type": type(e).__name__,
            "debug_info": {
                "working_directory": os.getcwd(),
                "template_file_exists": os.path.exists("app/core/research_prompt_template.txt"),
                "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
                "request_data": {
                    "api_name": request.api_name,
                    "model": request.model,
                    "debug": request.debug
                }
            }
        }
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{api_slug}/files", response_model=FilesListResponse)
async def get_api_files(api_slug: str):
    """
    Get list of downloaded files for an API
    """
    try:
        service = await get_research_service()
        files = await service.get_api_files(api_slug)
        
        return FilesListResponse(
            api_slug=api_slug,
            files=files,
            download_all_url=f"/api/research/{api_slug}/download-all"
        )
        
    except Exception as e:
        logger.error(f"Error getting files for {api_slug}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get files: {str(e)}")

@router.get("/{api_slug}/download-all")
async def download_all_files(api_slug: str):
    """
    Download all files for an API as a ZIP archive including summary report
    """
    try:
        static_dir = "static/apis"
        download_dir = os.path.join(static_dir, api_slug)
        
        if not os.path.exists(download_dir):
            raise HTTPException(status_code=404, detail="No files found for this API")
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            raise HTTPException(status_code=404, detail="No PDF files found for this API")
        
        # Create ZIP file in memory
        zip_filename = f"{api_slug}_complete_research_package.zip"
        
        def generate_zip():
            with tempfile.NamedTemporaryFile() as tmp_file:
                with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for pdf_file in pdf_files:
                        file_path = os.path.join(download_dir, pdf_file)
                        # Use original filename in ZIP
                        zip_file.write(file_path, pdf_file)
                
                tmp_file.seek(0)
                return tmp_file.read()
        
        zip_data = generate_zip()
        
        return StreamingResponse(
            iter([zip_data]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ZIP for {api_slug}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP file: {str(e)}")

@router.get("/status/{api_slug}")
async def get_search_status(api_slug: str):
    """
    Get the status of a search (for future async implementation)
    """
    # For now, just check if files exist
    static_dir = "static"
    download_dir = os.path.join(static_dir, api_slug)
    
    if os.path.exists(download_dir):
        pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
        return {
            "status": "completed",
            "api_slug": api_slug,
            "file_count": len(pdf_files)
        }
    else:
        return {
            "status": "not_found",
            "api_slug": api_slug,
            "file_count": 0
        }

@router.delete("/{api_slug}")
async def delete_api_files(api_slug: str):
    """
    Delete all files for an API (cleanup endpoint)
    """
    try:
        static_dir = "static"
        download_dir = os.path.join(static_dir, api_slug)
        
        if not os.path.exists(download_dir):
            raise HTTPException(status_code=404, detail="No files found for this API")
        
        # Delete all files in the directory
        import shutil
        shutil.rmtree(download_dir)
        
        return {"message": f"All files for {api_slug} have been deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting files for {api_slug}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete files: {str(e)}")

class TemplateUpdateRequest(BaseModel):
    template: str

@router.get("/template")
async def get_prompt_template():
    """Get the current research prompt template"""
    try:
        service = await get_research_service()
        template = service.get_current_template()
        return {"template": template}
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

@router.put("/template")
async def update_prompt_template(request: TemplateUpdateRequest):
    """Update the research prompt template"""
    try:
        service = await get_research_service()
        success = service.update_prompt_template(request.template)
        if success:
            return {"message": "Template updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update template")
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")

@router.get("/models")
async def get_available_models():
    """Get available OpenAI models for chat/completion"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # List all available models
        models = client.models.list()
        
        # Extract model IDs and filter for chat/completion models
        model_ids = [model.id for model in models.data]
        
        # Filter for relevant chat models that support web search
        # Only models with -search-preview suffix support web search functionality
        chat_models = []
        web_search_capable_models = ['gpt-4o-mini-search-preview', 'gpt-4o-search-preview', 'o1', 'o1-mini', 'o1-preview', 'o3-mini']
        
        for model_id in sorted(model_ids):
            # Only include models that are known to support web search
            if model_id in web_search_capable_models:
                    # Create a user-friendly display name
                    display_name = model_id
                    description = ""
                    
                    if model_id == 'gpt-4o-mini-search-preview':
                        description = "Fast Web Search"
                    elif model_id == 'gpt-4o-search-preview':
                        description = "Advanced Web Search"
                    elif model_id == 'o1-mini':
                        description = "Reasoning + Web Search"
                    elif model_id == 'o1-preview':
                        description = "Deep Reasoning + Web Search"
                    elif model_id == 'o1':
                        description = "Latest Reasoning + Web Search"
                    elif model_id == 'o3-mini':
                        description = "Next-Gen Reasoning + Web Search"
                    
                    chat_models.append({
                        "id": model_id,
                        "name": display_name,
                        "description": description
                    })
        
        return {"models": chat_models}
        
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

# Health check for research service
@router.get("/health")
async def research_health():
    """Check if the research service is healthy"""
    try:
        # Basic health check - verify OpenAI API key is configured
        import os
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "status": "unhealthy", 
                "message": "OpenAI API key not configured"
            }
        
        return {"status": "healthy", "message": "OpenAI Research service is operational"}
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}

# Cleanup endpoint for service
@router.on_event("shutdown")
async def shutdown_research_service():
    global research_service
    if research_service:
        await research_service.close()