#!/usr/bin/env python3

import argparse
from PIL import Image
import json
from pathlib import Path

def inspect_metadata(image_path: str, raw: bool = False) -> None:
    """Display metadata from a PNG file"""
    try:
        with Image.open(image_path) as img:
            if not img.info:
                print(f"No metadata found in {image_path}")
                return
                
            if raw:
                # Print raw metadata
                print(json.dumps(img.info, indent=2))
            else:
                # Print formatted metadata
                print(f"\nMetadata for {image_path}:")
                print("-" * 50)
                
                # Generation parameters
                print("\nGeneration Parameters:")
                if "original_prompt" in img.info:
                    print(f"Original Prompt: {img.info['original_prompt']}")
                if "modified_prompt" in img.info:
                    print(f"Modified Prompt: {img.info['modified_prompt']}")
                if "negative_prompt" in img.info:
                    print(f"Negative Prompt: {img.info['negative_prompt']}")
                if "sampler" in img.info:
                    print(f"Sampler: {img.info['sampler']}")
                if "guidance_scale" in img.info:
                    print(f"Guidance Scale: {img.info['guidance_scale']}")
                if "seed" in img.info:
                    print(f"Seed: {img.info['seed']}")
                if "num_inference_steps" in img.info:
                    print(f"Steps: {img.info['num_inference_steps']}")
                
                # Model information
                print("\nModel Information:")
                if "model_type" in img.info:
                    print(f"Model Type: {img.info['model_type']}")
                if "scheduler_type" in img.info:
                    print(f"Scheduler: {img.info['scheduler_type']}")
                
                # System information
                print("\nSystem Information:")
                if "device" in img.info:
                    print(f"Device: {img.info['device']}")
                if "generation_time" in img.info:
                    print(f"Generated: {img.info['generation_time']}")
                
                # LoRA information
                if "loras" in img.info:
                    print("\nLoRA Information:")
                    loras = json.loads(img.info["loras"])
                    for lora in loras:
                        print(f"  - {lora['file']} (weight: {lora['weight']})")
                
    except Exception as e:
        print(f"Error reading {image_path}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Inspect metadata in PNG files')
    parser.add_argument('files', nargs='+', help='PNG files to inspect')
    parser.add_argument('--raw', action='store_true', help='Print raw metadata')
    
    args = parser.parse_args()
    
    for pattern in args.files:
        # Handle wildcards in filenames
        for file_path in Path('.').glob(pattern):
            if file_path.suffix.lower() == '.png':
                inspect_metadata(str(file_path), args.raw)

if __name__ == "__main__":
    main() 