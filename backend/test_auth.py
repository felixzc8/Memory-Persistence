#!/usr/bin/env python3
"""
Test script for Homi Chatbot Authentication
This script demonstrates how to use the authentication endpoints
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_FULL_NAME = "Test User"

class AuthTestClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def signup(self, email: str, password: str, full_name: str) -> dict:
        """Test user signup"""
        url = f"{self.base_url}/api/v1/auth/signup"
        data = {
            "email": email,
            "password": password,
            "full_name": full_name
        }
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token")
            print(f"✅ Signup successful for {email}")
            return result
        else:
            print(f"❌ Signup failed: {response.status_code} - {response.text}")
            return {}
    
    def signin(self, email: str, password: str) -> dict:
        """Test user signin"""
        url = f"{self.base_url}/api/v1/auth/signin"
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token")
            print(f"✅ Signin successful for {email}")
            return result
        else:
            print(f"❌ Signin failed: {response.status_code} - {response.text}")
            return {}
    
    def get_user_info(self) -> dict:
        """Test getting current user info"""
        if not self.access_token:
            print("❌ No access token available")
            return {}
        
        url = f"{self.base_url}/api/v1/auth/me"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User info retrieved: {result.get('email')}")
            return result
        else:
            print(f"❌ Get user info failed: {response.status_code} - {response.text}")
            return {}
    
    def test_chat(self, message: str) -> dict:
        """Test authenticated chat endpoint"""
        if not self.access_token:
            print("❌ No access token available")
            return {}
        
        url = f"{self.base_url}/api/v1/chat"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"message": message}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat successful: {result.get('response')[:50]}...")
            return result
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return {}
    
    def test_memory_search(self, query: str) -> dict:
        """Test memory search endpoint"""
        if not self.access_token:
            print("❌ No access token available")
            return {}
        
        url = f"{self.base_url}/api/v1/memories/search"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"query": query, "limit": 3}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Memory search successful: {len(result.get('memories', []))} memories found")
            return result
        else:
            print(f"❌ Memory search failed: {response.status_code} - {response.text}")
            return {}

def main():
    """Run authentication tests"""
    print("🚀 Starting Homi Chatbot Authentication Tests")
    print(f"📍 Server URL: {BASE_URL}")
    print("-" * 50)
    
    client = AuthTestClient()
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running!")
        return
    
    # Test 2: Sign up
    print("\n📝 Testing user signup...")
    signup_result = client.signup(TEST_EMAIL, TEST_PASSWORD, TEST_FULL_NAME)
    
    # Test 3: Get user info
    if signup_result:
        print("\n👤 Testing get user info...")
        client.get_user_info()
    
    # Test 4: Test chat
    if client.access_token:
        print("\n💬 Testing authenticated chat...")
        client.test_chat("Hello! I'm testing the authentication system.")
    
    # Test 5: Test memory search
    if client.access_token:
        print("\n🧠 Testing memory search...")
        client.test_memory_search("authentication")
    
    # Test 6: Sign in (to test login flow)
    print("\n🔐 Testing user signin...")
    client.signin(TEST_EMAIL, TEST_PASSWORD)
    
    print("\n✨ Authentication tests completed!")
    print("-" * 50)

if __name__ == "__main__":
    main() 