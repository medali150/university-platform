#!/usr/bin/env python3
"""Quick verification that room fetching works correctly"""

import asyncio
import httpx

async def quick_test():
    print("🔍 Quick Room Fetching Test\n")
    
    async with httpx.AsyncClient() as client:
        # Login
        login = await client.post(
            "http://localhost:8000/auth/login",
            json={"email": "chef.dept1@university.tn", "password": "Test123!"}
        )
        
        if login.status_code != 200:
            print("❌ Login failed")
            return
        
        token = login.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test rooms endpoint
        rooms_resp = await client.get(
            "http://localhost:8000/department-head/timetable/rooms",
            headers=headers
        )
        
        print(f"Status: {rooms_resp.status_code}")
        
        if rooms_resp.status_code == 200:
            rooms = rooms_resp.json()
            print(f"✅ SUCCESS: Found {len(rooms)} rooms\n")
            print("Sample rooms:")
            for room in rooms[:5]:
                print(f"  • {room['code']:8s} | {room['type']:8s} | {room['capacite']:3d} places")
        else:
            print(f"❌ FAILED: {rooms_resp.text}")

if __name__ == "__main__":
    asyncio.run(quick_test())
