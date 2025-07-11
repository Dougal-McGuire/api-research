import os
import re
import logging
import httpx
from datetime import datetime
from typing import Dict, List
from openai import OpenAI
from urllib.parse import urljoin, urlparse
from .pdf_generator_service import PDFGeneratorService

logger = logging.getLogger(__name__)

class OpenAIResearchService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
        self.template_file = "app/core/research_prompt_template.txt"
    
    def _load_prompt_template(self) -> str:
        """Load the research prompt template from file - NO FALLBACK"""
        try:
            logger.info(f"🔍 Loading template from: {self.template_file}")
            with open(self.template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            logger.info(f"✅ Template loaded successfully, length: {len(template_content)} characters")
            return template_content
        except FileNotFoundError:
            logger.error(f"❌ Template file not found: {self.template_file}")
            raise FileNotFoundError(f"Template file not found: {self.template_file}. This file is required.")
        except Exception as e:
            logger.error(f"❌ Error loading template: {e}")
            raise
    
    async def research_substance(self, substance_name: str, debug: bool = True, model: str = "o1") -> Dict:
        """
        Research a pharmaceutical substance using OpenAI's web search capabilities
        """
        try:
            # Clean and normalize substance name
            clean_substance_name = substance_name.strip()
            
            logger.info(f"🔍 Starting OpenAI research for substance: {clean_substance_name}")
            
            # Load and format the prompt template
            template = self._load_prompt_template()
            formatted_prompt = template.format(substance_name=clean_substance_name)
            
            if debug:
                logger.info(f"📝 Using prompt: {formatted_prompt}")
            
            # Use the specified model
            logger.info(f"🤖 Calling OpenAI {model} model...")
            
            # Check if this is o1-pro which requires a different endpoint
            if model == "o1-pro":
                # o1-pro uses a different API endpoint that's not yet supported in the standard SDK
                # For now, we'll fallback to o1 model
                logger.warning(f"⚠️ {model} requires special API endpoint. Falling back to o1 model.")
                actual_model = "o1"
            else:
                actual_model = model
            
            response = self.client.chat.completions.create(
                model=actual_model,  # Using the specified model for research
                messages=[
                    {
                        "role": "user", 
                        "content": formatted_prompt
                    }
                ],
                # Note: o1 models don't support system messages or many parameters
                # They are optimized for research and reasoning tasks
            )
            
            research_content = response.choices[0].message.content
            
            if debug:
                logger.info(f"📊 Research completed. Response length: {len(research_content)} characters")
            
            # Prepare the result
            result = {
                "status": "completed",
                "substance": clean_substance_name,
                "research_content": research_content,
                "prompt_used": formatted_prompt if debug else None,
                "model_used": model,
                "debug_info": {
                    "substance_searched": clean_substance_name,
                    "template_file": self.template_file,
                    "template_length": len(template),
                    "formatted_prompt_length": len(formatted_prompt),
                    "response_length": len(research_content),
                    "actual_prompt_used": formatted_prompt
                } if debug else None
            }
            
            # Create API slug for file organization
            api_slug = self._create_api_slug(clean_substance_name)
            
            # Extract and download PDFs from research content
            downloaded_files = await self._extract_and_download_pdfs(research_content, api_slug)
            
            # Generate PDF summary
            pdf_summary_url = None
            try:
                pdf_generator = PDFGeneratorService()
                pdf_summary_path = pdf_generator.generate_research_summary_pdf(result, api_slug)
                pdf_summary_url = f"/static/apis/{api_slug}/{os.path.basename(pdf_summary_path)}"
            except Exception as e:
                logger.error(f"Failed to generate PDF summary: {e}")
                # Continue without PDF generation rather than failing the entire request
            
            # Update result with file information
            result.update({
                "api_slug": api_slug,
                "pdf_summary_url": pdf_summary_url,
                "download_all_url": f"/api/research/{api_slug}/download-all",
                "downloaded_files": downloaded_files
            })
            
            logger.info(f"✅ Research completed successfully for {clean_substance_name}")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error in OpenAI research for {substance_name}: {e}", exc_info=True)
            return {
                "status": "error",
                "substance": substance_name,
                "message": f"Research failed: {str(e)}",
                "research_content": None,
                "debug_info": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    def update_prompt_template(self, new_template: str) -> bool:
        """
        Update the prompt template file
        """
        try:
            with open(self.template_file, 'w', encoding='utf-8') as f:
                f.write(new_template)
            logger.info(f"✅ Prompt template updated successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update prompt template: {e}")
            return False
    
    def get_current_template(self) -> str:
        """
        Get the current prompt template
        """
        return self._load_prompt_template()
    
    def _create_api_slug(self, substance_name: str) -> str:
        """Create a URL-safe slug for the API name"""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', substance_name.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        return slug
    
    async def _extract_and_download_pdfs(self, research_content: str, api_slug: str) -> List[Dict]:
        """Extract PDF URLs from research content and download them"""
        downloaded_files = []
        
        try:
            # Create output directory
            output_dir = f"static/apis/{api_slug}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Extract PDF URLs from research content
            pdf_urls = self._extract_pdf_urls(research_content)
            
            for i, url in enumerate(pdf_urls):
                try:
                    file_info = await self._download_pdf(url, output_dir, api_slug, i)
                    if file_info:
                        downloaded_files.append(file_info)
                except Exception as e:
                    logger.warning(f"Failed to download PDF {url}: {e}")
                    continue
            
            logger.info(f"Downloaded {len(downloaded_files)} PDF files for {api_slug}")
            
        except Exception as e:
            logger.error(f"Error in PDF extraction and download: {e}")
        
        return downloaded_files
    
    def _extract_pdf_urls(self, content: str) -> List[str]:
        """Extract PDF URLs from research content"""
        # Look for various PDF URL patterns
        pdf_patterns = [
            r'https?://[^\s\n\r\t]+\.pdf(?:\?[^\s\n\r\t]*)?',  # Direct PDF links
            r'https?://[^\s\n\r\t]+/[^\s\n\r\t]*\.pdf(?:\?[^\s\n\r\t]*)?',  # PDF in path
        ]
        
        urls = set()
        for pattern in pdf_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            urls.update(matches)
        
        # Also look for links that might lead to PDFs (EMA/FDA patterns)
        potential_pdf_patterns = [
            r'https?://www\.ema\.europa\.eu/[^\s\n\r\t]+',
            r'https?://www\.accessdata\.fda\.gov/[^\s\n\r\t]+',
        ]
        
        for pattern in potential_pdf_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up the URL (remove trailing punctuation)
                clean_url = re.sub(r'[.,;:!?]+$', '', match)
                urls.add(clean_url)
        
        return list(urls)
    
    async def _download_pdf(self, url: str, output_dir: str, api_slug: str, index: int) -> Dict:
        """Download a single PDF file"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                # Check if it's actually a PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                    logger.warning(f"URL {url} doesn't appear to be a PDF (content-type: {content_type})")
                    return None
                
                # Generate meaningful filename
                filename = self._generate_pdf_filename(url, api_slug, index)
                file_path = os.path.join(output_dir, filename)
                
                # Save the file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Generate file info
                download_date = datetime.now().strftime("%d-%b-%Y")
                file_size = len(response.content)
                
                return {
                    "title": self._extract_title_from_url(url),
                    "filename": filename,
                    "url": url,
                    "local_path": f"/static/apis/{api_slug}/{filename}",
                    "source": self._determine_source(url),
                    "download_date": download_date,
                    "size_bytes": file_size
                }
                
        except Exception as e:
            logger.error(f"Error downloading PDF from {url}: {e}")
            return None
    
    def _generate_pdf_filename(self, url: str, api_slug: str, index: int) -> str:
        """Generate a meaningful filename for the PDF"""
        # Extract filename from URL
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%d-%b-%Y")
        
        # Determine source
        source = self._determine_source(url)
        
        # Create meaningful name
        if original_filename and original_filename.endswith('.pdf'):
            base_name = original_filename[:-4]  # Remove .pdf extension
            filename = f"{source}_{api_slug}_{base_name}_{timestamp}.pdf"
        else:
            filename = f"{source}_{api_slug}_doc_{index+1}_{timestamp}.pdf"
        
        # Clean filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        
        return filename
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a title from the URL"""
        parsed_url = urlparse(url)
        
        if 'ema.europa.eu' in parsed_url.netloc:
            return "EMA Document"
        elif 'fda.gov' in parsed_url.netloc:
            return "FDA Document"
        else:
            return "Regulatory Document"
    
    def _determine_source(self, url: str) -> str:
        """Determine the source of the document from URL"""
        url_lower = url.lower()
        
        if 'ema.europa.eu' in url_lower:
            if 'epar' in url_lower:
                return "EMA-EPAR"
            elif 'bioequivalence' in url_lower or 'psbg' in url_lower:
                return "EMA-PSBG"
            else:
                return "EMA"
        elif 'fda.gov' in url_lower:
            if 'daf' in url_lower or 'approval' in url_lower:
                return "FDA-DAF"
            elif 'psg' in url_lower or 'guidance' in url_lower:
                return "FDA-PSG"
            else:
                return "FDA"
        else:
            return "OTHER"