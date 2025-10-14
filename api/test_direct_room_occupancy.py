"""
Direct test of room occupancy endpoint with database data
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.db.prisma_client import get_prisma

async def test_room_occupancy_direct():
    """Test room occupancy logic directly"""
    prisma = await get_prisma().__anext__()
    
    try:
        # Calculate week dates
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        
        print(f"Testing for week: {monday} to {sunday}")
        print(f"Today's date type: {type(today)}")
        
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
            },
            take=3  # Just first 3 rooms for testing
        )
        
        print(f"\nFound {len(rooms)} rooms")
        
        if not rooms:
            print("No rooms found in database!")
            return
        
        # Process first room
        room = rooms[0]
        print(f"\nProcessing room: {room.code}")
        print(f"  Type: {room.type}")
        print(f"  Capacity: {room.capacite}")
        print(f"  Schedules this week: {len(room.emploitemps)}")
        
        if room.emploitemps:
            for i, schedule in enumerate(room.emploitemps[:3]):  # First 3 schedules
                print(f"\n  Schedule {i+1}:")
                print(f"    Date: {schedule.date} (type: {type(schedule.date).__name__})")
                print(f"    Start time: {schedule.heure_debut} (type: {type(schedule.heure_debut).__name__})")
                
                # Test the logic we use in the API
                schedule_date = schedule.date
                if hasattr(schedule_date, 'date'):
                    schedule_date = schedule_date.date()
                print(f"    Processed date: {schedule_date} (type: {type(schedule_date).__name__})")
                
                day_index = schedule_date.weekday()
                days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
                if day_index < 6:
                    day_name = days[day_index]
                    print(f"    Day: {day_name}")
                
                # Test time processing
                start_time = schedule.heure_debut
                if hasattr(start_time, 'time'):
                    start_time = start_time.time()
                print(f"    Processed time: {start_time} (type: {type(start_time).__name__})")
                
                if schedule.matiere:
                    print(f"    Subject: {schedule.matiere.nom}")
                if schedule.groupe:
                    print(f"    Group: {schedule.groupe.nom}")
        
        # Now test JSON serialization
        print("\n" + "="*50)
        print("Testing JSON serialization...")
        
        import json
        from fastapi.encoders import jsonable_encoder
        
        test_data = {
            "roomId": room.id,
            "roomName": room.code,
            "capacity": room.capacite,
            "type": room.type
        }
        
        if room.emploitemps:
            schedule = room.emploitemps[0]
            test_data["sampleSchedule"] = {
                "date": schedule.date,
                "start_time": schedule.heure_debut
            }
        
        # Try direct JSON (should fail)
        print("\n1. Direct json.dumps (should fail):")
        try:
            json_str = json.dumps(test_data)
            print("  ❌ Unexpectedly succeeded!")
        except TypeError as e:
            print(f"  ✅ Expected error: {e}")
        
        # Try with jsonable_encoder (should succeed)
        print("\n2. With jsonable_encoder (should succeed):")
        try:
            encoded = jsonable_encoder(test_data)
            json_str = json.dumps(encoded)
            print(f"  ✅ Success! Length: {len(json_str)} bytes")
            print(f"  Sample: {json_str[:200]}...")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
    
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(test_room_occupancy_direct())
