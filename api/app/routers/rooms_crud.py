from fastapi import APIRouter, Depends, HTTPException, Query
from prisma import Prisma
from pydantic import BaseModel
from typing import Optional
import logging

from app.db.prisma_client import get_prisma
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/rooms", tags=["Rooms"])
logger = logging.getLogger(__name__)


class RoomCreate(BaseModel):
    code: str
    type: str
    capacity: int
    building: Optional[str] = None


class RoomUpdate(BaseModel):
    code: Optional[str] = None
    type: Optional[str] = None
    capacity: Optional[int] = None
    building: Optional[str] = None


@router.get("")
async def get_rooms(
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    building: Optional[str] = Query(None),
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get all rooms with optional filters"""
    try:
        where = {}
        
        if search:
            where["code"] = {"contains": search, "mode": "insensitive"}
        
        if type:
            where["type"] = type
        
        if building:
            where["building"] = building
        
        rooms = await prisma.salle.find_many(
            where=where,
            order={"code": "asc"}
        )
        
        return rooms
    except Exception as e:
        logger.error(f"Error fetching rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}")
async def get_room(
    room_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    """Get a single room by ID"""
    try:
        room = await prisma.salle.find_unique(
            where={"id": room_id}
        )
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_room(
    room_data: RoomCreate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN", "DEPARTMENT_HEAD"]))
):
    """Create a new room (Admin and Department Head only)"""
    try:
        # Check if room code already exists
        existing = await prisma.salle.find_first(
            where={"code": room_data.code}
        )
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Room with code '{room_data.code}' already exists")
        
        room = await prisma.salle.create(
            data={
                "code": room_data.code,
                "type": room_data.type,
                "capacity": room_data.capacity,
                "building": room_data.building
            }
        )
        
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{room_id}")
async def update_room(
    room_id: str,
    room_data: RoomUpdate,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN", "DEPARTMENT_HEAD"]))
):
    """Update a room (Admin and Department Head only)"""
    try:
        # Check if room exists
        existing = await prisma.salle.find_unique(
            where={"id": room_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Check if new code conflicts with another room
        if room_data.code and room_data.code != existing.code:
            code_conflict = await prisma.salle.find_first(
                where={
                    "code": room_data.code,
                    "id": {"not": room_id}
                }
            )
            
            if code_conflict:
                raise HTTPException(status_code=400, detail=f"Room with code '{room_data.code}' already exists")
        
        # Build update data (only include provided fields)
        update_data = {}
        if room_data.code is not None:
            update_data["code"] = room_data.code
        if room_data.type is not None:
            update_data["type"] = room_data.type
        if room_data.capacity is not None:
            update_data["capacity"] = room_data.capacity
        if room_data.building is not None:
            update_data["building"] = room_data.building
        
        room = await prisma.salle.update(
            where={"id": room_id},
            data=update_data
        )
        
        return room
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{room_id}")
async def delete_room(
    room_id: str,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_role(["ADMIN"]))
):
    """Delete a room (Admin only)"""
    try:
        # Check if room exists
        existing = await prisma.salle.find_unique(
            where={"id": room_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Check if room is being used in schedules
        schedules_count = await prisma.emploitemps.count(
            where={"id_salle": room_id}
        )
        
        if schedules_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete room. It is used in {schedules_count} schedule(s)"
            )
        
        await prisma.salle.delete(
            where={"id": room_id}
        )
        
        return {"success": True, "message": "Room deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
