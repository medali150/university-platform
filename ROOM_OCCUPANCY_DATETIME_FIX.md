# Room Occupancy DateTime Serialization Fix

## Date: 2025-10-07

## Issue
```
Error getting room occupancy: Type <class 'datetime.date'> not serializable
INFO: 127.0.0.1:51581 - "GET /room-occupancy/rooms?week_offset=0 HTTP/1.1" 500 Internal Server Error
```

Frontend displayed:
```
{"detail": "Erreur lors de la récupération de l'occupation des salles : Type <class 'datetime.date'> not serializable"}
```

## Root Cause

When FastAPI tries to return Python objects as JSON responses, it uses `json.dumps()` which cannot serialize Python datetime objects (datetime.date, datetime.datetime, datetime.time). 

The room occupancy API was returning Prisma model objects directly, which contained:
- `schedule.date` - datetime.date object
- `schedule.heure_debut` - datetime.time object
- Other potential datetime fields from the database

Python's built-in `json.dumps()` doesn't know how to convert these to JSON strings, resulting in the serialization error.

## Solution

FastAPI provides `jsonable_encoder()` which automatically converts Python objects (including datetime, UUID, Decimal, etc.) to JSON-compatible types. We wrapped all API responses with `JSONResponse(content=jsonable_encoder(response_data))`.

### Changes Made to `api/app/routers/room_occupancy.py`:

#### 1. Added Imports
```python
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
```

#### 2. Updated `/rooms` endpoint return
**Before:**
```python
return {
    "success": True,
    "data": room_occupancy_data,
    "week_info": {
        "start_date": monday.strftime("%Y-%m-%d"),
        "end_date": sunday.strftime("%Y-%m-%d"),
        "week_offset": week_offset
    }
}
```

**After:**
```python
response_data = {
    "success": True,
    "data": room_occupancy_data,
    "week_info": {
        "start_date": monday.strftime("%Y-%m-%d"),
        "end_date": sunday.strftime("%Y-%m-%d"),
        "week_offset": week_offset
    }
}

# Use jsonable_encoder to handle datetime serialization
return JSONResponse(content=jsonable_encoder(response_data))
```

#### 3. Updated `/rooms/{room_id}/details` endpoint
```python
response_data = {
    "success": True,
    "room": {
        "id": room.id,
        "name": room.code,
        "capacity": room.capacite or 30,
        "type": room.type,
        "equipment": ["Projecteur", "Tableau", "WiFi"],
        "building": "Bâtiment Principal",
        "description": f"Salle {room.code} - Capacité {room.capacite} personnes"
    }
}

return JSONResponse(content=jsonable_encoder(response_data))
```

#### 4. Updated `/statistics` endpoint
```python
response_data = {
    "success": True,
    "statistics": {
        "total_rooms": total_rooms,
        "total_slots": total_possible_slots,
        "occupied_slots": occupied_slots,
        "available_slots": available_slots,
        "occupancy_rate": round(occupancy_rate, 1)
    }
}

return JSONResponse(content=jsonable_encoder(response_data))
```

#### 5. Enhanced Error Handling in Schedule Processing
Added try-catch around schedule processing to handle both datetime.date and datetime.datetime objects:

```python
for schedule in room.emploitemps:
    try:
        # Handle both datetime.date and datetime.datetime objects
        schedule_date = schedule.date
        if hasattr(schedule_date, 'date'):
            schedule_date = schedule_date.date()
        
        day_index = schedule_date.weekday()
        
        # Handle both time and datetime objects
        start_time = schedule.heure_debut
        if hasattr(start_time, 'time'):
            start_time = start_time.time()
        
        # ... rest of processing
    except Exception as e:
        logger.warning(f"Error processing schedule {schedule.id}: {str(e)}")
        continue
```

#### 6. Improved Error Logging
```python
except Exception as e:
    import traceback
    logger.error(f"Error getting room occupancy: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise HTTPException(...)
```

## How jsonable_encoder() Works

`jsonable_encoder()` from FastAPI automatically converts:
- `datetime.datetime` → ISO format string (e.g., "2025-10-07T14:30:00")
- `datetime.date` → ISO format string (e.g., "2025-10-07")
- `datetime.time` → ISO format string (e.g., "14:30:00")
- `UUID` → string
- `Decimal` → float
- Pydantic models → dict
- Enums → their value
- bytes → base64 string
- Sets → lists

## Testing

### 1. Debug Endpoint (No Auth Required)
```bash
curl http://localhost:8000/room-occupancy/debug/rooms
```
Expected: Returns mock data with success=true

### 2. Authenticated Endpoint
```bash
# Login first
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Use token
curl http://localhost:8000/room-occupancy/rooms?week_offset=0 \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Expected: Returns room occupancy data with success=true

### 3. Frontend Test
1. Login to the application
2. Navigate to `/dashboard/department-head/room-occupancy`
3. Page should load without errors
4. Room occupancy grid should display
5. Statistics cards should show correct numbers

## Benefits of This Fix

### 1. **Automatic Serialization**
- No need to manually convert datetime objects to strings
- Handles all Python types automatically
- Future-proof for new field types

### 2. **Consistent Response Format**
- All endpoints use the same serialization method
- Standardized datetime format (ISO 8601)
- Frontend can reliably parse dates

### 3. **Better Error Handling**
- Individual schedule processing errors don't crash the entire request
- Detailed logging with tracebacks
- Graceful degradation

### 4. **Maintainability**
- Single pattern applied to all endpoints
- Easy to add new endpoints
- Less boilerplate code

## Alternative Approaches (Not Used)

### 1. Manual String Conversion
```python
# Not used - too verbose
"date": schedule.date.strftime("%Y-%m-%d") if schedule.date else None
```
**Drawback**: Need to convert every datetime field manually

### 2. Custom JSONEncoder
```python
# Not used - requires more setup
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)
```
**Drawback**: FastAPI already provides `jsonable_encoder()`

### 3. Pydantic Response Models
```python
# Not used - more overhead
class RoomOccupancyResponse(BaseModel):
    success: bool
    data: List[RoomData]
    week_info: WeekInfo
```
**Drawback**: Need to define schemas for every response

## Related Files

- `api/app/routers/room_occupancy.py` - Main fix applied here
- `frontend/lib/api.ts` - API client methods
- `frontend/app/dashboard/department-head/room-occupancy/page.tsx` - Frontend consuming the API

## Verification Steps

After the fix:
1. ✅ Backend server starts without errors
2. ✅ Debug endpoint returns valid JSON
3. ✅ Authenticated endpoints work with proper token
4. ✅ Frontend page loads without errors
5. ✅ Room occupancy grid displays correctly
6. ✅ Date filtering works (week navigation)
7. ✅ No serialization errors in logs

## Future Improvements

1. **Database Schema Enhancement**
   - Add `building` field to `salle` table
   - Add `equipment` JSON field for room equipment list
   - Store actual building information

2. **Response Caching**
   ```python
   from fastapi_cache import Cache
   from fastapi_cache.decorator import cache
   
   @router.get("/rooms")
   @cache(expire=300)  # Cache for 5 minutes
   async def get_rooms_occupancy(...):
   ```

3. **Pagination for Large Datasets**
   ```python
   @router.get("/rooms")
   async def get_rooms_occupancy(
       page: int = Query(1, ge=1),
       page_size: int = Query(50, ge=1, le=100)
   ):
   ```

4. **WebSocket for Real-Time Updates**
   ```python
   @router.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket):
       # Send real-time room occupancy updates
   ```

## Conclusion

The room occupancy API now properly handles datetime serialization using FastAPI's `jsonable_encoder()`. The fix is:
- ✅ Simple and clean
- ✅ Follows FastAPI best practices
- ✅ Handles all Python types automatically
- ✅ Easy to maintain and extend

The integration between frontend and backend now works correctly with proper datetime handling.
