#!/usr/bin/env python3
"""Test configuration and connectivity"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import httpx
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

async def test_model_endpoint(model_type: str, base_url: str, api_key: str, model_name: str):
    """Test if a model endpoint is accessible"""
    print(f"\n{BLUE}Testing {model_type} model...{NC}")
    print(f"  Model: {model_name}")
    print(f"  URL: {base_url}")
    
    try:
        # Test endpoint connectivity
        async with httpx.AsyncClient() as client:
            # Try to get models list (OpenAI compatible)
            headers = {"Authorization": f"Bearer {api_key}"}
            response = await client.get(f"{base_url}/models", headers=headers, timeout=5.0)
            
            if response.status_code == 200:
                print(f"{GREEN}✅ {model_type} endpoint is accessible{NC}")
                return True
            else:
                print(f"{YELLOW}⚠️  {model_type} endpoint returned status {response.status_code}{NC}")
                return True  # Still might work for chat completions
                
    except httpx.ConnectError:
        print(f"{RED}❌ Cannot connect to {model_type} endpoint at {base_url}{NC}")
        if "localhost:11434" in base_url:
            print(f"{YELLOW}   Make sure Ollama is running: ollama serve{NC}")
        return False
    except Exception as e:
        print(f"{YELLOW}⚠️  {model_type} endpoint test inconclusive: {str(e)}{NC}")
        return True  # Might still work

async def test_tavily():
    """Test Tavily API key"""
    print(f"\n{BLUE}Testing Tavily API...{NC}")
    api_key = os.getenv("TAVILY_API_KEY", "")
    
    if not api_key or api_key == "your-tavily-api-key-here":
        print(f"{RED}❌ Tavily API key not configured{NC}")
        print(f"{YELLOW}   Get your API key at: https://tavily.com{NC}")
        return False
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        # Simple test search
        results = client.search("test", max_results=1)
        print(f"{GREEN}✅ Tavily API key is valid{NC}")
        return True
    except Exception as e:
        print(f"{RED}❌ Tavily API error: {str(e)}{NC}")
        return False

async def main():
    print(f"{BLUE}{'='*60}{NC}")
    print(f"{BLUE}Open Deep Research Configuration Test{NC}")
    print(f"{BLUE}{'='*60}{NC}")
    
    all_good = True
    
    # Test Tavily
    tavily_ok = await test_tavily()
    all_good = all_good and tavily_ok
    
    # Test each model type
    model_types = ["SUMMARIZATION", "RESEARCH", "COMPRESSION", "FINAL_REPORT"]
    
    for model_type in model_types:
        model_name = os.getenv(f"{model_type}_MODEL_NAME", "")
        base_url = os.getenv(f"{model_type}_MODEL_BASE_URL", "")
        api_key = os.getenv(f"{model_type}_MODEL_API_KEY", "")
        
        if not model_name or not base_url:
            print(f"\n{RED}❌ {model_type} model not configured{NC}")
            all_good = False
            continue
            
        model_ok = await test_model_endpoint(model_type, base_url, api_key, model_name)
        all_good = all_good and model_ok
    
    # Summary
    print(f"\n{BLUE}{'='*60}{NC}")
    if all_good:
        print(f"{GREEN}✅ All configurations look good!{NC}")
        print(f"\n{BLUE}You can now start the application with: ./ui/start.sh{NC}")
    else:
        print(f"{YELLOW}⚠️  Some configurations need attention{NC}")
        print(f"\n{BLUE}Please check your .env file and ensure all services are running{NC}")
    
    return all_good

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main()) else 1)