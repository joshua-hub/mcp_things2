"""Time tool implementation."""
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from datetime import datetime, timezone
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Time Tool")

@app.get("/current-time", operation_id="get_current_time", summary="Get the current time in UTC format")
async def get_current_time() -> str:
    """Get the current time in UTC format.
    
    Returns:
        Current time in yyyy-mm-dd HH:MM UTC format
    """
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    logger.info(f"Time tool returning: {current_time}")
    return current_time

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Initialize FastAPI-MCP and mount it
mcp = FastApiMCP(app)
mcp.mount()

# Add MCP SSE endpoint for mcpo integration
@app.get("/mcp/sse")
async def mcp_sse_endpoint():
    """SSE endpoint for MCP protocol communication"""
    return mcp.sse_endpoint()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 