import os
import re
import tempfile
import asyncio
from typing import Dict, Optional, List
import httpx
import PyPDF2
from pdfminer.high_level import extract_text
import pytesseract
from pdf2image import convert_from_path
import logging

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=60.0)
    
    async def extract_text_sample(self, pdf_url: str, max_pages: int = 3) -> str:
        """
        Download PDF and extract text from first few pages for relevance assessment
        """
        try:
            # Add delay to avoid rate limiting
            await asyncio.sleep(1)
            
            # Download PDF to temporary file
            response = await self.session.get(pdf_url)
            if response.status_code != 200:
                logger.error(f"Failed to download PDF: {pdf_url} (status: {response.status_code})")
                return ""
            
            # Check if it's actually a PDF
            if not response.headers.get('content-type', '').startswith('application/pdf'):
                logger.warning(f"URL doesn't appear to be a PDF: {pdf_url}")
                return ""
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            try:
                # Try multiple text extraction methods
                text = await self._extract_text_multiple_methods(tmp_file_path, max_pages)
                return text
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_url}: {e}")
            return ""
    
    async def _extract_text_multiple_methods(self, pdf_path: str, max_pages: int) -> str:
        """
        Try multiple methods to extract text from PDF
        """
        text = ""
        
        # Method 1: PyPDF2
        try:
            text = self._extract_with_pypdf2(pdf_path, max_pages)
            if len(text.strip()) > 100:  # If we got substantial text
                return text
        except Exception as e:
            logger.debug(f"PyPDF2 extraction failed: {e}")
        
        # Method 2: pdfminer
        try:
            text = self._extract_with_pdfminer(pdf_path, max_pages)
            if len(text.strip()) > 100:
                return text
        except Exception as e:
            logger.debug(f"pdfminer extraction failed: {e}")
        
        # Method 3: OCR as fallback
        try:
            text = await self._extract_with_ocr(pdf_path, max_pages)
            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_path: str, max_pages: int) -> str:
        """Extract text using PyPDF2"""
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = min(len(reader.pages), max_pages)
            
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text
    
    def _extract_with_pdfminer(self, pdf_path: str, max_pages: int) -> str:
        """Extract text using pdfminer"""
        text = extract_text(pdf_path, maxpages=max_pages)
        return text
    
    async def _extract_with_ocr(self, pdf_path: str, max_pages: int) -> str:
        """Extract text using OCR as fallback"""
        text = ""
        
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path, last_page=max_pages)
            
            for i, image in enumerate(images):
                # Use OCR to extract text from image
                page_text = pytesseract.image_to_string(image)
                text += f"Page {i+1}:\n{page_text}\n\n"
                
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
        
        return text
    
    async def download_pdf(self, pdf_url: str, save_path: str) -> bool:
        """
        Download a PDF file to the specified path
        """
        try:
            response = await self.session.get(pdf_url)
            if response.status_code != 200:
                logger.error(f"Failed to download PDF: {pdf_url} (status: {response.status_code})")
                return False
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Write PDF to file
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded PDF: {pdf_url} -> {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading PDF {pdf_url}: {e}")
            return False
    
    def get_pdf_filename(self, pdf_url: str, title: str = "") -> str:
        """
        Generate a safe filename for the PDF
        """
        # Try to get filename from URL
        filename = os.path.basename(pdf_url.split('?')[0])
        
        # If no filename in URL or not a PDF, generate from title
        if not filename.endswith('.pdf'):
            if title:
                # Clean title for filename
                safe_title = re.sub(r'[^\w\s-]', '', title)
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                filename = f"{safe_title[:50]}.pdf"
            else:
                filename = f"document_{hash(pdf_url) % 10000}.pdf"
        
        return filename
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()