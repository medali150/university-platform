# 🔧 Notification System Fix - Server Restart Required

## Problem
The Prisma client was regenerated with the Notification model, but the running server still has the old client loaded in memory.

## Solution: Restart the Backend Server

### Option 1: Use the Restart Script (Easiest)
```bash
cd api
.\restart_server.bat
```

### Option 2: Manual Restart
1. **Find the terminal** running the backend server (look for "uvicorn" or "INFO: Application startup complete")
2. **Press Ctrl+C** to stop it
3. **Restart it**:
   ```bash
   cd api
   python main.py
   ```

### Option 3: Kill and Restart
```powershell
# Stop all Python processes
taskkill /F /IM python.exe

# Wait 2 seconds
timeout /t 2

# Start server
cd api
python main.py
```

## Verification

After restarting, you should see these logs:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Then the notification endpoints should work:
- GET `/notifications/` - ✅ Should return 200
- GET `/notifications/stats` - ✅ Should return 200

## What Was Fixed

### ✅ Backend
1. **Prisma Schema**: Notification model with proper relations
   - Table name: `notifications` (lowercase, plural)
   - Relation: `Utilisateur` ↔ `Notification` (one-to-many)
2. **Migrations Applied**:
   - `20251008095928_add_notification` - Initial
   - `20251008102944_fix_notification_table_name` - Table name fix
3. **Prisma Client**: Regenerated with `prisma generate`
4. **Notification Router**: Already registered in `main.py`
5. **Notification Creation**: Integrated in `department_head_timetable.py`

### ✅ Frontend
1. **API Client**: 6 notification methods in `lib/api.ts`
2. **Notifications Page**: Complete UI at `/dashboard/notifications`
3. **Bell Badge**: Shows unread count in navbar
4. **Auto-refresh**: Polls every 30 seconds

## Status Check

Run this to verify Prisma has the notification model:
```bash
cd api
python check_prisma_models.py
```

Expected output:
```
✅ notification model EXISTS
```

## After Server Restart

The notification system will be fully functional:
- Department heads create schedules → Notifications sent to teachers & students
- Bell badge shows unread count
- Notifications page shows all notifications
- Users can mark as read, delete, etc.

---

**Next Step**: Restart the server using one of the options above! 🚀
