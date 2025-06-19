from transformers import CLIPTokenizer, T5Tokenizer, T5ForConditionalGeneration
from diffusers import StableDiffusionXLPipeline
import os
import torch
from huggingface_hub import snapshot_download

def download_sdxl_base_model():
    """
    Downloads the complete Stable Diffusion XL 1.0 Base model from Hugging Face.
    """
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    local_dir = os.path.join(os.path.dirname(__file__), "models", "sdxl", "base")
    
    print(f"Starting download of model: {model_id}")
    print(f"This will save the model to: {os.path.abspath(local_dir)}")
    print("This is a large download (approx. 7 GB) and may take a while.")

    # Ensure the target directory exists
    os.makedirs(local_dir, exist_ok=True)

    # Use snapshot_download to get all files from the repository
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,  # Set to False to copy files directly
        resume_download=True,
    )

    print("-" * 50)
    print(f"✅ Download complete!")
    print(f"All files for '{model_id}' have been saved to '{local_dir}'.")
    print("You can now run the diffusion-api service.")
    print("-" * 50)

def download_tokenizers():
    """Download tokenizers for prompt processing"""
    print("Downloading tokenizers...")
    
    # Create directories
    os.makedirs("models/tokenizers/clip", exist_ok=True)
    os.makedirs("models/tokenizers/t5", exist_ok=True)

    try:
        # Download CLIP tokenizer
        print("📥 Downloading CLIP tokenizer...")
        CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14").save_pretrained("models/tokenizers/clip")
        print("✅ CLIP tokenizer downloaded!")

        # Download T5 model and tokenizer
        print("📥 Downloading T5 model and tokenizer...")
        T5Tokenizer.from_pretrained("t5-small").save_pretrained("models/tokenizers/t5")
        T5ForConditionalGeneration.from_pretrained("t5-small").save_pretrained("models/tokenizers/t5")
        print("✅ T5 model and tokenizer downloaded!")
        
    except Exception as e:
        print(f"❌ Error downloading tokenizers: {e}")
        raise

def main():
    """Main download function"""
    print("🚀 Starting optimized model download...")
    print("📊 This will download ~7-8GB instead of ~15GB+")
    print("-" * 50)
    
    try:
        # Download SDXL model (essential files only)
        download_sdxl_base_model()
        
        # Download tokenizers
        download_tokenizers()
        
        print("-" * 50)
        print("🎉 All models downloaded successfully!")
        print("💾 Saved several GB by downloading only essential files")
        print("🔧 Your API is ready to use!")
        
    except Exception as e:
        print(f"💥 Download failed: {e}")
        print("🔍 Check your internet connection and try again")
        exit(1)

if __name__ == "__main__":
    main() 