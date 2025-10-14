#!/usr/bin/env python3
"""
Test script to debug the API endpoint
"""

import requests
import json

def test_api():
    """Test the API endpoint directly."""
    url = "http://localhost:5000/api/analyze"
    
    test_data = {
        "prompt": "Tell me a joke",
        "smoothllm_num_copies": 10,
        "smoothllm_pert_type": "RandomPatchPerturbation",
        "smoothllm_pert_pct": 10,
        "target_model": "tinyllama"
    }
    
    try:
        print("Testing API endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Result: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_api()
