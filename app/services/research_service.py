import os
import asyncio
from typing import List, Dict, Optional
import re
import logging
from pathlib import Path

from .openai_service import OpenAIService
from .web_service import WebExplorationService
from .pdf_service import PDFService

logger = logging.getLogger(__name__)

class ResearchService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.web_service = WebExplorationService()
        self.pdf_service = PDFService()
        self.resources_file = "app/core/research_resources.txt"
        self.static_dir = "static"
    
    async def search_pharmaceutical_documents(self, api_name: str) -> Dict:
        """
        Main orchestration method for pharmaceutical document search
        """
        try:
            # Clean and normalize API name
            clean_api_name = self._clean_api_name(api_name)
            api_slug = self._create_api_slug(clean_api_name)
            
            logger.info(f"🔍 Starting search for pharmaceutical API: {clean_api_name}")
            logger.info(f"📂 API slug: {api_slug}")
            
            # Load research sources
            sources = self._load_research_sources()
            source_names = list(sources.keys())
            logger.info(f"📋 Loaded {len(sources)} research sources: {', '.join(source_names)}")
            
            # Step 1: Generate search queries using OpenAI
            logger.info("🤖 Step 1: Generating search queries using OpenAI...")
            search_plan = await self.openai_service.plan_search_queries(clean_api_name, source_names)
            search_queries = search_plan.get("search_queries", {})
            logger.info(f"✅ Generated search queries for {len(search_queries)} sources")
            for source, query in search_queries.items():
                logger.info(f"  - {source}: {query}")
            
            # Step 2: Discover PDF links from web sources
            logger.info("🌐 Step 2: Discovering PDF documents from regulatory sources...")
            pdf_candidates = await self.web_service.discover_pdf_links(search_queries, clean_api_name)
            
            logger.info(f"📄 Found {len(pdf_candidates)} PDF candidates total")
            if pdf_candidates:
                for i, pdf in enumerate(pdf_candidates[:5]):  # Show first 5
                    logger.info(f"  [{i+1}] {pdf['source']}: {pdf['title'][:50]}...")
                if len(pdf_candidates) > 5:
                    logger.info(f"  ... and {len(pdf_candidates) - 5} more")
            
            if not pdf_candidates:
                logger.warning("❌ No PDF documents found in any source")
                return {
                    "status": "completed",
                    "api": clean_api_name,
                    "message": "No PDF documents found",
                    "hits": [],
                    "debug_info": {
                        "sources_searched": source_names,
                        "search_queries": search_queries,
                        "pdf_candidates_found": 0
                    }
                }
            
            # Step 3: Filter PDFs for relevance using OpenAI
            logger.info("🔬 Step 3: Filtering PDFs for relevance using AI...")
            relevant_pdfs = await self._filter_relevant_pdfs(pdf_candidates, clean_api_name)
            
            logger.info(f"✅ Found {len(relevant_pdfs)} relevant PDFs after filtering")
            
            if not relevant_pdfs:
                logger.warning("❌ No relevant PDF documents found after AI filtering")
                return {
                    "status": "completed",
                    "api": clean_api_name,
                    "message": "No relevant PDF documents found after filtering",
                    "hits": [],
                    "debug_info": {
                        "sources_searched": source_names,
                        "search_queries": search_queries,
                        "pdf_candidates_found": len(pdf_candidates),
                        "relevant_pdfs_found": 0
                    }
                }
            
            # Step 4: Download and store PDFs
            download_dir = os.path.join(self.static_dir, api_slug)
            os.makedirs(download_dir, exist_ok=True)
            
            logger.info(f"⬇️ Step 4: Downloading {len(relevant_pdfs)} PDFs to {download_dir}...")
            downloaded_files = await self._download_pdfs(relevant_pdfs, download_dir)
            
            logger.info(f"💾 Successfully downloaded {len(downloaded_files)} files")
            
            # Step 5: Prepare response
            result = {
                "status": "completed",
                "api": clean_api_name,
                "api_slug": api_slug,
                "total_found": len(pdf_candidates),
                "total_relevant": len(relevant_pdfs),
                "total_downloaded": len(downloaded_files),
                "hits": downloaded_files,
                "download_all_url": f"/api/research/{api_slug}/download-all",
                "debug_info": {
                    "sources_searched": source_names,
                    "search_queries": search_queries,
                    "pdf_candidates_found": len(pdf_candidates),
                    "relevant_pdfs_found": len(relevant_pdfs),
                    "files_downloaded": len(downloaded_files)
                }
            }
            
            logger.info(f"🎉 Search completed for {clean_api_name}: {len(downloaded_files)} files downloaded")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error in pharmaceutical search for {api_name}: {e}", exc_info=True)
            return {
                "status": "error",
                "api": api_name,
                "message": f"Search failed: {str(e)}",
                "hits": [],
                "debug_info": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    async def _filter_relevant_pdfs(self, pdf_candidates: List[Dict], api_name: str) -> List[Dict]:
        """
        Filter PDF candidates for relevance using OpenAI assessment
        """
        relevant_pdfs = []
        
        # Process PDFs in batches to avoid overwhelming the API
        batch_size = 5
        for i in range(0, len(pdf_candidates), batch_size):
            batch = pdf_candidates[i:i + batch_size]
            batch_tasks = []
            
            for pdf_info in batch:
                task = self._assess_pdf_relevance(pdf_info, api_name)
                batch_tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error assessing PDF relevance: {result}")
                    continue
                
                if result:  # PDF was deemed relevant
                    relevant_pdfs.append(batch[j])
            
            # Small delay between batches to be respectful to APIs
            await asyncio.sleep(1)
        
        return relevant_pdfs
    
    async def _assess_pdf_relevance(self, pdf_info: Dict, api_name: str) -> bool:
        """
        Assess if a single PDF is relevant to the API
        """
        try:
            # Extract text sample from PDF
            pdf_text = await self.pdf_service.extract_text_sample(pdf_info['url'])
            
            if not pdf_text.strip():
                logger.warning(f"No text extracted from PDF: {pdf_info['url']}")
                return False
            
            # Use OpenAI to assess relevance
            assessment = await self.openai_service.assess_pdf_relevance(pdf_text, api_name)
            
            # Consider high and medium relevance as relevant
            relevance = assessment.get('relevance', 'low')
            confidence = assessment.get('confidence', 0.0)
            
            is_relevant = relevance in ['high', 'medium'] and confidence > 0.3
            
            if is_relevant:
                logger.info(f"PDF deemed relevant: {pdf_info['title']} (relevance: {relevance}, confidence: {confidence})")
            else:
                logger.debug(f"PDF filtered out: {pdf_info['title']} (relevance: {relevance}, confidence: {confidence})")
            
            return is_relevant
            
        except Exception as e:
            logger.error(f"Error assessing PDF relevance for {pdf_info['url']}: {e}")
            return False
    
    async def _download_pdfs(self, pdf_list: List[Dict], download_dir: str) -> List[Dict]:
        """
        Download relevant PDFs to storage directory
        """
        downloaded_files = []
        
        # Download PDFs in parallel batches
        batch_size = 3
        for i in range(0, len(pdf_list), batch_size):
            batch = pdf_list[i:i + batch_size]
            batch_tasks = []
            
            for pdf_info in batch:
                task = self._download_single_pdf(pdf_info, download_dir)
                batch_tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error downloading PDF: {result}")
                    continue
                
                if result:  # Download successful
                    downloaded_files.append(result)
        
        return downloaded_files
    
    async def _download_single_pdf(self, pdf_info: Dict, download_dir: str) -> Optional[Dict]:
        """
        Download a single PDF file
        """
        try:
            # Generate safe filename
            filename = self.pdf_service.get_pdf_filename(pdf_info['url'], pdf_info['title'])
            save_path = os.path.join(download_dir, filename)
            
            # Download the PDF
            success = await self.pdf_service.download_pdf(pdf_info['url'], save_path)
            
            if success:
                file_size = os.path.getsize(save_path)
                return {
                    'source': pdf_info['source'],
                    'title': pdf_info['title'],
                    'filename': filename,
                    'url': f"/static/{os.path.relpath(save_path, self.static_dir)}",
                    'original_url': pdf_info['url'],
                    'size_bytes': file_size
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error downloading PDF {pdf_info['url']}: {e}")
            return None
    
    def _load_research_sources(self) -> Dict[str, str]:
        """
        Load research sources from configuration file
        """
        sources = {}
        try:
            with open(self.resources_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ';' in line:
                        name, url = line.split(';', 1)
                        sources[name.strip()] = url.strip()
        except FileNotFoundError:
            logger.error(f"Research resources file not found: {self.resources_file}")
        except Exception as e:
            logger.error(f"Error loading research sources: {e}")
        
        return sources
    
    def _clean_api_name(self, api_name: str) -> str:
        """
        Clean and normalize the API name
        """
        # Remove extra whitespace and normalize case
        clean_name = api_name.strip()
        
        # Remove common suffixes that might interfere with search
        suffixes = [' hcl', ' hydrochloride', ' sulfate', ' sodium', ' potassium']
        for suffix in suffixes:
            if clean_name.lower().endswith(suffix):
                clean_name = clean_name[:-len(suffix)].strip()
        
        return clean_name
    
    def _create_api_slug(self, api_name: str) -> str:
        """
        Create a URL-safe slug for the API name
        """
        slug = api_name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    async def get_api_files(self, api_slug: str) -> List[Dict]:
        """
        Get list of downloaded files for an API
        """
        download_dir = os.path.join(self.static_dir, api_slug)
        
        if not os.path.exists(download_dir):
            return []
        
        files = []
        for filename in os.listdir(download_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(download_dir, filename)
                file_size = os.path.getsize(file_path)
                files.append({
                    'filename': filename,
                    'url': f"/static/{api_slug}/{filename}",
                    'size_bytes': file_size
                })
        
        return files
    
    async def close(self):
        """Close all service connections"""
        await self.web_service.close()
        await self.pdf_service.close()