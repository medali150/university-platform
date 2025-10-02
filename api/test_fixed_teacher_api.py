"""
Test the fixed teacher API endpoints
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_teacher_api():
    """Test the teacher listing API after database fixes"""
    print("🧪 Testing Teacher API After Database Fixes")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Try different admin credentials
        admin_credentials_list = [
            {"login": "admin", "password": "admin123"},
            {"login": "admin", "password": "password123"},
            {"login": "mohamedali.gh15@gmail.com", "password": "daligh15"},
        ]
        
        token = None
        print("1️⃣ Trying admin authentication...")
        
        for creds in admin_credentials_list:
            print(f"   Trying: {creds['login']}")
            response = await client.post(f"{BASE_URL}/auth/login", json=creds)
            if response.status_code == 200:
                token = response.json()["access_token"]
                print(f"✅ Authenticated as: {creds['login']}")
                break
            else:
                print(f"   ❌ Failed: {response.status_code}")
        
        if not token:
            print("❌ Could not authenticate with any admin credentials")
            return
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Admin authenticated")
        
        # Get teachers list
        print("\n2️⃣ Getting teachers list...")
        response = await client.get(f"{BASE_URL}/admin/teachers/", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            teachers = response.json()
            print(f"✅ Found {len(teachers)} teachers")
            
            print("\n📋 TEACHERS LIST:")
            for teacher in teachers:
                print(f"   👨‍🏫 {teacher['firstName']} {teacher['lastName']}")
                print(f"      Email: {teacher['email']}")
                print(f"      Login: {teacher['login']}")
                print(f"      Role: {teacher['role']}")
                print(f"      Created: {teacher['createdAt']}")
                if teacher.get('teacherInfo'):
                    print(f"      Teacher ID: {teacher['teacherInfo']['id']}")
                print()
        else:
            print(f"❌ Failed to get teachers: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_teacher_api())