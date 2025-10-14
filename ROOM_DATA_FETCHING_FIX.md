# Room Data Fetching Fix - Complete Documentation

## Issues Identified

### 1. Room Dropdown Showing Checkmarks Instead of Names
**Problem**: The room selector in the schedule creator was showing checkmarks (✓) but no room names.

**Root Cause**: 
- The `Salle` database model uses `code` field for room names
- Frontend code was trying to access `nom` or `name` fields which don't exist
- This caused undefined/null values to be displayed

**Database Schema**:
```prisma
model Salle {
  id          String        @id @default(cuid())
  code        String        @unique   // ← This is the room name!
  type        RoomType
  capacite    Int
  createdAt   DateTime      @default(now())
  updatedAt   DateTime      @updatedAt
  
  emploiTemps EmploiTemps[]
  @@map("Room")
}
```

### 2. Room Occupancy API Serialization Error
**Problem**: `/room-occupancy/rooms` endpoint returned 500 error with message:
```
Type <class 'datetime.date'> not serializable
```

**Root Cause**: 
- The endpoint was using `.isoformat()` on date objects
- Some date objects needed `.strftime()` for proper serialization

## Fixes Applied

### Fix 1: Update Frontend to Use `code` Field

**File**: `frontend/components/department-head/schedule-creator.tsx`

**Before**:
```typescript
availableRooms.map(room => (
  <SelectItem key={room.id} value={room.nom || room.name}>
    {room.nom || room.name}
  </SelectItem>
))
```

**After**:
```typescript
availableRooms.map(room => (
  <SelectItem key={room.id} value={room.code}>
    {room.code} ({room.type}) - {room.capacite} places
  </SelectItem>
))
```

**Benefits**:
- Shows room code (A101, AMPHA, LI1, etc.)
- Shows room type (LECTURE, LAB, OTHER)
- Shows capacity (30 places, 40 places, etc.)
- More informative selection

### Fix 2: Update Room Occupancy API

**File**: `api/app/routers/room_occupancy.py`

**Changes Made**:

1. **Fixed room name field** (line ~117):
```python
# Before
"roomName": room.nom,

# After
"roomName": room.code,
```

2. **Fixed room details endpoint** (line ~161):
```python
# Before
"name": room.nom,
"type": room.type or "Salle",

# After
"name": room.code,
"type": room.type,
```

3. **Fixed date serialization** (line ~125):
```python
# Before
"start_date": monday.isoformat(),
"end_date": sunday.isoformat(),

# After
"start_date": monday.strftime("%Y-%m-%d"),
"end_date": sunday.strftime("%Y-%m-%d"),
```

## Room Data in Database

The database has **19 rooms** created by `populate_database_complete.py`:

### Amphithéâtres (2)
- AMPHA - 200 places (LECTURE)
- AMPHB - 150 places (LECTURE)

### Salles de cours (9)
- A101 - 40 places (LECTURE)
- A102 - 35 places (LECTURE)
- A103 - 40 places (LECTURE)
- A201 - 45 places (LECTURE)
- A202 - 40 places (LECTURE)
- B101 - 35 places (LECTURE)
- B102 - 40 places (LECTURE)
- B201 - 35 places (LECTURE)

### Laboratoires Informatique (4)
- LI1 - 30 places (LAB)
- LI2 - 25 places (LAB)
- LI3 - 30 places (LAB)
- LI4 - 28 places (LAB)

### Laboratoires Spécialisés (3)
- LM1 - 20 places (LAB) - Mécanique
- LE1 - 25 places (LAB) - Électrique
- LA1 - 20 places (LAB) - Autre

### Ateliers (2)
- AM1 - 25 places (OTHER) - Atelier Mécanique
- AE1 - 20 places (OTHER) - Atelier Électrique

## API Endpoints

### 1. Get Rooms for Schedule Creation
```
GET /department-head/timetable/rooms
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "id": "cmgfpq...",
    "code": "A101",
    "type": "LECTURE",
    "capacite": 40,
    "createdAt": "2025-10-07T...",
    "updatedAt": "2025-10-07T..."
  },
  ...
]
```

**Status**: ✅ Working (tested successfully)

### 2. Get Room Occupancy
```
GET /room-occupancy/rooms?week_offset=0
Authorization: Bearer <token>
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "roomId": "cmgfpq...",
      "roomName": "A101",
      "capacity": 40,
      "type": "LECTURE",
      "building": "Bâtiment Principal",
      "occupancies": {
        "lundi": {
          "slot1": {"isOccupied": false, "course": null},
          "slot2": {"isOccupied": true, "course": {...}},
          ...
        },
        ...
      }
    }
  ],
  "week_info": {
    "start_date": "2025-10-07",
    "end_date": "2025-10-13",
    "week_offset": 0
  }
}
```

**Status**: ✅ Fixed (serialization error resolved)

## Testing

### Test Script Results
```
✅ Logged in successfully

1. Testing /department-head/timetable/rooms
   Status: 200
   ✅ Found 19 rooms
      - A101 (LECTURE) - 40 places
      - A102 (LECTURE) - 35 places
      - A103 (LECTURE) - 40 places
      - A201 (LECTURE) - 45 places
      - A202 (LECTURE) - 40 places

2. Testing /room-occupancy/rooms
   Status: 200 (after fix)
   ✅ Room occupancy data retrieved successfully
```

## Frontend Display

### Before Fix
```
Salle *
[Sélectionner une salle ▼]
  ✓
  ✓
  ✓
  ✓
  ...
```

### After Fix
```
Salle *
[Sélectionner une salle ▼]
  AMPHA (LECTURE) - 200 places
  AMPHB (LECTURE) - 150 places
  A101 (LECTURE) - 40 places
  A102 (LECTURE) - 35 places
  A201 (LECTURE) - 45 places
  LI1 (LAB) - 30 places
  LI2 (LAB) - 25 places
  ...
```

## Room Types (RoomType Enum)

```prisma
enum RoomType {
  LECTURE  // Amphithéâtre ou salle de cours
  LAB      // Laboratoire
  OTHER    // Atelier ou autre
}
```

## Common Issues & Solutions

### Issue: "Aucune salle disponible"
**Cause**: No rooms in database or authentication failed
**Solution**: 
1. Check if backend is running
2. Verify authentication token is valid
3. Run `populate_database_complete.py` if database is empty

### Issue: Room names not displaying
**Cause**: Using wrong field name (nom/name instead of code)
**Solution**: Always use `room.code` to access room name

### Issue: "Token d'authentification manquant"
**Cause**: User not logged in or token expired
**Solution**:
1. Check localStorage has 'authToken' key
2. Try logging out and logging back in
3. Verify backend auth middleware is working

## Files Modified

1. ✅ `api/app/routers/room_occupancy.py`
   - Changed `room.nom` → `room.code`
   - Fixed date serialization
   - Updated room details endpoint

2. ✅ `frontend/components/department-head/schedule-creator.tsx`
   - Changed `room.nom || room.name` → `room.code`
   - Enhanced display to show type and capacity
   - Added better placeholders

## Verification Checklist

- [x] Rooms fetch from API successfully
- [x] Room dropdown shows all 19 rooms
- [x] Room names display correctly (codes like A101, AMPHA, etc.)
- [x] Room type and capacity shown in dropdown
- [x] Room occupancy endpoint returns 200
- [x] No serialization errors
- [x] Authentication works correctly

## Next Steps

### Recommended Enhancements

1. **Add Room Filtering**:
   - Filter by type (LECTURE, LAB, OTHER)
   - Filter by capacity
   - Search by room code

2. **Add Room Details View**:
   - Click room to see full schedule
   - Show room equipment
   - Show availability percentage

3. **Add Room Validation**:
   - Check if room is available before booking
   - Warn about conflicts
   - Suggest alternative rooms

4. **Add Room Management**:
   - CRUD operations for rooms
   - Update room details
   - Mark rooms as unavailable/maintenance

---

**Status**: ✅ Complete
**Date**: 2025-10-07
**Impact**: Critical - Enables room selection in schedule creation
