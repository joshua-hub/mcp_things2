#!/usr/bin/env python3
"""
Direct MCP tool test script - bypasses the LLM chat interface.

Usage: python3 direct_test.py
"""

import sys
import json
import requests
from typing import Dict, Any


def test_time_service():
    """Test the time service directly."""
    try:
        print("Testing time-client directly...")
        response = requests.get("http://localhost:8003/current-time", timeout=10)
        if response.status_code == 200:
            print(f"✅ Time service: {response.text}")
            return True
        else:
            print(f"❌ Time service failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Time service error: {e}")
        return False


def test_sandbox_service():
    """Test the sandbox service directly."""
    try:
        print("Testing sandbox directly...")
        
        # Test health first
        health_response = requests.get("http://localhost:8001/health", timeout=10)
        if health_response.status_code != 200:
            print(f"❌ Sandbox health check failed: {health_response.status_code}")
            return False
        
        # Test code execution
        code_payload = {
            "code": "print('Hello from sandbox!')\nresult = 2 + 2\nprint(f'2 + 2 = {result}')"
        }
        
        response = requests.post("http://localhost:8001/execute", 
                               json=code_payload, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sandbox execution: {result}")
            return True
        else:
            print(f"❌ Sandbox execution failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Sandbox error: {e}")
        return False


def test_mcp_server():
    """Test the MCP server directly."""
    try:
        print("Testing mcp-server directly...")
        
        # Test health
        health_response = requests.get("http://localhost:8000/health", timeout=10)
        if health_response.status_code == 200:
            print(f"✅ MCP server health: {health_response.json()}")
            
            # Try to get available tools
            try:
                tools_response = requests.get("http://localhost:8000/mcp/tools", timeout=10)
                if tools_response.status_code == 200:
                    print(f"✅ MCP tools available: {tools_response.json()}")
                else:
                    print(f"⚠️ MCP tools endpoint: {tools_response.status_code}")
            except Exception as e:
                print(f"⚠️ MCP tools error: {e}")
            
            return True
        else:
            print(f"❌ MCP server health failed: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ MCP server error: {e}")
        return False


def test_code_executor():
    """Test the code-executor service directly."""
    try:
        print("Testing code-executor directly...")
        
        # Test health first
        health_response = requests.get("http://localhost:8004/health", timeout=10)
        if health_response.status_code == 200:
            print(f"✅ Code-executor health: {health_response.json()}")
            return True
        else:
            print(f"❌ Code-executor health failed: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Code-executor error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing MCP Services Directly")
    print("=" * 50)
    
    results = []
    
    # Test each service
    print("\n1. Testing Individual Services:")
    print("-" * 30)
    
    results.append(("Time Client", test_time_service()))
    results.append(("Sandbox", test_sandbox_service()))
    results.append(("MCP Server", test_mcp_server()))
    results.append(("Code Executor", test_code_executor()))
    
    # Summary
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY:")
    print("=" * 50)
    
    all_passed = True
    for service, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service:15} {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Status: {'✅ ALL SERVICES WORKING' if all_passed else '❌ SOME SERVICES FAILED'}")
    
    if all_passed:
        print("\n💡 All services are working! The middleware issue is likely:")
        print("   - Missing or misconfigured OpenAI API connection")
        print("   - Need to set up a local LLM service (like Ollama)")
        print("   - Or modify middleware to work without LLM")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main()) 