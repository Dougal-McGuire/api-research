import os
import logging
from typing import Dict
from openai import OpenAI

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