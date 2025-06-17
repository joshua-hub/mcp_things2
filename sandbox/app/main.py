"""Pure code execution sandbox."""
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel, constr
import subprocess
import os
from pathlib import Path
import re
import uvicorn
import logging
from typing import Dict, Any
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Code Execution Sandbox")

WORKSPACE_DIR = Path("/app/workspace")

# Package name validation regex
PACKAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\-_\.]+$')

# Known malicious or problematic packages
BLOCKED_PACKAGES = {
    'crypto-locker',
    'pythonapi',
    'python-api',
    'system',
    'snake',
    # Add more as needed
}

# Packages that require extra scrutiny
SUSPICIOUS_PACKAGES = {
    'cryptography',
    'crypto',
    'requests',
    'urllib3',
    'socket',
    'subprocess',
    # Add more as needed
}

class CodeRequest(BaseModel):
    code: str

class PipRequest(BaseModel):
    package: constr(min_length=1, max_length=100)  # Constrain package name length
    version: str = "latest"

class CodeResponse(BaseModel):
    success: bool
    output: str = ""
    error: str = ""

def validate_package_name(package: str) -> bool:
    """Validate package name against security rules."""
    if package.lower() in BLOCKED_PACKAGES:
        raise HTTPException(status_code=400, detail=f"Package {package} is blocked for security reasons")
    
    if not PACKAGE_NAME_PATTERN.match(package):
        raise HTTPException(status_code=400, detail="Invalid package name format")
    
    if package.lower() in SUSPICIOUS_PACKAGES:
        raise HTTPException(status_code=400, detail=f"Package {package} requires administrative approval")
    
    return True

@app.post("/execute", response_model=Dict[str, Any])
async def execute_code(request: CodeRequest):
    """
    Execute Python code in a sandboxed environment.
    
    Args:
        request: CodeRequest containing the Python code to execute
        
    Returns:
        Dict containing execution results or error information
    """
    try:
        # Create a temporary file in the workspace
        workspace_dir = "/app/workspace"
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Execute the code
        logger.info(f"Executing code in sandbox")
        result = {}
        
        # Create a new namespace for execution
        namespace = {}
        
        # Execute the code
        exec(request.code, namespace)
        
        # Get any output variables
        for key, value in namespace.items():
            if not key.startswith('__'):
                result[key] = str(value)
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/pip/install", response_model=CodeResponse)
async def pip_install(request: PipRequest):
    try:
        # Validate package name
        validate_package_name(request.package)
        
        # Construct pip command
        pip_cmd = ['pip', 'install', '--no-cache-dir']
        if request.version != "latest":
            pip_cmd.append(f"{request.package}=={request.version}")
        else:
            pip_cmd.append(request.package)

        # Run pip install
        process = subprocess.run(
            pip_cmd,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout for pip
        )

        return CodeResponse(
            success=process.returncode == 0,
            output=process.stdout,
            error=process.stderr
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    uvicorn.run(app, host="0.0.0.0", port=8001) 