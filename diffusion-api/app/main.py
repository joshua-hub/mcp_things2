from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
import torch
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler, DDIMScheduler, DPMSolverMultistepScheduler
import base64
from io import BytesIO
import random
from transformers import CLIPTokenizer, T5Tokenizer, T5ForConditionalGeneration
import re
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
import os
import json
from fastapi_mcp import FastApiMCP
import glob

class SamplerType(str, Enum):
    DPM_SOLVER = "dpm solver ++"
    EULER_A = "euler a"
    DDIM = "ddim"

class LoraConfig(BaseModel):
    filename: str
    weight: float = Field(ge=0.0, le=1.0)

class StyleModel(BaseModel):
    name: str
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    source_file: Optional[str] = None

class StyleSuggestionRequest(BaseModel):
    description: str
    max_suggestions: Optional[int] = Field(default=3, ge=1, le=10)

class StyleSuggestionResponse(BaseModel):
    suggestions: List[StyleModel]

class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    sampler: Optional[SamplerType] = SamplerType.DPM_SOLVER
    num_images: Optional[int] = Field(default=1, ge=1)
    seed: Optional[int] = None
    guidance_scale: Optional[float] = Field(default=7.0, ge=2.0, le=15.0)
    loras: Optional[List[LoraConfig]] = None
    style_name: Optional[str] = None  # New field for style selection

    @validator('guidance_scale')
    def validate_guidance_scale(cls, v):
        if v < 2.0 or v > 15.0:
            raise ValueError('Guidance scale must be between 2 and 15')
        return v
        
    @validator('prompt')
    def process_prompt(cls, v):
        return rewrite_prompt(v)
        
    @validator('negative_prompt')
    def process_negative_prompt(cls, v):
        if v:
            return rewrite_prompt(v)
        return v

class GenerationResponse(BaseModel):
    images: List[str]
    seeds: List[int]
    parameters: dict

app = FastAPI(
    title="Stable Diffusion API",
    description="""
    API v1 for generating images using Stable Diffusion XL.
    
    Features:
    - Image generation with customizable parameters
    - LoRA support with adjustable weights
    - Multiple sampling methods
    - Automatic prompt optimization for token limits
    
    Endpoints:
    - /v1/generate - Generate images
    - /v1/models - List available models
    - /v1/loras - List available LoRAs
    - /v1/samplers - List available samplers
    - /v1/health - Check API status
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize FastAPI-MCP
mcp = FastApiMCP(app)

# Mount the MCP server to make endpoints available as tools
mcp.mount()

# Global pipeline variable
pipeline = None

# Update these paths
MODEL_DIR = "/app/models/sdxl/base"  # Changed to point to the diffusers format directory
CLIP_PATH = "/app/models/tokenizers/clip"
T5_PATH = "/app/models/tokenizers/t5"

def get_model_path():
    """Get the path to the diffusers model directory"""
    if not os.path.exists(MODEL_DIR):
        raise Exception(f"Model directory {MODEL_DIR} does not exist")
    
    # Check if model_index.json exists (indicates diffusers format)
    model_index = os.path.join(MODEL_DIR, "model_index.json")
    if not os.path.exists(model_index):
        raise Exception(f"No model_index.json found in {MODEL_DIR}. Run download_models.py first.")
    
    return MODEL_DIR

# Get model path dynamically
MODEL_PATH = get_model_path()

# Add this near the top with other globals
tokenizer = CLIPTokenizer.from_pretrained(
    CLIP_PATH,
    local_files_only=True
)
prompt_rewriter = T5ForConditionalGeneration.from_pretrained(
    T5_PATH,
    local_files_only=True,
    torch_dtype=torch.float16
)
prompt_tokenizer = T5Tokenizer.from_pretrained(
    T5_PATH,
    local_files_only=True
)
MAX_TOKENS = 77

def rewrite_prompt(prompt: str) -> str:
    """Use T5 to rewrite prompt, trying multiple lengths to preserve detail"""
    tokens = tokenizer.encode(prompt)
    if len(tokens) <= MAX_TOKENS:
        return prompt
        
    # Try different target lengths, from longest to shortest
    target_lengths = [70, 60, 50, 40]  # All under MAX_TOKENS=77
    best_prompt = None
    
    for length in target_lengths:
        input_text = f"Summarize for stable diffusion, preserve details: {prompt}"
        inputs = prompt_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        
        # Generate version targeting this length
        outputs = prompt_rewriter.generate(
            inputs.input_ids,
            max_length=length,
            min_length=max(10, length-10),
            num_beams=4,
            temperature=0.7,
            no_repeat_ngram_size=2
        )
        
        candidate = prompt_tokenizer.decode(outputs[0], skip_special_tokens=True)
        candidate_tokens = len(tokenizer.encode(candidate))
        
        if candidate_tokens <= MAX_TOKENS:
            best_prompt = candidate
            break
    
    if best_prompt is None:
        # Fallback to shortest possible if all attempts are too long
        best_prompt = rewrite_prompt_aggressive(prompt)
    
    print(f"Original prompt ({len(tokens)} tokens): {prompt}")
    print(f"Rewritten prompt ({len(tokenizer.encode(best_prompt))} tokens): {best_prompt}")
    print(f"Token reduction: {len(tokens)} -> {len(tokenizer.encode(best_prompt))}")
    
    return best_prompt

def rewrite_prompt_aggressive(prompt: str) -> str:
    """Aggressive shortening as a last resort"""
    input_text = f"Summarize very briefly: {prompt}"
    inputs = prompt_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    
    outputs = prompt_rewriter.generate(
        inputs.input_ids,
        max_length=40,
        min_length=10,
        num_beams=4,
        temperature=0.7,
        no_repeat_ngram_size=2
    )
    
    return prompt_tokenizer.decode(outputs[0], skip_special_tokens=True)

# Style management functions
def load_all_styles():
    """Load all styles from JSON files in sdxl_styles directory"""
    styles = {}
    styles_dir = "/app/sdxl_styles"
    
    if not os.path.exists(styles_dir):
        print(f"Warning: Styles directory {styles_dir} not found")
        return styles
    
    # Load all JSON files in the styles directory
    for json_file in glob.glob(os.path.join(styles_dir, "*.json")):
        try:
            with open(json_file, 'r') as f:
                style_data = json.load(f)
                source_file = os.path.basename(json_file)
                
                # Handle both list and dict formats
                if isinstance(style_data, list):
                    for style in style_data:
                        if 'name' in style:
                            styles[style['name']] = StyleModel(
                                name=style['name'],
                                prompt=style.get('prompt'),
                                negative_prompt=style.get('negative_prompt'),
                                source_file=source_file
                            )
                elif isinstance(style_data, dict):
                    for name, style in style_data.items():
                        styles[name] = StyleModel(
                            name=name,
                            prompt=style.get('prompt'),
                            negative_prompt=style.get('negative_prompt'),
                            source_file=source_file
                        )
        except Exception as e:
            print(f"Error loading styles from {json_file}: {e}")
    
    print(f"Loaded {len(styles)} styles from {styles_dir}")
    return styles

def apply_style_to_prompt(prompt: str, style_name: str, available_styles: dict) -> str:
    """Apply a style to a user prompt"""
    if style_name not in available_styles:
        raise ValueError(f"Style '{style_name}' not found")
    
    style = available_styles[style_name]
    
    # If style has a prompt template, replace {prompt} with user's prompt
    if style.prompt and '{prompt}' in style.prompt:
        return style.prompt.replace('{prompt}', prompt)
    elif style.prompt:
        # If style has prompt but no placeholder, append user prompt
        return f"{style.prompt}, {prompt}"
    else:
        # Style only has negative prompt, return original prompt
        return prompt

def suggest_styles(description: str, available_styles: dict, max_suggestions: int = 3) -> List[StyleModel]:
    """Suggest styles based on user description using keyword matching"""
    description_lower = description.lower()
    
    # Keywords for different style categories
    style_keywords = {
        'cinematic': ['cinematic', 'movie', 'film', 'dramatic', 'epic', 'hollywood'],
        'photograph': ['photo', 'realistic', 'portrait', 'camera', 'real', 'picture'],
        'artistic': ['art', 'painting', 'artistic', 'creative', 'abstract', 'style'],
        'enhance': ['better', 'quality', 'enhance', 'improve', 'detailed', 'sharp'],
        'negative': ['fix', 'avoid', 'remove', 'clean', 'negative'],
        'masterpiece': ['masterpiece', 'best', 'amazing', 'perfect', 'detailed'],
        'sharp': ['sharp', 'focus', 'detailed', 'clear', 'crisp'],
        'pony': ['pony', 'mlp', 'cartoon', 'cute', 'colorful']
    }
    
    # Score styles based on keyword matches
    style_scores = {}
    for style_name, style in available_styles.items():
        score = 0
        style_name_lower = style_name.lower()
        
        # Check style name for direct matches
        for keyword in description_lower.split():
            if keyword in style_name_lower:
                score += 10
        
        # Check category keywords
        for category, keywords in style_keywords.items():
            if category in style_name_lower:
                for keyword in keywords:
                    if keyword in description_lower:
                        score += 5
        
        # Additional scoring for specific patterns
        if 'realistic' in description_lower and 'photograph' in style_name_lower:
            score += 8
        if 'cinematic' in description_lower and 'cinematic' in style_name_lower:
            score += 8
        if 'art' in description_lower and any(word in style_name_lower for word in ['masterpiece', 'artistic']):
            score += 6
        
        if score > 0:
            style_scores[style_name] = score
    
    # Sort by score and return top suggestions
    sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
    suggestions = []
    
    for style_name, score in sorted_styles[:max_suggestions]:
        suggestions.append(available_styles[style_name])
    
    # If no matches found, return some popular default styles
    if not suggestions:
        default_styles = ['Fooocus Enhance', 'Fooocus Photograph', 'Fooocus Cinematic']
        for default in default_styles:
            if default in available_styles and len(suggestions) < max_suggestions:
                suggestions.append(available_styles[default])
    
    return suggestions

# Global styles variable
AVAILABLE_STYLES = {}

def get_scheduler(sampler_type: SamplerType):
    if sampler_type == SamplerType.DPM_SOLVER:
        return DPMSolverMultistepScheduler.from_pretrained(MODEL_PATH, subfolder="scheduler")
    elif sampler_type == SamplerType.EULER_A:
        return EulerAncestralDiscreteScheduler.from_pretrained(MODEL_PATH, subfolder="scheduler")
    elif sampler_type == SamplerType.DDIM:
        return DDIMScheduler.from_pretrained(MODEL_PATH, subfolder="scheduler")

@app.on_event("startup")
async def startup_event():
    global pipeline, AVAILABLE_STYLES
    try:
        print(f"Loading model from: {MODEL_PATH}")
        pipeline = StableDiffusionXLPipeline.from_pretrained(
            MODEL_PATH,  # Now points to the diffusers format directory
            torch_dtype=torch.float16,
            use_safetensors=True,
            local_files_only=True
        )
        
        if torch.cuda.is_available():
            pipeline = pipeline.to("cuda")
        
        # Load styles
        print("Loading SDXL styles...")
        AVAILABLE_STYLES = load_all_styles()
        print(f"Loaded {len(AVAILABLE_STYLES)} styles")
            
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

@app.post("/v1/generate", response_model=GenerationResponse)
async def generate_images(request: GenerationRequest):
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Create a copy of the pipeline for this generation
        current_pipeline = pipeline
        
        # Load LoRAs if specified
        if request.loras:
            current_pipeline = load_loras(pipeline.copy(), request.loras)
            
        # Set scheduler based on request
        current_pipeline.scheduler = get_scheduler(request.sampler)
        
        # Store original prompt before any modification
        original_prompt = request.prompt
        
        # Apply style if specified
        style_applied = None
        final_prompt = request.prompt
        if request.style_name:
            try:
                final_prompt = apply_style_to_prompt(request.prompt, request.style_name, AVAILABLE_STYLES)
                style_applied = request.style_name
                print(f"Applied style '{request.style_name}': '{request.prompt}' -> '{final_prompt}'")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Generate seeds
        seeds = []
        if request.seed is not None:
            seeds = [request.seed] + [random.randint(0, 2**32 - 1) for _ in range(request.num_images - 1)]
        else:
            seeds = [random.randint(0, 2**32 - 1) for _ in range(request.num_images)]
        
        # Generate images
        images = []
        for i, seed in enumerate(seeds):
            generator = torch.Generator(device='cuda').manual_seed(seed)
            output = current_pipeline(
                prompt=final_prompt,
                negative_prompt=request.negative_prompt,
                guidance_scale=request.guidance_scale,
                generator=generator,
                num_inference_steps=30
            )
            
            # Convert to base64 with metadata
            for image in output.images:
                # Create metadata
                metadata = PngInfo()
                
                # Generation parameters
                metadata.add_text("original_prompt", original_prompt)
                metadata.add_text("styled_prompt", final_prompt)
                metadata.add_text("style_applied", style_applied or "none")
                metadata.add_text("negative_prompt", request.negative_prompt or "")
                metadata.add_text("sampler", str(request.sampler))
                metadata.add_text("guidance_scale", str(request.guidance_scale))
                metadata.add_text("seed", str(seed))
                metadata.add_text("num_inference_steps", "30")
                
                # LoRA information
                if request.loras:
                    metadata.add_text("loras", json.dumps([
                        {"file": l.filename, "weight": l.weight} 
                        for l in request.loras
                    ]))
                
                # Model information
                metadata.add_text("model_path", MODEL_PATH)
                metadata.add_text("model_type", "SDXL")
                metadata.add_text("scheduler_type", current_pipeline.scheduler.__class__.__name__)
                
                # System information
                metadata.add_text("torch_version", torch.__version__)
                metadata.add_text("device", str(current_pipeline.device))
                metadata.add_text("generation_time", datetime.now().isoformat())
                
                # Save image with metadata
                buffered = BytesIO()
                image.save(buffered, format="PNG", pnginfo=metadata)
                images.append(base64.b64encode(buffered.getvalue()).decode())
        
        return GenerationResponse(
            images=images,
            seeds=seeds,
            parameters={
                "original_prompt": original_prompt,
                "styled_prompt": final_prompt,
                "style_applied": style_applied,
                "negative_prompt": request.negative_prompt,
                "sampler": request.sampler,
                "guidance_scale": request.guidance_scale,
                "num_inference_steps": 30,
                "scheduler_type": current_pipeline.scheduler.__class__.__name__,
                "loras": [{"file": l.filename, "weight": l.weight} for l in request.loras] if request.loras else None
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/health")
async def health_check():
    return {"status": "healthy", "model_loaded": pipeline is not None}

def get_available_loras():
    """List available LoRA files"""
    lora_path = os.path.join(os.path.dirname(MODEL_PATH), "loras")
    if not os.path.exists(lora_path):
        return []
    return [f for f in os.listdir(lora_path) if f.endswith('.safetensors')]

@app.get("/v1/loras")
async def list_loras():
    """Endpoint to list available LoRAs"""
    return {"loras": get_available_loras()}

def load_loras(pipeline, lora_configs: List[LoraConfig]):
    """Load and apply LoRA weights"""
    available_loras = get_available_loras()
    for lora in lora_configs:
        if lora.filename not in available_loras:
            raise HTTPException(
                status_code=400, 
                detail=f"LoRA file {lora.filename} not found. Available: {available_loras}"
            )
        
        lora_path = os.path.join(os.path.dirname(MODEL_PATH), "loras", lora.filename)
        pipeline.load_lora_weights(lora_path, weight=lora.weight)
    return pipeline 

def get_available_models():
    """List available models in the models directory"""
    models_base_path = "/app/models/sdxl"
    if not os.path.exists(models_base_path):
        return []
    
    models = []
    for item in os.listdir(models_base_path):
        item_path = os.path.join(models_base_path, item)
        if os.path.isdir(item_path):
            # Check if it's a diffusers format model (has model_index.json)
            if os.path.exists(os.path.join(item_path, "model_index.json")):
                models.append(item)
    return models

@app.get("/v1/models")
async def list_models():
    """Endpoint to list available models"""
    return {
        "models": get_available_models(),
        "current_model": os.path.basename(MODEL_PATH)
    }

@app.get("/v1/samplers")
async def list_samplers():
    """Endpoint to list available samplers"""
    return {
        "samplers": [
            {
                "name": sampler.value,
                "type": sampler.name,
                "description": {
                    "dpm solver ++": "DPM-Solver++: Fast with good quality",
                    "euler a": "Euler Ancestral: Good for creative variations",
                    "ddim": "DDIM: Deterministic, good for consistency"
                }.get(sampler.value, "")
            }
            for sampler in SamplerType
        ]
    }

@app.get("/v1/styles")
async def list_styles():
    """Endpoint to list all available SDXL styles"""
    if not AVAILABLE_STYLES:
        return {"styles": [], "total": 0}
    
    styles_list = []
    for name, style in AVAILABLE_STYLES.items():
        styles_list.append({
            "name": style.name,
            "has_prompt_template": bool(style.prompt and '{prompt}' in style.prompt),
            "has_negative_prompt": bool(style.negative_prompt),
            "source_file": style.source_file,
            "preview_prompt": style.prompt[:100] + "..." if style.prompt and len(style.prompt) > 100 else style.prompt
        })
    
    return {
        "styles": sorted(styles_list, key=lambda x: x["name"]),
        "total": len(styles_list)
    }

@app.get("/v1/styles/{style_name}")
async def get_style(style_name: str):
    """Get details for a specific style"""
    if style_name not in AVAILABLE_STYLES:
        raise HTTPException(status_code=404, detail=f"Style '{style_name}' not found")
    
    style = AVAILABLE_STYLES[style_name]
    return {
        "name": style.name,
        "prompt": style.prompt,
        "negative_prompt": style.negative_prompt,
        "source_file": style.source_file,
        "has_prompt_template": bool(style.prompt and '{prompt}' in style.prompt)
    }

@app.post("/v1/styles/suggest", response_model=StyleSuggestionResponse)
async def suggest_styles_endpoint(request: StyleSuggestionRequest):
    """Suggest styles based on user description"""
    if not AVAILABLE_STYLES:
        raise HTTPException(status_code=500, detail="No styles loaded")
    
    suggestions = suggest_styles(
        request.description, 
        AVAILABLE_STYLES, 
        request.max_suggestions
    )
    
    return StyleSuggestionResponse(suggestions=suggestions) 