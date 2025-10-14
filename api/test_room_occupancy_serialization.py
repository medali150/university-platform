"""
Test script to verify room occupancy API serialization
"""
import asyncio
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.db.prisma_client import get_prisma
from datetime import datetime, timedelta
import json

async def test_room_occupancy():
    """Test room occupancy data serialization"""
    prisma = await get_prisma().__anext__()
    
    try:
        # Calculate week dates
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        
        print(f"Testing room occupancy for week: {monday} to {sunday}")
        print(f"Monday type: {type(monday)}")
        print(f"Sunday type: {type(sunday)}")
        
        # Get all rooms with their schedules
        rooms = await prisma.salle.find_many(
            include={
                "emploitemps": {
                    "where": {
                        "date": {
                            "gte": monday,
                            "lte": sunday
                        }
                    },
                    "include": {
                        "matiere": True,
                        "enseignant": {
                            "include": {"utilisateur": True}
                        },
                        "groupe": True
                    }
                }
            }
        )
        
        print(f"\nFound {len(rooms)} rooms")
        
        if rooms:
            room = rooms[0]
            print(f"\nFirst room: {room.code}")
            print(f"Room ID type: {type(room.id)}")
            print(f"Room capacity type: {type(room.capacite)}")
            
            if room.emploitemps:
                schedule = room.emploitemps[0]
                print(f"\nFirst schedule:")
                print(f"  Date: {schedule.date} (type: {type(schedule.date)})")
                print(f"  Start time: {schedule.heure_debut} (type: {type(schedule.heure_debut)})")
                print(f"  Has weekday method: {hasattr(schedule.date, 'weekday')}")
                
                # Try to serialize
                test_data = {
                    "roomId": room.id,
                    "roomName": room.code,
                    "capacity": room.capacite,
                    "scheduleDate": schedule.date,
                    "startTime": schedule.heure_debut
                }
                
                print("\nAttempting JSON serialization...")
                try:
                    json_str = json.dumps(test_data)
                    print("✗ Serialization failed - should have raised error")
                except TypeError as e:
                    print(f"✓ Got expected error: {e}")
                
                # Now try with string conversion
                test_data_fixed = {
                    "roomId": room.id,
                    "roomName": room.code,
                    "capacity": room.capacite,
                    "scheduleDate": str(schedule.date),
                    "startTime": str(schedule.heure_debut)
                }
                
                print("\nAttempting JSON serialization with string conversion...")
                try:
                    json_str = json.dumps(test_data_fixed)
                    print("✓ Serialization successful!")
                    print(f"Result: {json_str[:100]}...")
                except TypeError as e:
                    print(f"✗ Still failed: {e}")
                    
    except Exception as e:
        import traceback
        print(f"\n✗ Error: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_room_occupancy())
