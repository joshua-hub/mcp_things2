#!/usr/bin/env python3

import requests
import base64
import argparse
from typing import Optional, List
from datetime import datetime

def generate_image(
    prompt: str,
    negative_prompt: Optional[str] = "",
    sampler: Optional[str] = "dpm solver ++",
    num_images: Optional[int] = 1,
    seed: Optional[int] = None,
    guidance_scale: Optional[float] = 7.0,
    loras: Optional[List[tuple]] = None  # Add LoRA support
) -> None:
    
    url = "http://localhost:9000/generate"
    
    # Convert LoRA tuples to dict format
    lora_configs = None
    if loras:
        lora_configs = [{"filename": name, "weight": float(weight)} for name, weight in loras]
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "sampler": sampler,
        "num_images": num_images,
        "seed": seed,
        "guidance_scale": guidance_scale,
        "loras": lora_configs
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save each image with timestamp and index
        for i, img_data in enumerate(data['images']):
            img_bytes = base64.b64decode(img_data)
            filename = f"generated_{timestamp}_{i+1}.png"
            with open(filename, "wb") as f:
                f.write(img_bytes)
            print(f"Saved image {i+1} as {filename} with seed {data['seeds'][i]}")
            
        # Print parameters used
        print("\nGeneration parameters:")
        for key, value in data['parameters'].items():
            print(f"{key}: {value}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate images using SDXL API')
    parser.add_argument('prompt', help='The prompt to generate images from')
    parser.add_argument('--negative', help='Negative prompt', default="")
    parser.add_argument('--sampler', help='Sampler to use', choices=['dpm solver ++', 'euler a', 'ddim'], default='dpm solver ++')
    parser.add_argument('--num', type=int, help='Number of images to generate', default=1)
    parser.add_argument('--seed', type=int, help='Seed for generation')
    parser.add_argument('--cfg', type=float, help='Guidance scale (2-15)', default=7.0)
    parser.add_argument('--lora', nargs=2, action='append', metavar=('FILE', 'WEIGHT'),
                       help='LoRA file and weight (can be used multiple times)')
    
    args = parser.parse_args()
    
    generate_image(
        prompt=args.prompt,
        negative_prompt=args.negative,
        sampler=args.sampler,
        num_images=args.num,
        seed=args.seed,
        guidance_scale=args.cfg,
        loras=args.lora
    )

if __name__ == "__main__":
    main() 