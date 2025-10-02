"""
Simple authentication test
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_auth():
    """Test authentication"""
    credentials = {
        "login": "souhir",
        "password": "daligh15"
    }
    
    print("Testing authentication with:")
    print(json.dumps(credentials, indent=2))
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json=credentials
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Authentication successful!")
            token = data["access_token"]
            print(f"Token: {token[:50]}...")
            return token
        else:
            print("❌ Authentication failed")
            return None

if __name__ == "__main__":
    asyncio.run(test_auth())