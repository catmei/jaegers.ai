#!/usr/bin/env python3
"""
Test script for the Video Generation API
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5001"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_api_info():
    """Test the root endpoint"""
    print("\n📋 Testing API info...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API info failed: {e}")
        return False

def test_video_generation(topic="lebron james and the lakers"):
    """Test the video generation endpoint"""
    print(f"\n🎬 Testing video generation with topic: '{topic}'...")
    try:
        payload = {"topic": topic}
        print(f"Sending payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/generate-video",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Generated video structure:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Video Generation API")
    print("="*50)
    
    # Test health check
    health_ok = test_health_check()
    
    # Test API info
    info_ok = test_api_info()
    
    # Test video generation
    video_ok = test_video_generation()
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   API Info: {'✅ PASS' if info_ok else '❌ FAIL'}")
    print(f"   Video Generation: {'✅ PASS' if video_ok else '❌ FAIL'}")
    
    if all([health_ok, info_ok, video_ok]):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the server logs.")

if __name__ == "__main__":
    main() 