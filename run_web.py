#!/usr/bin/env python3
"""
SmoothLLM Web Interface Runner

This script starts the SmoothLLM web interface with proper model configuration.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import torch
        import numpy
        import pandas
        print("✓ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def setup_model_config():
    """Setup model configuration for web interface."""
    # Check if model configs exist
    if not os.path.exists('lib/model_configs.py'):
        print("✗ Model configuration file not found")
        return False
    
    # For web interface, we'll use a simplified model config
    # Users can modify this based on their available models
    print("✓ Model configuration found")
    return True

def main():
    """Main function to start the web interface."""
    print("🚀 Starting SmoothLLM Web Interface...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup model config
    if not setup_model_config():
        sys.exit(1)
    
    print("✓ Starting Flask application...")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("📝 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down SmoothLLM Web Interface...")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
