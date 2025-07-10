import json
import os
from typing import Dict, List, Optional
import openai
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    async def plan_search_queries(self, api_name: str, sources: List[str]) -> Dict:
        """
        Use OpenAI to generate optimal search queries for each regulatory source
        """
        system_prompt = """You are an expert regulatory-document search assistant that knows how to navigate specific regulatory search interfaces.

For each source, generate the appropriate search strategy:

1. EPAR - EMA's medicine search page with filters already applied. Search for the API name to find European Public Assessment Reports.
2. EMA-PSBG - EMA's Product-Specific Bioequivalence Guidance page. Look for the API name in guidance documents.
3. FDA-Approvals - FDA's drug approval database. Search for the API name to find approval letters and reviews.
4. FDA-PSBG - FDA's Product-Specific Guidance database. Search for API name in guidance documents.

These are landing pages with search functionality. The AI needs to:
- Enter the API name in search fields
- Follow links to relevant documents
- Look for PDF documents containing approval information, clinical reviews, or guidance

Return JSON with simple search terms that would be entered into search boxes on these pages."""

        user_prompt = f"""API = "{api_name}"
Sources = {sources}

For each source, provide the search term that should be entered into their search interface to find regulatory documents for this pharmaceutical ingredient."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Generated search queries for {api_name}: {result}")
            
            # Ensure we return the expected format
            if 'search_queries' not in result:
                # If the AI didn't use the expected format, create it
                if isinstance(result, dict) and len(result) > 0:
                    # Assume the result is the search queries directly
                    result = {"search_queries": result, "canonical": api_name}
                else:
                    # Fallback if AI response is unexpected
                    result = {
                        "canonical": api_name,
                        "search_queries": {source: api_name for source in sources}
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating search queries: {e}")
            # Fallback to basic queries
            return {
                "canonical": api_name,
                "search_queries": {
                    source: f'"{api_name}" approval filetype:pdf site:{self._get_domain(source)}'
                    for source in sources
                }
            }
    
    async def assess_pdf_relevance(self, pdf_text: str, api_name: str) -> Dict:
        """
        Assess if a PDF document is relevant to the target API
        """
        system_prompt = f"""Given the text of pages 1-3 of a PDF and the target API "{api_name}",
assess the relevance of this document for pharmaceutical research.

Consider:
- Does it mention the specific API name or close synonyms?
- Is it an official regulatory document (approval, assessment, guidance)?
- Does it contain clinical or safety information about the drug?

Answer ONLY with JSON:
{{
  "relevance": "high" | "medium" | "low",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

        # Truncate text to first 3000 characters to avoid token limits
        truncated_text = pdf_text[:3000] if len(pdf_text) > 3000 else pdf_text
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": truncated_text}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"PDF relevance assessment for {api_name}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error assessing PDF relevance: {e}")
            return {
                "relevance": "medium",
                "confidence": 0.5,
                "reasoning": "Error during assessment, defaulting to medium relevance"
            }
    
    def _get_domain(self, source: str) -> str:
        """Extract domain from source for search queries"""
        domain_map = {
            "EPAR": "ema.europa.eu",
            "EMA-PSBG": "ema.europa.eu",
            "FDA-Approvals": "accessdata.fda.gov",
            "FDA-PSBG": "accessdata.fda.gov"
        }
        return domain_map.get(source, source.lower().replace(" ", "").replace("-", ""))