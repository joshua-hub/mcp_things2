#!/usr/bin/env python3

import sys
import httpx
import asyncio
from typing import Optional

MIDDLEWARE_URL = "http://localhost:8001"

async def send_prompt(prompt: str) -> Optional[str]:
    """Send a prompt to the middleware and get the response."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MIDDLEWARE_URL}/chat",
                json={"content": prompt}
            )
            response.raise_for_status()
            return response.json()["response"]
    except httpx.HTTPError as e:
        print(f"Error communicating with middleware: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 testing-mcp.py \"your prompt here\"")
        sys.exit(1)

    prompt = sys.argv[1]
    print(f"\nSending prompt: {prompt}\n")
    
    response = await send_prompt(prompt)
    if response:
        print(f"Response:\n{response}\n")
    else:
        print("Failed to get response from middleware")

if __name__ == "__main__":
    asyncio.run(main()) 