#!/bin/bash

# Build script for Netlify deployment
echo "Building SmoothLLM for Netlify..."

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/css static/js templates

# Set permissions
chmod +x app.py

echo "Build completed successfully!"
