from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    api_name: str
    debug: bool = True
    model: Optional[str] = "o1"

class FileInfo(BaseModel):
    source: str
    title: str
    filename: str
    url: str
    original_url: str
    size_bytes: int

class SearchResponse(BaseModel):
    status: str
    substance: Optional[str] = None
    research_content: Optional[str] = None
    prompt_used: Optional[str] = None
    model_used: Optional[str] = None
    message: Optional[str] = None
    debug_info: Optional[dict] = None
    api_slug: Optional[str] = None
    pdf_summary_url: Optional[str] = None
    download_all_url: Optional[str] = None
    downloaded_files: List[dict] = []

class FilesListResponse(BaseModel):
    api_slug: str
    files: List[dict]
    download_all_url: str