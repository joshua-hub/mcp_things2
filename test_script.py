#!/usr/bin/env python3
"""
Test script to interact with the MCP middleware system.

Usage: python3 test_script.py "your prompt here"
"""

import sys
import json
import requests
import argparse
from typing import Dict, Any


def send_to_middleware(prompt: str, endpoint: str = "http://localhost:8002") -> Dict[str, Any]:
    """
    Send a prompt to the middleware and return the response.
    
    Args:
        prompt: The user prompt/query to send
        endpoint: The middleware endpoint URL
        
    Returns:
        Dictionary containing the response from middleware
    """
    
    # Prepare the request payload
    # Based on ChatRequest model in middleware: expects messages array
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print(f"Sending request to {endpoint}...")
        print(f"Prompt: {prompt}")
        print("-" * 50)
        
        # Try different possible endpoints
        endpoints_to_try = [
            f"{endpoint}/chat",
            f"{endpoint}/query", 
            f"{endpoint}/mcp",
            f"{endpoint}/api/chat",
            f"{endpoint}/process"
        ]
        
        response = None
        for ep in endpoints_to_try:
            try:
                response = requests.post(ep, json=payload, headers=headers, timeout=30)
                if response.status_code == 200:
                    print(f"✅ Success with endpoint: {ep}")
                    break
                elif response.status_code == 404:
                    continue
                else:
                    print(f"❌ {ep} returned status {response.status_code}")
                    continue
            except requests.exceptions.ConnectionError:
                print(f"❌ Connection failed to {ep}")
                continue
            except Exception as e:
                print(f"❌ Error with {ep}: {e}")
                continue
        
        if response is None or response.status_code != 200:
            print("❌ All endpoints failed. Trying health check...")
            health_response = requests.get(f"{endpoint}/health", timeout=10)
            print(f"Health check status: {health_response.status_code}")
            if health_response.status_code == 200:
                print("Middleware is running but API endpoints might be different.")
                print("Available endpoints might be:")
                print("- Check middleware logs for actual API routes")
                return {"error": "Could not find working API endpoint"}
            else:
                return {"error": f"Middleware not responding. Health check failed: {health_response.status_code}"}
        
        # Parse and return response
        try:
            result = response.json()
            print("Response received:")
            print(json.dumps(result, indent=2))
            return result
        except json.JSONDecodeError:
            print("Response (raw text):")
            print(response.text)
            return {"response": response.text, "status_code": response.status_code}
            
    except requests.exceptions.ConnectionError:
        return {"error": f"Could not connect to middleware at {endpoint}. Is it running?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Middleware might be processing..."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Test script for MCP middleware")
    parser.add_argument("prompt", help="The prompt/query to send to the middleware")
    parser.add_argument("--endpoint", default="http://localhost:8002", 
                       help="Middleware endpoint (default: http://localhost:8002)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Endpoint: {args.endpoint}")
        print(f"Prompt: {args.prompt}")
        print()
    
    # Send request to middleware
    result = send_to_middleware(args.prompt, args.endpoint)
    
    # Print final result
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    else:
        print("✅ Success!")
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_script.py \"your prompt here\"")
        print("Example: python3 test_script.py \"What time is it?\"")
        sys.exit(1)
    
    main() 