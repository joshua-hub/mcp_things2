from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import os

app = FastAPI(title="SDXL Style Browser", description="Browse and explore SDXL styles")

# Diffusion API base URL
DIFFUSION_API_BASE = os.environ.get("DIFFUSION_API_URL", "http://diffusion-api:8000")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main style browser page"""
    with open("/app/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/styles")
async def get_styles():
    """Proxy styles list from diffusion API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DIFFUSION_API_BASE}/v1/styles")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Unable to connect to diffusion API: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Diffusion API error: {e.response.text}")

@app.get("/api/styles/{style_name}")
async def get_style_details(style_name: str):
    """Proxy specific style details from diffusion API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DIFFUSION_API_BASE}/v1/styles/{style_name}")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Unable to connect to diffusion API: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Diffusion API error: {e.response.text}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DIFFUSION_API_BASE}/v1/health")
            diffusion_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        diffusion_status = "unreachable"
    
    return {
        "status": "healthy",
        "diffusion_api": diffusion_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 