# Room Occupancy Feature - Complete Rebuild

## ✅ Feature Successfully Rebuilt from Scratch

### Overview
The Room Occupancy feature allows department heads and administrators to visualize room availability and schedules across different time slots and days of the week.

---

## 🏗️ Architecture

### Backend (FastAPI + Prisma)
**File**: `api/app/routers/room_occupancy.py`

#### Endpoints

1. **GET `/room-occupancy/rooms`**
   - Get room occupancy for a specific week
   - **Query Parameters**:
     - `week_offset` (int): Week offset from current (0=current, 1=next, -1=previous)
     - `room_type` (optional): Filter by type (LECTURE, LAB, EXAM, OTHER)
     - `building` (optional): Filter by building name
   - **Response**: List of rooms with occupancy grid

2. **GET `/room-occupancy/rooms/{room_id}/details`**
   - Get detailed information about a specific room
   - **Query Parameters**:
     - `week_offset` (int): Week offset
   - **Response**: Room details with all schedules

3. **GET `/room-occupancy/statistics`**
   - Get occupancy statistics for a week
   - **Query Parameters**:
     - `week_offset` (int): Week offset
   - **Response**: Statistics (total rooms, occupied slots, occupancy rate, etc.)

---

### Frontend (Next.js 14 + React + TypeScript)
**File**: `frontend/app/dashboard/department-head/room-occupancy/page.tsx`

#### Features
- 📅 **Week Navigation**: Previous/Next week, Jump to current week
- 🔍 **Search**: Filter rooms by name
- 🏷️ **Type Filter**: Filter by room type (Lecture, Lab, Exam, Other)
- 📊 **Statistics Cards**: Display room occupancy metrics
- 🎨 **Color-Coded Grid**: 
  - 🟢 Green: Available
  - 🔵 Blue: Occupied (Planned)
  - 🔴 Red: Canceled
  - 🟡 Yellow: Makeup class
- 📱 **Responsive Design**: Works on all screen sizes

---

## 🗄️ Database Schema

### Tables Used

#### `Salle` (Room)
```prisma
model Salle {
  id          String        @id @default(cuid())
  code        String        @unique
  type        RoomType      // LECTURE, LAB, EXAM, OTHER
  capacite    Int
  emploiTemps EmploiTemps[]
}
```

#### `EmploiTemps` (Schedule)
```prisma
model EmploiTemps {
  id            String         @id @default(cuid())
  date          DateTime
  heure_debut   DateTime
  heure_fin     DateTime
  id_salle      String
  id_matiere    String
  id_groupe     String
  id_enseignant String
  status        ScheduleStatus // PLANNED, CANCELED, MAKEUP
  
  salle         Salle         @relation(...)
  matiere       Matiere       @relation(...)
  groupe        Groupe        @relation(...)
  enseignant    Enseignant    @relation(...)
}
```

---

## 🔧 Technical Implementation

### Key Features

#### 1. Datetime Handling (CRITICAL FIX)
**Problem Solved**: Prisma query builder cannot serialize Python `datetime.date` objects

**Solution**: Convert dates to ISO strings BEFORE passing to Prisma:

```python
# ✅ CORRECT - Convert to ISO string first
start_datetime = datetime.combine(start_of_week, datetime.min.time())
end_datetime = datetime.combine(end_of_week, datetime.max.time())

start_str = start_datetime.isoformat()  # "2025-10-06T00:00:00"
end_str = end_datetime.isoformat()      # "2025-10-12T23:59:59.999999"

# Now pass strings to Prisma
rooms = await prisma.salle.find_many(
    include={
        "emploiTemps": {
            "where": {
                "date": {
                    "gte": start_str,  # ✅ String works
                    "lte": end_str     # ✅ String works
                }
            }
        }
    }
)
```

#### 2. Time Slot Mapping
The system maps database times to fixed time slots:

```python
TIME_SLOTS = {
    "slot1": {"start": "08:10", "end": "09:50"},
    "slot2": {"start": "10:00", "end": "11:40"},
    "slot3": {"start": "11:50", "end": "13:30"},
    "slot4": {"start": "14:30", "end": "16:10"},
    "slot5": {"start": "16:10", "end": "17:50"}
}
```

#### 3. Occupancy Grid Structure
```typescript
{
  roomId: string
  roomName: string
  capacity: number
  type: string
  building: string
  occupancies: {
    Monday: {
      slot1: { isOccupied: boolean, course?: {...} },
      slot2: { isOccupied: boolean, course?: {...} },
      // ... more slots
    },
    Tuesday: { ... },
    // ... more days
  }
}
```

---

## 📊 Statistics Calculation

```python
# Total possible slots = rooms × days × slots_per_day
total_possible_slots = total_rooms * 6 * 5  # 6 days, 5 slots

# Occupancy rate
occupancy_rate = (occupied_slots / total_possible_slots * 100)
```

---

## 🎨 UI Components Used

- **Card**: Room containers and statistics
- **Badge**: Room type, schedule status
- **Button**: Week navigation
- **Input**: Search functionality
- **Select**: Type filter dropdown
- **Icons**: lucide-react (ChevronLeft, ChevronRight, Search, Building, Users)

---

## 🔐 Security

- **Authentication Required**: All endpoints require authentication
- **Role-Based Access**: Only `DEPARTMENT_HEAD` and `ADMIN` roles can access
- **Authorization Check**: `Depends(require_role(["DEPARTMENT_HEAD", "ADMIN"]))`

---

## 🚀 Testing Instructions

### Backend Testing

```bash
# Get current week occupancy
curl http://localhost:8000/room-occupancy/rooms?week_offset=0 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get next week with filter
curl "http://localhost:8000/room-occupancy/rooms?week_offset=1&room_type=LAB" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl http://localhost:8000/room-occupancy/statistics?week_offset=0 \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get room details
curl http://localhost:8000/room-occupancy/rooms/ROOM_ID/details?week_offset=0 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend Testing

1. Navigate to: `http://localhost:3000/dashboard/department-head/room-occupancy`
2. Login as a department head or admin user
3. Test features:
   - ✅ Week navigation (Previous/Next buttons)
   - ✅ Search for specific room
   - ✅ Filter by room type
   - ✅ View statistics cards
   - ✅ See color-coded occupancy grid
   - ✅ View course details in occupied slots

---

## 📁 Files Modified/Created

### Backend
- ✅ `api/app/routers/room_occupancy.py` - Complete rewrite
  - Proper datetime handling
  - Clean code structure
  - Comprehensive error handling
  - Detailed logging

### Frontend
- ✅ `frontend/app/dashboard/department-head/room-occupancy/page.tsx` - Complete rebuild
  - Modern React hooks
  - TypeScript interfaces
  - Responsive design
  - Beautiful UI with ShadCN components

### API Client
- ✅ `frontend/lib/api.ts` - Methods already exist:
  - `getRoomOccupancy()`
  - `getRoomDetails()`
  - `getRoomOccupancyStatistics()`

---

## 🐛 Common Issues & Solutions

### Issue 1: Datetime Serialization Error
**Error**: `Type <class 'datetime.date'> not serializable`

**Solution**: Always convert datetime objects to ISO strings before Prisma queries
```python
date_str = date_obj.isoformat()
```

### Issue 2: Missing Teacher Data
**Solution**: Safe navigation with null checks
```python
teacher_name = "Non assigné"
if schedule.enseignant:
    if schedule.enseignant.utilisateur:
        teacher_name = f"{schedule.enseignant.utilisateur.prenom} {schedule.enseignant.utilisateur.nom}"
    else:
        teacher_name = f"{schedule.enseignant.prenom} {schedule.enseignant.nom}"
```

### Issue 3: Empty Response
**Check**:
- Are there rooms in the database?
- Are there schedules for the selected week?
- Is the date range calculated correctly?

---

## 🎯 Future Enhancements

1. **Room Reservation**: Add ability to reserve rooms
2. **Building Filter**: Add actual building data to database
3. **Export**: Export occupancy to PDF/Excel
4. **Conflict Detection**: Highlight scheduling conflicts
5. **Equipment Info**: Add room equipment details
6. **Real-time Updates**: WebSocket for live updates
7. **Mobile App**: Native mobile version

---

## 📚 Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prisma Python Client](https://prisma-client-py.readthedocs.io/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [ShadCN UI Components](https://ui.shadcn.com/)

---

## ✅ Status: READY FOR TESTING

The Room Occupancy feature has been completely rebuilt from scratch with:
- ✅ Clean, maintainable code
- ✅ Proper error handling
- ✅ Type safety (TypeScript)
- ✅ Responsive UI
- ✅ Fixed datetime serialization issues
- ✅ Comprehensive logging
- ✅ Security (authentication & authorization)

**Test the feature now at**: `http://localhost:3000/dashboard/department-head/room-occupancy`

---

## 📞 Support

If you encounter any issues:
1. Check backend logs in uvicorn terminal
2. Check browser console (F12) for frontend errors
3. Verify authentication token is valid
4. Ensure database has room and schedule data
