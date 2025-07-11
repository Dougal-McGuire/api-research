import os
import re
from datetime import datetime
from typing import Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging

logger = logging.getLogger(__name__)

class PDFGeneratorService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF"""
        # Check if styles already exist before adding
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=12
            ))
        
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.darkgreen,
                spaceBefore=12,
                spaceAfter=6
            ))
        
        if 'ResearchBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResearchBodyText',
                parent=self.styles['Normal'],
                fontSize=10,
                leftIndent=0,
                rightIndent=0,
                spaceAfter=6
            ))
    
    def generate_research_summary_pdf(self, research_data: Dict, api_slug: str) -> str:
        """Generate a PDF summary of the research results"""
        try:
            # Create output directory
            output_dir = f"static/apis/{api_slug}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%d-%b-%Y")
            filename = f"research_summary_{api_slug}_{timestamp}.pdf"
            file_path = os.path.join(output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Title
            substance_name = research_data.get('substance', 'Unknown Substance')
            title = f"Pharmaceutical Research Summary: {substance_name}"
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 12))
            
            # Metadata
            model_used = research_data.get('model_used', 'Unknown')
            generated_date = datetime.now().strftime("%d %B %Y at %H:%M UTC")
            
            metadata_text = f"""
            <b>Generated:</b> {generated_date}<br/>
            <b>AI Model:</b> {model_used}<br/>
            <b>Search Sources:</b> EMA EPAR, EMA-PSBG, FDA Approvals, FDA-PSBG<br/>
            """
            story.append(Paragraph(metadata_text, self.styles['ResearchBodyText']))
            story.append(Spacer(1, 18))
            
            # Research Content
            research_content = research_data.get('research_content', '')
            if research_content:
                story.append(Paragraph("Research Results", self.styles['SectionHeader']))
                
                # Split content by sections and format
                sections = self.parse_research_content(research_content)
                for section_title, section_content in sections:
                    if section_title:
                        story.append(Paragraph(section_title, self.styles['Heading3']))
                    
                    # Clean and format the content
                    try:
                        formatted_content = self.format_content_for_pdf(section_content)
                        story.append(Paragraph(formatted_content, self.styles['ResearchBodyText']))
                    except Exception as e:
                        logger.warning(f"Failed to format section content: {e}")
                        # Fallback to plain text
                        safe_content = section_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        safe_content = safe_content.replace('\n', '<br/>')
                        story.append(Paragraph(safe_content, self.styles['ResearchBodyText']))
                    story.append(Spacer(1, 12))
            
            # Downloaded Files Section
            downloaded_files = research_data.get('downloaded_files', [])
            if downloaded_files:
                story.append(PageBreak())
                story.append(Paragraph("Downloaded Documents", self.styles['SectionHeader']))
                
                for file_info in downloaded_files:
                    file_text = f"""
                    <b>{file_info.get('title', 'Document')}</b><br/>
                    Source: {file_info.get('source', 'Unknown')}<br/>
                    Downloaded: {file_info.get('download_date', 'Unknown')}<br/>
                    File: {file_info.get('filename', 'Unknown')}<br/>
                    """
                    story.append(Paragraph(file_text, self.styles['ResearchBodyText']))
                    story.append(Spacer(1, 8))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF summary generated: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating PDF summary: {e}")
            raise
    
    def parse_research_content(self, content: str):
        """Parse research content into sections"""
        sections = []
        
        # Split by common section headers
        section_patterns = [
            r'(?i)^#+\s*(EPAR|EMA.*PSBG|FDA.*Approvals?|FDA.*PSG|Key.*Regulatory|Clinical.*Trials?).*$',
            r'(?i)^\*\*(EPAR|EMA.*PSBG|FDA.*Approvals?|FDA.*PSG|Key.*Regulatory|Clinical.*Trials?)\*\*',
            r'(?i)^(EPAR|EMA.*PSBG|FDA.*Approvals?|FDA.*PSG|Key.*Regulatory|Clinical.*Trials?):\s*$',
        ]
        
        current_section = ""
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line.strip()):
                    # Save previous section
                    if current_section or current_content:
                        sections.append((current_section, '\n'.join(current_content)))
                    
                    # Start new section
                    current_section = line.strip()
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Add final section
        if current_section or current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def format_content_for_pdf(self, content: str) -> str:
        """Format content for PDF rendering"""
        import html
        
        # First, unescape any HTML entities
        content = html.unescape(content)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove any existing HTML/XML tags to avoid conflicts
        content = re.sub(r'<[^>]+>', '', content)
        
        # Handle bullet points
        content = re.sub(r'^[\s]*[-•]\s*', '• ', content, flags=re.MULTILINE)
        
        # Now escape for XML/ReportLab
        content = content.replace('&', '&amp;')
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        content = content.replace('"', '&quot;')
        content = content.replace("'", '&apos;')
        
        # Convert URLs to plain text (ReportLab has issues with complex link tags)
        # Just make them visible but not clickable to avoid parsing errors
        url_pattern = r'(https?://[^\s\n\r\t]+)'
        urls = re.findall(url_pattern, content)
        for url in urls:
            # Clean the URL of any trailing punctuation
            clean_url = re.sub(r'[.,;:!?]+$', '', url)
            content = content.replace(url, clean_url)
        
        # Convert markdown-style formatting safely
        # Bold
        content = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', content)
        # Italic  
        content = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', content)
        
        # Convert newlines to line breaks
        content = content.replace('\n', '<br/>')
        
        return content