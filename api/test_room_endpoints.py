#!/usr/bin/env python3
"""Test room fetching endpoints"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_room_endpoints():
    print("=" * 80)
    print("TESTING ROOM ENDPOINTS")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        # Login as department head
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "chef.dept1@university.tn",
                "password": "Test123!"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"✅ Logged in successfully\n")
        
        # Test 1: Get rooms from timetable endpoint
        print("1. Testing /department-head/timetable/rooms")
        resp1 = await client.get(
            f"{BASE_URL}/department-head/timetable/rooms",
            headers=headers
        )
        print(f"   Status: {resp1.status_code}")
        if resp1.status_code == 200:
            rooms = resp1.json()
            print(f"   ✅ Found {len(rooms)} rooms")
            for room in rooms[:5]:  # Show first 5
                print(f"      - {room.get('code')} ({room.get('type')}) - {room.get('capacite')} places")
        else:
            print(f"   ❌ Error: {resp1.text}")
        
        # Test 2: Get room occupancy
        print("\n2. Testing /room-occupancy/rooms")
        resp2 = await client.get(
            f"{BASE_URL}/room-occupancy/rooms",
            headers=headers
        )
        print(f"   Status: {resp2.status_code}")
        if resp2.status_code == 200:
            data = resp2.json()
            if data.get('success'):
                rooms_data = data.get('data', [])
                print(f"   ✅ Found {len(rooms_data)} rooms with occupancy data")
                for room in rooms_data[:3]:
                    print(f"      - {room.get('roomName')} ({room.get('type')}) - {room.get('capacity')} places")
            else:
                print(f"   ❌ Success=False: {data}")
        else:
            print(f"   ❌ Error: {resp2.text}")
        
        # Test 3: Direct database query
        print("\n3. Testing direct database query")
        from prisma import Prisma
        db = Prisma()
        await db.connect()
        
        all_rooms = await db.salle.find_many()
        print(f"   ✅ Database has {len(all_rooms)} rooms")
        print(f"   Room codes:")
        for room in all_rooms[:10]:
            print(f"      - {room.code} ({room.type}) - {room.capacite} places")
        
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(test_room_endpoints())
