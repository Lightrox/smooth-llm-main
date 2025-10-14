#!/usr/bin/env python3
"""
Model Download Script for SmoothLLM Web Interface

This script downloads and configures the TinyLlama model for real analysis.
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import shutil

def download_tinyllama():
    """Download TinyLlama model and tokenizer."""
    print("🚀 Downloading TinyLlama model...")
    print("=" * 50)
    
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    try:
        print(f"📥 Downloading model: {model_name}")
        print("This may take a few minutes (model is ~2GB)...")
        
        # Download tokenizer
        print("1. Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("✅ Tokenizer downloaded successfully!")
        
        # Download model
        print("2. Downloading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        print("✅ Model downloaded successfully!")
        
        # Test the model
        print("3. Testing model...")
        test_prompt = "Hello, how are you?"
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
            model = model.cuda()
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_length=50,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"✅ Model test successful!")
        print(f"Test response: {response}")
        
        print("\n🎉 Model download completed successfully!")
        print("You can now run the web interface with real model analysis.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Ensure you have at least 4GB free disk space")
        print("3. Try running: pip install --upgrade transformers torch")
        return False

def check_system_requirements():
    """Check if system meets requirements."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check PyTorch
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    # Check Transformers
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
    except ImportError:
        print("❌ Transformers not installed")
        return False
    
    # Check disk space (rough estimate)
    import shutil
    free_space = shutil.disk_usage('.').free
    free_gb = free_space / (1024**3)
    print(f"✅ Free disk space: {free_gb:.1f} GB")
    
    if free_gb < 3:
        print("⚠️  Warning: Less than 3GB free space. Model download might fail.")
    
    return True

def main():
    """Main function."""
    print("🤖 SmoothLLM Model Downloader")
    print("=" * 50)
    
    # Check requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please install missing dependencies.")
        return
    
    print("\n" + "=" * 50)
    
    # Download model
    if download_tinyllama():
        print("\n🎯 Next steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Test with real model analysis!")
    else:
        print("\n💡 Alternative: The web interface will work with mock responses")
        print("   Run: python app.py (will use intelligent mock analysis)")

if __name__ == "__main__":
    main()
