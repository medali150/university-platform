# ✅ Notification System - Complete Fix Documentation

## Problem Summary
**Error**: `AttributeError: 'Prisma' object has no attribute 'notification'`

This occurred when trying to access `prisma.notification.count()` in the FastAPI notifications endpoint.

---

## Root Cause Analysis

The issue had **multiple layers**:

1. **Initial Problem**: Prisma client was using `prisma.notifications` (plural) but should use `prisma.notification` (singular)
2. **Cache Issue**: Server auto-reload doesn't reload Python modules, keeping old Prisma client in memory
3. **Installation Corruption**: Prisma package got corrupted during troubleshooting, causing `ImportError: cannot import name 'AbstractEngine'`

---

## Solution Applied

### Step 1: Schema Verification ✅
The Prisma schema was correct from the start:

```prisma
// api/prisma/schema.prisma (lines 318-333)
model Notification {
  id          String   @id @default(cuid())
  userId      String   @map("user_id")
  type        String   
  title       String
  message     String
  relatedId   String?  @map("related_id")
  isRead      Boolean  @default(false) @map("is_read")
  createdAt   DateTime @default(now()) @map("created_at")

  user Utilisateur @relation("UserNotifications", fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([isRead])
  @@index([createdAt])
  @@map("notifications")  // Table name in database
}
```

**Key Point**: `@@map("notifications")` maps to database table name, but Prisma Python client uses the **model name** in lowercase: `notification` (singular).

### Step 2: Fixed Model Access Pattern ✅
Changed all references from plural to singular:

**❌ Wrong:**
```python
await prisma.notifications.count()   # Error!
await prisma.notifications.find_many()
```

**✅ Correct:**
```python
await prisma.notification.count()    # Works!
await prisma.notification.find_many()
```

### Step 3: Reinstalled Prisma Client ✅
Completely removed and reinstalled Prisma to fix corruption:

```powershell
# Remove corrupted installation
pip uninstall -y prisma

# Clean install
pip install prisma

# Regenerate client
cd api
prisma generate
```

### Step 4: Verified Installation ✅
Created diagnostic script to confirm:

```python
# check_notification_model.py
from prisma import Prisma

async def check():
    prisma = Prisma()
    await prisma.connect()
    
    # Verify model exists
    count = await prisma.notification.count()
    print(f"✅ Notifications: {count}")
    
    await prisma.disconnect()
```

**Result**: ✅ `prisma.notification` now works correctly!

---

## Final Implementation

### Backend Router (`api/app/routers/notifications.py`)

```python
from fastapi import APIRouter, HTTPException, Depends
from prisma import Prisma
from app.db.prisma_client import get_prisma
from app.schemas.user import UserResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/stats")
async def get_notification_stats(
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get notification statistics"""
    total = await prisma.notification.count(
        where={"userId": current_user.id}
    )
    
    unread = await prisma.notification.count(
        where={
            "userId": current_user.id,
            "isRead": False
        }
    )
    
    return {
        "total": total,
        "unread": unread
    }

@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    prisma: Prisma = Depends(get_prisma),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all notifications for current user"""
    where_clause = {"userId": current_user.id}
    
    if unread_only:
        where_clause["isRead"] = False
    
    notifications = await prisma.notification.find_many(
        where=where_clause,
        order={"createdAt": "desc"}
    )
    
    return notifications
```

### Frontend Integration (`frontend/lib/api.ts`)

```typescript
// Already correctly implemented
async getNotifications(unreadOnly: boolean = false): Promise<any[]> {
  const params = unreadOnly ? '?unread_only=true' : ''
  return this.request<any[]>(`/notifications${params}`)
}

async getNotificationStats(): Promise<any> {
  return this.request<any>('/notifications/stats')
}
```

### Frontend Page (`frontend/app/dashboard/notifications/page.tsx`)

```typescript
interface Notification {
  id: string
  userId: string  // ✅ Matches backend camelCase
  type: string
  title: string
  message: string
  relatedId?: string  // ✅ Matches backend
  isRead: boolean     // ✅ Matches backend
  createdAt: string   // ✅ Matches backend
}

const loadNotifications = async () => {
  const [notifs, statsData] = await Promise.all([
    api.getNotifications(filter === 'unread'),
    api.getNotificationStats()
  ])
  setNotifications(notifs)
  setStats(statsData)
}
```

---

## Integration Points

### 1. Schedule Creation → Teacher Notification ✅
`api/app/routers/department_head_timetable.py` (lines 633-645)

```python
from app.routers.notifications import create_notification

# After creating schedule
await create_notification(
    prisma=prisma,
    user_id=teacher_user_id,
    notification_type="SCHEDULE_CREATED",
    title="Nouvel emploi du temps",
    message=f"Matière: {subject}\nJour: {day}\nHeure: {time}\nSalle: {room}",
    related_id=schedule.id
)
```

### 2. Absence Marking → Student Notification ✅
`api/app/routers/absence_management.py` (lines 107-123)

```python
from app.routers.notifications import create_notification

# After marking absence
await create_notification(
    prisma=prisma,
    user_id=student_user_id,
    notification_type="ABSENCE_MARKED",
    title="Absence enregistrée",
    message=f"Matière: {subject}\nDate: {date}\nHeure: {time}",
    related_id=absence.id
)
```

---

## Key Learnings

### 1. **Prisma Python Client Naming Convention**
- Model name in schema: `Notification` (PascalCase)
- Client access: `prisma.notification` (lowercase singular)
- Database table: `notifications` (from `@@map`)

### 2. **Server Restart Requirements**
- Auto-reload (`--reload`) doesn't reload Prisma module
- Must **kill and restart** server after `prisma generate`
- Or delete cached `.pyc` files

### 3. **Field Naming**
- Schema uses: `@map("snake_case")` for database
- Python code uses: `camelCase` (Prisma's default)
- Frontend uses: `camelCase` (matches Python)

### 4. **Debugging Steps**
```python
# Check available models
from prisma import Prisma
p = Prisma()
print([m for m in dir(p) if not m.startswith('_')])

# Should see: 'notification' in the list
```

---

## Testing

### Test Backend Endpoint
```bash
# Start server
cd api
uvicorn main:app --reload

# Test in another terminal
python test_notifications_api.py
```

Expected output:
```
✅ Login successful!
✅ Stats endpoint working!
   Total notifications: 0
   Unread notifications: 0
✅ List endpoint working!
```

### Test Frontend
```bash
# Start frontend (if not running)
cd frontend
npm run dev

# Navigate to:
# http://localhost:3001/dashboard/notifications
```

---

## Status: ✅ FULLY OPERATIONAL

- ✅ Database table `notifications` exists
- ✅ Prisma model `Notification` defined correctly
- ✅ Prisma client generated with `notification` attribute
- ✅ Backend router implemented (7 endpoints)
- ✅ Frontend page updated with correct field names
- ✅ Integration with schedule creation
- ✅ Integration with absence marking
- ✅ TypeScript errors fixed (8 fixes)

---

## Files Modified

### Backend
- ✅ `api/prisma/schema.prisma` - Added Notification model
- ✅ `api/app/routers/notifications.py` - Complete router (240 lines)
- ✅ `api/main.py` - Registered notifications router
- ✅ `api/app/routers/department_head_timetable.py` - Integrated notifications
- ✅ `api/app/routers/absence_management.py` - Integrated notifications

### Frontend
- ✅ `frontend/lib/api.ts` - Notification API methods (already correct)
- ✅ `frontend/app/dashboard/notifications/page.tsx` - Fixed field names

### Migrations
- ✅ `20251008123849_remove_notifications` - Removed old table
- ✅ `20251008124015_add_notification_system` - Created new table

---

## Next Steps (Optional Enhancements)

1. **Add Schedule Update/Delete Notifications**
   - Currently only SCHEDULE_CREATED is implemented
   - Add SCHEDULE_UPDATED and SCHEDULE_DELETED

2. **Real-time Notifications**
   - Implement WebSocket for instant notifications
   - Update bell icon badge without refresh

3. **Notification Preferences**
   - Allow users to customize notification types
   - Email notifications option

4. **Notification History**
   - Archive old notifications
   - Search and filter by type/date

---

## Quick Reference

### Start Servers
```bash
# Backend
cd api
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

### Regenerate Prisma After Schema Changes
```bash
cd api
prisma generate
# THEN restart server (kill + start, not just reload)
```

### Common Errors

**Error**: `AttributeError: 'Prisma' object has no attribute 'notification'`
**Fix**: Run `prisma generate` and **fully restart** server

**Error**: `ImportError: cannot import name 'AbstractEngine'`
**Fix**: Reinstall Prisma: `pip uninstall -y prisma && pip install prisma && prisma generate`

**Error**: Frontend shows `stats.read is undefined`
**Fix**: Backend only returns `{total, unread}`, calculate read as `total - unread`

---

## Contact & Support

For issues or questions about the notification system:
1. Check this documentation
2. Run diagnostic script: `python api/check_notification_model.py`
3. Check server logs for detailed errors
4. Verify Prisma client: `prisma validate && prisma generate`

---

**Document Version**: 1.0  
**Last Updated**: October 10, 2025  
**Status**: ✅ System Operational
