import asyncio
import re
import urllib.parse
from typing import List, Set, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class WebExplorationService:
    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    async def discover_pdf_links(self, search_queries: Dict[str, str], api_name: str) -> List[Dict]:
        """
        Discover PDF links from regulatory sources using search queries
        """
        all_pdf_links = []
        
        for source, query in search_queries.items():
            try:
                logger.info(f"Searching {source} for {api_name}")
                pdf_links = await self._search_source(source, query, api_name)
                
                for link in pdf_links:
                    link['source'] = source
                    all_pdf_links.append(link)
                    
            except Exception as e:
                logger.error(f"Error searching {source}: {e}")
                continue
        
        # Deduplicate by URL
        seen_urls = set()
        unique_links = []
        for link in all_pdf_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        logger.info(f"Found {len(unique_links)} unique PDF links for {api_name}")
        return unique_links
    
    async def _search_source(self, source: str, query: str, api_name: str) -> List[Dict]:
        """
        Search a specific regulatory source for PDF documents using their search interfaces
        """
        logger.info(f"🔍 Searching {source} for '{api_name}' using query: {query}")
        
        # Load the actual URLs from the research resources
        sources_config = self._load_source_configs()
        
        if source not in sources_config:
            logger.warning(f"❌ No URL configured for source: {source}")
            return []
        
        search_page_url = sources_config[source]
        logger.info(f"🌐 Using search page: {search_page_url}")
        
        pdf_links = []
        
        try:
            if source == "EPAR":
                pdf_links = await self._search_ema_epar(search_page_url, api_name, query)
            elif source == "EMA-PSBG":
                pdf_links = await self._search_ema_psbg(search_page_url, api_name, query)
            elif source == "FDA-Approvals":
                pdf_links = await self._search_fda_approvals(search_page_url, api_name, query)
            elif source == "FDA-PSBG":
                pdf_links = await self._search_fda_psbg(search_page_url, api_name, query)
            else:
                logger.warning(f"⚠️ No specific search method for {source}, using generic search")
                pdf_links = await self._generic_search(search_page_url, api_name, query)
                
        except Exception as e:
            logger.error(f"💥 Error searching {source}: {e}", exc_info=True)
        
        final_count = min(len(pdf_links), 10)
        logger.info(f"✅ {source} search complete: {final_count} PDFs found (limited to 10)")
        return pdf_links[:10]  # Limit to 10 PDFs per source
    
    async def _get_search_urls(self, base_url: str, api_name: str) -> List[str]:
        """
        Get search result URLs for the API name
        """
        search_urls = []
        
        # Try common search patterns
        search_patterns = [
            f"{base_url}/search?q={urllib.parse.quote(api_name)}",
            f"{base_url}/en/search?q={urllib.parse.quote(api_name)}",
            f"{base_url}/medicines/{urllib.parse.quote(api_name.lower())}",
            f"{base_url}/drugs/{urllib.parse.quote(api_name.lower())}"
        ]
        
        for pattern in search_patterns:
            try:
                response = await self.session.get(pattern)
                if response.status_code == 200:
                    search_urls.append(pattern)
                    break
            except:
                continue
        
        # If no search works, just use the base URL
        if not search_urls:
            search_urls.append(base_url)
            
        return search_urls
    
    async def _extract_pdfs_from_page(self, url: str, api_name: str) -> List[Dict]:
        """
        Extract PDF links from a single page
        """
        pdf_links = []
        
        try:
            response = await self.session.get(url)
            if response.status_code != 200:
                return pdf_links
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links to PDFs
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Check if it's a PDF link
                if href.lower().endswith('.pdf') or 'filetype=pdf' in href.lower():
                    # Make absolute URL
                    if href.startswith('//'):
                        href = f"https:{href}"
                    elif href.startswith('/'):
                        base = urllib.parse.urlparse(url)
                        href = f"{base.scheme}://{base.netloc}{href}"
                    elif not href.startswith('http'):
                        href = urllib.parse.urljoin(url, href)
                    
                    # Get link text for title
                    title = link.get_text(strip=True) or "Document"
                    
                    # Basic relevance check in title/link text
                    if self._is_potentially_relevant(title + " " + href, api_name):
                        pdf_links.append({
                            'url': href,
                            'title': title,
                            'found_on': url
                        })
            
        except Exception as e:
            logger.error(f"Error extracting PDFs from {url}: {e}")
        
        return pdf_links
    
    async def _explore_linked_pages(self, base_url: str, api_name: str, max_depth: int = 1) -> List[Dict]:
        """
        Explore linked pages to find more PDFs
        """
        if max_depth <= 0:
            return []
        
        pdf_links = []
        
        try:
            response = await self.session.get(base_url)
            if response.status_code != 200:
                return pdf_links
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find relevant internal links
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True).lower()
                
                # Only follow links that seem relevant
                if not self._is_potentially_relevant(link_text, api_name):
                    continue
                
                # Make absolute URL
                if href.startswith('/'):
                    base = urllib.parse.urlparse(base_url)
                    href = f"{base.scheme}://{base.netloc}{href}"
                elif not href.startswith('http'):
                    href = urllib.parse.urljoin(base_url, href)
                
                # Only follow internal links
                if not href.startswith(urllib.parse.urlparse(base_url).netloc):
                    continue
                
                # Extract PDFs from this linked page
                page_pdfs = await self._extract_pdfs_from_page(href, api_name)
                pdf_links.extend(page_pdfs)
                
                if len(pdf_links) >= 5:  # Limit exploration
                    break
                    
        except Exception as e:
            logger.error(f"Error exploring linked pages from {base_url}: {e}")
        
        return pdf_links
    
    def _is_potentially_relevant(self, text: str, api_name: str) -> bool:
        """
        Basic check if text might be relevant to the API
        """
        text_lower = text.lower()
        api_lower = api_name.lower()
        
        # Direct name match
        if api_lower in text_lower:
            return True
        
        # Look for pharmaceutical keywords
        pharma_keywords = [
            'approval', 'assessment', 'authorization', 'summary', 'product',
            'clinical', 'safety', 'efficacy', 'medicine', 'drug', 'therapeutic',
            'indication', 'dosage', 'prescribing', 'regulatory', 'guidance'
        ]
        
        return any(keyword in text_lower for keyword in pharma_keywords)
    
    def _load_source_configs(self) -> Dict[str, str]:
        """
        Load source configurations from the research resources file
        """
        sources = {}
        try:
            with open("app/core/research_resources.txt", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ';' in line:
                        name, url = line.split(';', 1)
                        sources[name.strip()] = url.strip()
        except Exception as e:
            logger.error(f"Error loading source configs: {e}")
        return sources
    
    async def _search_ema_epar(self, search_url: str, api_name: str, query: str) -> List[Dict]:
        """
        Search EMA EPAR (European Public Assessment Reports) database
        """
        logger.info(f"🔍 Searching EMA EPAR for {api_name}")
        pdf_links = []
        
        try:
            # The URL already has filters applied, we need to add search term
            search_with_term = f"{search_url}&search_api_fulltext={query}"
            logger.info(f"📋 EMA EPAR search URL: {search_with_term}")
            
            response = await self.session.get(search_with_term)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for medicine links and then follow to find PDFs
                medicine_links = soup.find_all('a', href=True)
                for link in medicine_links:
                    href = link['href']
                    link_text = link.get_text(strip=True).lower()
                    
                    # Check if this looks like a medicine page
                    if any(keyword in link_text for keyword in [api_name.lower(), 'epar', 'assessment']):
                        if href.startswith('/'):
                            href = f"https://www.ema.europa.eu{href}"
                        
                        # Follow this link to find PDFs
                        page_pdfs = await self._extract_pdfs_from_page(href, api_name)
                        pdf_links.extend(page_pdfs)
                        
                        if len(pdf_links) >= 5:  # Limit per source
                            break
        
        except Exception as e:
            logger.error(f"Error in EMA EPAR search: {e}")
        
        return pdf_links
    
    async def _search_ema_psbg(self, search_url: str, api_name: str, query: str) -> List[Dict]:
        """
        Search EMA Product-Specific Bioequivalence Guidance
        """
        logger.info(f"🔍 Searching EMA PSBG for {api_name}")
        pdf_links = []
        
        try:
            response = await self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for guidance documents mentioning the API
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    link_text = link.get_text(strip=True)
                    href = link['href']
                    
                    # Check if this link mentions our API or contains "guidance"
                    if (api_name.lower() in link_text.lower() or 
                        any(keyword in link_text.lower() for keyword in ['guidance', 'bioequivalence', 'product-specific'])):
                        
                        if href.startswith('/'):
                            href = f"https://www.ema.europa.eu{href}"
                        elif not href.startswith('http'):
                            continue
                        
                        # If it's a PDF, add it directly
                        if href.lower().endswith('.pdf'):
                            pdf_links.append({
                                'url': href,
                                'title': link_text,
                                'found_on': search_url
                            })
                        else:
                            # Follow the link to find PDFs
                            page_pdfs = await self._extract_pdfs_from_page(href, api_name)
                            pdf_links.extend(page_pdfs)
                        
                        if len(pdf_links) >= 5:
                            break
        
        except Exception as e:
            logger.error(f"Error in EMA PSBG search: {e}")
        
        return pdf_links
    
    async def _search_fda_approvals(self, search_url: str, api_name: str, query: str) -> List[Dict]:
        """
        Search FDA Drug Approval database
        """
        logger.info(f"🔍 Searching FDA Approvals for {api_name}")
        pdf_links = []
        
        try:
            # For now, load the page and look for search functionality
            response = await self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for forms or search inputs where we can submit the API name
                # This is a simplified approach - in production you'd want to interact with the actual search form
                
                # Look for any existing links that might contain the API name
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    link_text = link.get_text(strip=True)
                    href = link['href']
                    
                    if api_name.lower() in link_text.lower():
                        if not href.startswith('http') and href.startswith('/'):
                            href = f"https://www.accessdata.fda.gov{href}"
                        
                        # Follow this link to find PDFs
                        page_pdfs = await self._extract_pdfs_from_page(href, api_name)
                        pdf_links.extend(page_pdfs)
                        
                        if len(pdf_links) >= 5:
                            break
        
        except Exception as e:
            logger.error(f"Error in FDA Approvals search: {e}")
        
        return pdf_links
    
    async def _search_fda_psbg(self, search_url: str, api_name: str, query: str) -> List[Dict]:
        """
        Search FDA Product-Specific Guidance database
        """
        logger.info(f"🔍 Searching FDA PSBG for {api_name}")
        pdf_links = []
        
        try:
            response = await self.session.get(search_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for guidance documents
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    link_text = link.get_text(strip=True)
                    href = link['href']
                    
                    if (api_name.lower() in link_text.lower() or 
                        'guidance' in link_text.lower()):
                        
                        if not href.startswith('http') and href.startswith('/'):
                            href = f"https://www.accessdata.fda.gov{href}"
                        
                        # If it's a PDF, add it directly
                        if href.lower().endswith('.pdf'):
                            pdf_links.append({
                                'url': href,
                                'title': link_text,
                                'found_on': search_url
                            })
                        else:
                            # Follow the link to find PDFs
                            page_pdfs = await self._extract_pdfs_from_page(href, api_name)
                            pdf_links.extend(page_pdfs)
                        
                        if len(pdf_links) >= 5:
                            break
        
        except Exception as e:
            logger.error(f"Error in FDA PSBG search: {e}")
        
        return pdf_links
    
    async def _generic_search(self, search_url: str, api_name: str, query: str) -> List[Dict]:
        """
        Generic search method for unknown sources
        """
        logger.info(f"🔍 Generic search for {api_name}")
        return await self._extract_pdfs_from_page(search_url, api_name)

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()