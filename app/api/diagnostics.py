import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, List
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from openai import OpenAI
from app.services.openai_research_service import OpenAIResearchService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health-check", response_class=HTMLResponse)
async def health_check_page():
    """
    Comprehensive health check page with logging and diagnostics
    """
    
    # Collect system information
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "environment": "production" if os.getenv("GOOGLE_CLOUD_PROJECT") else "development"
        },
        "environment_variables": {
            "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "openai_api_key_length": len(os.getenv("OPENAI_API_KEY", "")) if os.getenv("OPENAI_API_KEY") else 0,
        },
        "file_system": {
            "template_file_exists": os.path.exists("app/core/research_prompt_template.txt"),
            "template_file_path": os.path.abspath("app/core/research_prompt_template.txt"),
            "app_directory_contents": os.listdir("app") if os.path.exists("app") else "app directory not found",
            "core_directory_contents": os.listdir("app/core") if os.path.exists("app/core") else "app/core directory not found"
        }
    }
    
    # Test OpenAI connection
    openai_test_result = await test_openai_connection()
    health_data["openai_connection"] = openai_test_result
    
    # Test service initialization
    service_test_result = await test_service_initialization()
    health_data["service_initialization"] = service_test_result
    
    # Test models endpoint
    models_test_result = await test_models_endpoint()
    health_data["models_endpoint"] = models_test_result
    
    # Get recent logs
    recent_logs = get_recent_logs()
    health_data["recent_logs"] = recent_logs
    
    # Generate HTML page
    html_content = generate_health_check_html(health_data)
    return HTMLResponse(content=html_content)

async def test_openai_connection():
    """Test basic OpenAI API connection"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"status": "error", "message": "OPENAI_API_KEY not set"}
        
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        return {
            "status": "success",
            "message": "OpenAI API connection successful",
            "response": response.choices[0].message.content,
            "model_used": "gpt-3.5-turbo"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"OpenAI API connection failed: {str(e)}",
            "error_type": type(e).__name__
        }

async def test_service_initialization():
    """Test research service initialization"""
    try:
        service = OpenAIResearchService()
        template = service._load_prompt_template()
        
        return {
            "status": "success",
            "message": "Research service initialized successfully",
            "template_length": len(template),
            "template_preview": template[:200] + "..." if len(template) > 200 else template
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Service initialization failed: {str(e)}",
            "error_type": type(e).__name__
        }

async def test_models_endpoint():
    """Test models endpoint functionality"""
    try:
        from app.api.research import get_available_models
        models = await get_available_models()
        
        return {
            "status": "success",
            "message": f"Models endpoint working, {len(models.models)} models available",
            "models_count": len(models.models),
            "models": [{"id": m.id, "name": m.name} for m in models.models]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Models endpoint failed: {str(e)}",
            "error_type": type(e).__name__
        }

def get_recent_logs():
    """Get recent application logs"""
    try:
        # In production, we'd typically read from Cloud Logging
        # For now, we'll capture recent log messages from the logger
        log_messages = []
        
        # Get the root logger and check for recent messages
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if hasattr(handler, 'buffer'):
                log_messages.extend(handler.buffer)
        
        # If no buffered logs, return a status message
        if not log_messages:
            return {
                "status": "info",
                "message": "No recent logs available in memory buffer",
                "note": "Logs may be available in Cloud Logging console"
            }
        
        return {
            "status": "success",
            "message": f"Found {len(log_messages)} recent log entries",
            "logs": log_messages[-50:]  # Last 50 entries
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve logs: {str(e)}",
            "error_type": type(e).__name__
        }

def generate_health_check_html(health_data: Dict) -> str:
    """Generate HTML page for health check"""
    
    def status_badge(status: str) -> str:
        color = "green" if status == "success" else "red" if status == "error" else "orange"
        return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{status.upper()}</span>'
    
    def format_dict(data: Dict, indent: int = 0) -> str:
        html = ""
        for key, value in data.items():
            if isinstance(value, dict):
                html += f"{'  ' * indent}<strong>{key}:</strong><br>"
                html += format_dict(value, indent + 1)
            elif isinstance(value, list):
                html += f"{'  ' * indent}<strong>{key}:</strong><br>"
                for item in value[:10]:  # Limit to first 10 items
                    html += f"{'  ' * (indent + 1)}- {item}<br>"
                if len(value) > 10:
                    html += f"{'  ' * (indent + 1)}... and {len(value) - 10} more<br>"
            else:
                html += f"{'  ' * indent}<strong>{key}:</strong> {value}<br>"
        return html
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Research - Health Check</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .section {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .success {{ background-color: #f0f9ff; border-color: #22c55e; }}
            .error {{ background-color: #fef2f2; border-color: #ef4444; }}
            .info {{ background-color: #f8fafc; border-color: #64748b; }}
            .timestamp {{ color: #666; font-size: 14px; }}
            pre {{ background-color: #f1f5f9; padding: 10px; border-radius: 4px; overflow-x: auto; }}
            .refresh-btn {{ background-color: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            .refresh-btn:hover {{ background-color: #2563eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 API Research - Health Check Dashboard</h1>
            <p class="timestamp">Last updated: {health_data['timestamp']}</p>
            <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh</button>
            
            <div class="section {health_data['openai_connection']['status']}">
                <h2>🔗 OpenAI API Connection {status_badge(health_data['openai_connection']['status'])}</h2>
                <p><strong>Message:</strong> {health_data['openai_connection']['message']}</p>
                {f"<p><strong>Response:</strong> {health_data['openai_connection'].get('response', 'N/A')}</p>" if health_data['openai_connection']['status'] == 'success' else ''}
                {f"<p><strong>Error Type:</strong> {health_data['openai_connection'].get('error_type', 'N/A')}</p>" if health_data['openai_connection']['status'] == 'error' else ''}
            </div>
            
            <div class="section {health_data['service_initialization']['status']}">
                <h2>⚙️ Service Initialization {status_badge(health_data['service_initialization']['status'])}</h2>
                <p><strong>Message:</strong> {health_data['service_initialization']['message']}</p>
                {f"<p><strong>Template Length:</strong> {health_data['service_initialization'].get('template_length', 'N/A')} characters</p>" if health_data['service_initialization']['status'] == 'success' else ''}
                {f"<p><strong>Error Type:</strong> {health_data['service_initialization'].get('error_type', 'N/A')}</p>" if health_data['service_initialization']['status'] == 'error' else ''}
            </div>
            
            <div class="section {health_data['models_endpoint']['status']}">
                <h2>🤖 Models Endpoint {status_badge(health_data['models_endpoint']['status'])}</h2>
                <p><strong>Message:</strong> {health_data['models_endpoint']['message']}</p>
                {f"<p><strong>Available Models:</strong></p><ul>{''.join([f'<li>{m[\"name\"]} ({m[\"id\"]})</li>' for m in health_data['models_endpoint'].get('models', [])])}</ul>" if health_data['models_endpoint']['status'] == 'success' else ''}
            </div>
            
            <div class="section info">
                <h2>🖥️ System Information</h2>
                {format_dict(health_data['system_info'])}
            </div>
            
            <div class="section info">
                <h2>🔐 Environment Variables</h2>
                {format_dict(health_data['environment_variables'])}
            </div>
            
            <div class="section info">
                <h2>📁 File System</h2>
                {format_dict(health_data['file_system'])}
            </div>
            
            <div class="section {health_data['recent_logs']['status']}">
                <h2>📋 Recent Logs {status_badge(health_data['recent_logs']['status'])}</h2>
                <p><strong>Message:</strong> {health_data['recent_logs']['message']}</p>
                {f"<p><strong>Note:</strong> {health_data['recent_logs'].get('note', '')}</p>" if 'note' in health_data['recent_logs'] else ''}
                <p><strong>Cloud Logging Console:</strong> <a href="https://console.cloud.google.com/logs" target="_blank">View production logs</a></p>
            </div>
            
            <div class="section info">
                <h2>🔧 Quick Actions</h2>
                <p><a href="/api/research/health">JSON Health Check</a></p>
                <p><a href="/api/research/test-openai">Test OpenAI Connection</a></p>
                <p><a href="/api/research/models">Available Models</a></p>
                <p><a href="/docs">API Documentation</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content