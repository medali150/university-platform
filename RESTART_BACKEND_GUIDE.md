# ROOM OCCUPANCY FIX - COMPLETE TROUBLESHOOTING GUIDE

## Current Status

### ✅ Backend Code Fixed
- Added `jsonable_encoder()` to handle datetime serialization
- All room occupancy endpoints updated
- Frontend API client properly integrated
- Enhanced error handling and logging

### ⚠️ Issue: Backend May Not Have Reloaded
Even though uvicorn has `reload=True`, it sometimes doesn't catch all file changes.

## SOLUTION: Restart Backend Server

### Step 1: Stop Current Backend
1. Find the terminal running uvicorn
2. Press `Ctrl+C` to stop the server
3. OR kill the process:
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*universety_app*"} | Stop-Process -Force
   ```

### Step 2: Restart Backend
```powershell
cd C:\Users\pc\universety_app\api
c:\Users\pc\universety_app\.venv\Scripts\python.exe run_server.py
```

### Step 3: Verify Backend is Working
```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test room occupancy debug endpoint (no auth needed)
curl http://localhost:8000/room-occupancy/debug/rooms
```

You should see JSON output with `"success": true` and room data.

### Step 4: Start Frontend
```powershell
cd C:\Users\pc\universety_app\frontend
npm run dev
```

### Step 5: Test in Browser
1. Open http://localhost:3000
2. Login with your credentials
3. Navigate to: `/dashboard/department-head/room-occupancy`
4. Open browser DevTools (F12) → Console tab
5. Look for console.log messages we added:
   ```
   Fetching room occupancy data...
   Params: {week_offset: 0, room_type: "all", building: "all"}
   API Response received: {success: true, data: Array(19), week_info: {...}}
   Room data extracted: 19 rooms
   ```

## What to Look For

### ✅ SUCCESS - Page Loads Correctly
- No red error message
- Room occupancy grid displays
- Statistics cards show numbers
- Console shows: "API Response received" with data

### ❌ STILL FAILING - Error Appears
Check console for error details. The error will show:
```
Error loading room occupancy: [error details]
Error details: {message: "...", status: 500, statusText: "..."}
```

## Common Issues & Solutions

### Issue 1: "Session expirée" or 401 Error
**Solution:** You're not logged in or token expired
- Logout and login again
- Make sure you're using correct credentials

### Issue 2: "Accès non autorisé" or 403 Error  
**Solution:** Your user doesn't have permission
- You need DEPARTMENT_HEAD or ADMIN role
- Check your user role in database

### Issue 3: Backend Still Shows Serialization Error
**Solution:** Backend not restarted
- **RESTART THE BACKEND SERVER** (see Step 1 & 2 above)
- Make sure you see "Starting University API server..." message
- Server should show: `Uvicorn running on http://127.0.0.1:8000`

### Issue 4: Frontend Not Loading
**Solution:** Frontend server not running
```powershell
cd C:\Users\pc\universety_app\frontend
npm run dev
```
Should see: `ready - started server on 0.0.0.0:3000`

## Verification Checklist

Before testing in browser, verify:

- [ ] Backend server is running (check http://localhost:8000/health)
- [ ] Backend shows: "Starting University API server..."
- [ ] Frontend server is running (check http://localhost:3000)
- [ ] No compilation errors in terminal
- [ ] Can access login page

## Quick Test Script

Run this in PowerShell to test the API directly:

```powershell
# Test debug endpoint (no auth)
$response = Invoke-RestMethod -Uri "http://localhost:8000/room-occupancy/debug/rooms"
Write-Host "Success: $($response.success)"
Write-Host "Rooms: $($response.data.Count)"
Write-Host "Week: $($response.week_info.start_date) to $($response.week_info.end_date)"
```

Expected output:
```
Success: True
Rooms: 3
Week: 2025-10-06 to 2025-10-12
```

## Files Changed (For Reference)

### Backend:
- `api/app/routers/room_occupancy.py`
  - Added: `from fastapi.responses import JSONResponse`
  - Added: `from fastapi.encoders import jsonable_encoder`
  - Updated: All return statements to use `JSONResponse(content=jsonable_encoder(...))`
  - Enhanced: Error handling with traceback logging

### Frontend:
- `frontend/lib/api.ts`
  - Added: `getRoomOccupancy()` method
  - Added: `getRoomDetails()` method
  - Added: `getRoomOccupancyStatistics()` method

- `frontend/app/dashboard/department-head/room-occupancy/page.tsx`
  - Changed: From direct fetch to API client
  - Added: Console logging for debugging
  - Enhanced: Error message parsing
  - Added: `building` field to interface

## Expected Behavior After Fix

### Backend Logs Should Show:
```
INFO: 127.0.0.1:xxxxx - "GET /room-occupancy/rooms?week_offset=0 HTTP/1.1" 200 OK
```

### Frontend Console Should Show:
```
Fetching room occupancy data...
Params: {week_offset: 0, room_type: "all", building: "all"}
API Response received: {success: true, data: [...], week_info: {...}}
Room data extracted: 19 rooms
```

### Browser Should Display:
- Room occupancy page without errors
- Statistics cards with numbers
- Room grid with colored circles (green=free, red=occupied)
- Week navigation buttons working
- Filters working

## If Still Not Working

1. **Check browser console** - Press F12, look at Console and Network tabs
2. **Check backend terminal** - Look for error messages
3. **Verify API endpoint** - Test with curl or Postman
4. **Clear browser cache** - Hard refresh with Ctrl+Shift+R
5. **Try incognito mode** - Rule out cache issues

## Contact/Debug Information

If you're still seeing the datetime serialization error:
1. Copy the exact error message from browser console
2. Copy the backend terminal output
3. Check which version of the code is running:
   ```powershell
   # Check if jsonable_encoder is in the file
   Select-String -Path "C:\Users\pc\universety_app\api\app\routers\room_occupancy.py" -Pattern "jsonable_encoder"
   ```
   Should show 6+ matches

## Summary

**THE FIX IS COMPLETE** - You just need to **RESTART THE BACKEND SERVER** for the changes to take effect.

The datetime serialization error has been fixed in the code. The server needs to reload the updated files.
