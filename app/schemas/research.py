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
    api: str
    api_slug: Optional[str] = None
    message: Optional[str] = None
    total_found: Optional[int] = None
    total_relevant: Optional[int] = None
    total_downloaded: Optional[int] = None
    hits: List[FileInfo] = []
    download_all_url: Optional[str] = None
    debug_info: Optional[dict] = None

class FilesListResponse(BaseModel):
    api_slug: str
    files: List[dict]
    download_all_url: str