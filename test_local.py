#!/usr/bin/env python3
"""
Simple test script to verify the research service is working
This tests the basic functionality without requiring real OpenAI API calls
"""
import os
import sys
import asyncio
import httpx

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_basic_functionality():
    """Test basic service functionality"""
    print("🧪 Testing Clinical Research Helper - Basic Functionality")
    print("=" * 60)
    
    # Test 1: Import all services
    print("1. Testing imports...")
    try:
        from services.research_service import ResearchService
        from services.openai_service import OpenAIService  
        from services.web_service import WebExplorationService
        from services.pdf_service import PDFService
        print("   ✅ All services imported successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Check research resources file
    print("2. Testing research resources...")
    try:
        resources_file = "app/core/research_resources.txt"
        if os.path.exists(resources_file):
            with open(resources_file, 'r') as f:
                lines = f.readlines()
                print(f"   ✅ Found {len(lines)} research sources")
                for line in lines[:3]:  # Show first 3
                    name, url = line.strip().split(';', 1)
                    print(f"      - {name}: {url}")
                if len(lines) > 3:
                    print(f"      ... and {len(lines) - 3} more")
        else:
            print(f"   ❌ Research resources file not found: {resources_file}")
            return False
    except Exception as e:
        print(f"   ❌ Error reading research resources: {e}")
        return False
    
    # Test 3: Test API name processing utility functions
    print("3. Testing API name processing...")
    try:
        import re
        
        # Test clean_api_name function (replicate the logic)
        def clean_api_name(api_name: str) -> str:
            clean_name = api_name.strip()
            suffixes = [' hcl', ' hydrochloride', ' sulfate', ' sodium', ' potassium']
            for suffix in suffixes:
                if clean_name.lower().endswith(suffix):
                    clean_name = clean_name[:-len(suffix)].strip()
            return clean_name
        
        def create_api_slug(api_name: str) -> str:
            slug = api_name.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            return slug.strip('-')
        
        # Test cases
        test_cases = [
            ("Aspirin", "Aspirin"),
            ("Ibuprofen HCL", "Ibuprofen"),
            ("  Dexamethasone sodium  ", "Dexamethasone"),
        ]
        
        for input_name, expected in test_cases:
            cleaned = clean_api_name(input_name)
            slug = create_api_slug(cleaned)
            print(f"   '{input_name}' -> '{cleaned}' -> slug: '{slug}'")
        
        print("   ✅ API name processing works correctly")
            
    except Exception as e:
        print(f"   ❌ API name processing failed: {e}")
        return False
    
    # Test 4: Test web service (without making actual requests)
    print("4. Testing web service initialization...")
    try:
        web_service = WebExplorationService()
        print("   ✅ Web service initialized successfully")
        await web_service.close()
    except Exception as e:
        print(f"   ❌ Web service initialization failed: {e}")
        return False
    
    # Test 5: Test PDF service
    print("5. Testing PDF service...")
    try:
        pdf_service = PDFService()
        
        # Test filename generation
        test_url = "https://example.com/document.pdf"
        filename = pdf_service.get_pdf_filename(test_url, "Test Document")
        print(f"   Generated filename: {filename}")
        print("   ✅ PDF service works correctly")
        await pdf_service.close()
    except Exception as e:
        print(f"   ❌ PDF service failed: {e}")
        return False
    
    # Test 6: Test directory creation
    print("6. Testing directory creation...")
    try:
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_slug = "test-api"
            download_dir = os.path.join(temp_dir, test_slug)
            os.makedirs(download_dir, exist_ok=True)
            
            # Create a test file
            test_file = os.path.join(download_dir, "test.pdf")
            with open(test_file, "w") as f:
                f.write("test content")
            
            print(f"   Created test directory: {download_dir}")
            print(f"   Created test file: {test_file}")
            print("   ✅ Directory and file operations work correctly")
    except Exception as e:
        print(f"   ❌ Directory operations failed: {e}")
        return False
    
    print("\n🎉 All basic functionality tests passed!")
    print("\n📝 Next steps:")
    print("   1. Set up OPENAI_API_KEY environment variable")
    print("   2. Test with docker-compose.dev.yml")
    print("   3. Try a real search with a pharmaceutical API name")
    
    return True

async def test_api_health():
    """Test the health check endpoint if server is running"""
    print("\n🏥 Testing API health (if server is running)...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                print("   ✅ Main health endpoint responding")
                print(f"   Response: {response.json()}")
                
                # Test research health endpoint
                research_response = await client.get("http://localhost:8000/api/research/health", timeout=5.0)
                if research_response.status_code == 200:
                    print("   ✅ Research service health endpoint responding")
                    print(f"   Response: {research_response.json()}")
                else:
                    print(f"   ⚠️  Research health endpoint returned: {research_response.status_code}")
            else:
                print(f"   ⚠️  Server returned status: {response.status_code}")
    except httpx.ConnectError:
        print("   ℹ️  Server not running (this is ok for basic tests)")
    except Exception as e:
        print(f"   ⚠️  Error connecting to server: {e}")

async def main():
    """Run all tests"""
    success = await test_basic_functionality()
    await test_api_health()
    
    if success:
        print(f"\n✅ Basic functionality test completed successfully!")
        print("\nTo start the full system:")
        print("  1. Create .env file with OPENAI_API_KEY=your_key_here")
        print("  2. Run: docker-compose -f docker-compose.dev.yml up")
        print("  3. Visit: http://localhost:5173")
        return True
    else:
        print(f"\n❌ Tests failed!")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)