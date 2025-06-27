#!/usr/bin/env python3
"""
Simple test to debug root endpoint
"""
import requests

def test_endpoints():
    base_url = "http://localhost:8088"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Health status: {response.status_code}")
        print(f"Health response: {response.json()}")
    except Exception as e:
        print(f"Health error: {e}")
    
    print("\nTesting root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root status: {response.status_code}")
        if response.status_code == 200:
            print(f"Root response: {response.json()}")
        else:
            print(f"Root error: {response.text}")
    except Exception as e:
        print(f"Root error: {e}")
    
    print("\nTesting docs endpoint...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"Docs status: {response.status_code}")
    except Exception as e:
        print(f"Docs error: {e}")

if __name__ == "__main__":
    test_endpoints() 