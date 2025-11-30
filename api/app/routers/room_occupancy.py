from fastapi import APIRouter, Depends, HTTPException, Query
from prisma import Prisma
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.db.prisma_client import get_prisma
from app.core.deps import require_role, get_current_user

router = APIRouter(prefix="/room-occupancy", tags=["Room Occupancy"])
logger = logging.getLogger(__name__)


@router.get("/rooms")
async def get_rooms_occupancy(
    week_offset: int = Query(0, description="Week offset from current week"),
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    building: Optional[str] = Query(None, description="Filter by building name"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)  # Allow all authenticated users
):
    try:
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=6)
        
        start_datetime = datetime.combine(start_of_week, datetime.min.time())
        end_datetime = datetime.combine(end_of_week, datetime.max.time())
        
        room_where = {}
        if room_type:
            room_where["type"] = room_type
        
        rooms = await prisma.salle.find_many(
            where=room_where,
            include={
                "emploiTemps": {
                    "where": {
                        "date": {
                            "gte": start_datetime,
                            "lte": end_datetime
                        }
                    },
                    "include": {
                        "matiere": True,
                        "enseignant": {
                            "include": {
                                "utilisateur": True
                            }
                        },
                        "groupe": True
                    }
                }
            },
            order={"code": "asc"}
        )
        
        time_slots = [
            {"id": "slot1", "start": "08:10", "end": "09:50"},
            {"id": "slot2", "start": "10:00", "end": "11:40"},
            {"id": "slot3", "start": "11:50", "end": "13:30"},
            {"id": "slot4", "start": "14:30", "end": "16:10"},
            {"id": "slot5", "start": "16:10", "end": "17:50"}
        ]
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        room_occupancy_data = []
        
        for room in rooms:
            occupancies = {}
            for day in days:
                occupancies[day] = {}
                for slot in time_slots:
                    occupancies[day][slot["id"]] = {"isOccupied": False}
            
            for schedule in room.emploiTemps:
                try:
                    # Use heure_debut for both date and time (it contains the full datetime)
                    schedule_datetime = schedule.heure_debut
                    day_index = schedule_datetime.weekday()
                    if day_index > 5:
                        continue
                    
                    day_name = days[day_index]
                    
                    # Get schedule start time (HH:MM format)
                    schedule_start = f"{schedule_datetime.hour:02d}:{schedule_datetime.minute:02d}"
                    
                    # Match schedule to time slot based on start time
                    time_slot = None
                    for slot in time_slots:
                        if schedule_start == slot["start"]:
                            time_slot = slot["id"]
                            break
                    
                    # If no exact match, find the slot that contains this time
                    if not time_slot:
                        schedule_minutes = schedule_datetime.hour * 60 + schedule_datetime.minute
                        for slot in time_slots:
                            slot_start_parts = slot["start"].split(":")
                            slot_start_minutes = int(slot_start_parts[0]) * 60 + int(slot_start_parts[1])
                            slot_end_parts = slot["end"].split(":")
                            slot_end_minutes = int(slot_end_parts[0]) * 60 + int(slot_end_parts[1])
                            
                            if slot_start_minutes <= schedule_minutes < slot_end_minutes:
                                time_slot = slot["id"]
                                break
                    
                    if time_slot:
                        teacher_name = "Non assigné"
                        if schedule.enseignant:
                            if schedule.enseignant.utilisateur:
                                teacher_name = f"{schedule.enseignant.utilisateur.prenom} {schedule.enseignant.utilisateur.nom}"
                            else:
                                teacher_name = f"{schedule.enseignant.prenom} {schedule.enseignant.nom}"
                        
                        occupancies[day_name][time_slot] = {
                            "isOccupied": True,
                            "course": {
                                "subject": schedule.matiere.nom if schedule.matiere else "Non spécifié",
                                "teacher": teacher_name,
                                "group": schedule.groupe.nom if schedule.groupe else "Non spécifié",
                                "status": schedule.status
                            }
                        }
                        logger.info(f"Assigned schedule to room {room.code}, {day_name} {time_slot}: {schedule.matiere.nom if schedule.matiere else 'N/A'}")
                    else:
                        logger.warning(f"Could not find time slot for schedule {schedule.id} at {schedule_start} in room {room.code}")
                except Exception as e:
                    logger.error(f"Error processing schedule {schedule.id}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue
            
            room_data = {
                "roomId": room.id,
                "roomName": room.code,
                "capacity": room.capacite,
                "type": room.type,
                "building": "Bâtiment Principal",
                "occupancies": occupancies
            }
            
            room_occupancy_data.append(room_data)
        
        return {
            "success": True,
            "data": room_occupancy_data,
            "week_info": {
                "start_date": start_of_week.isoformat(),
                "end_date": end_of_week.isoformat(),
                "week_offset": week_offset
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting room occupancy: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get room occupancy: {str(e)}"
        )


@router.get("/statistics")
async def get_occupancy_statistics(
    week_offset: int = Query(0, description="Week offset from current week"),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)  # Allow all authenticated users
):
    try:
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=6)
        
        start_datetime = datetime.combine(start_of_week, datetime.min.time())
        end_datetime = datetime.combine(end_of_week, datetime.max.time())
        
        total_rooms = await prisma.salle.count()
        
        occupied_slots = await prisma.emploitemps.count(
            where={
                "date": {
                    "gte": start_datetime,
                    "lte": end_datetime
                }
            }
        )
        
        total_possible_slots = total_rooms * 6 * 5
        available_slots = total_possible_slots - occupied_slots
        occupancy_rate = (occupied_slots / total_possible_slots * 100) if total_possible_slots > 0 else 0
        
        return {
            "success": True,
            "statistics": {
                "total_rooms": total_rooms,
                "total_slots": total_possible_slots,
                "occupied_slots": occupied_slots,
                "available_slots": available_slots,
                "occupancy_rate": round(occupancy_rate, 1)
            },
            "week_info": {
                "start_date": start_of_week.isoformat(),
                "end_date": end_of_week.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting occupancy statistics: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get occupancy statistics: {str(e)}"
        )
