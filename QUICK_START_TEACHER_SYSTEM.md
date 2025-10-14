# 🚀 Quick Start Guide - Teacher Profile & Timetable System

## Prerequisites
- Backend server running on port 8000
- Frontend server running on port 3000
- PostgreSQL database configured
- Prisma schema applied

## Step 1: Start Backend Server

Open a terminal and run:
```powershell
cd c:\Users\pc\universety_app\api
python -m uvicorn main:app --reload --port 8000
```

Verify it's running: Open `http://localhost:8000/docs` in your browser

## Step 2: Start Frontend Server

Open another terminal and run:
```powershell
cd c:\Users\pc\universety_app\frontend
npm run dev
```

Verify it's running: Open `http://localhost:3000` in your browser

## Step 3: Register a Teacher

### Option A: Using the Frontend (Recommended)
1. Go to `http://localhost:3000/register`
2. Fill in the form:
   - **Prénom:** Jean
   - **Nom:** Dupont
   - **Email:** jean.dupont@university.com
   - **Rôle:** Select "Enseignant"
   - **Département:** Select a department from the dropdown
   - **Mot de passe:** password123
   - **Confirmer:** password123
3. Click "Créer le compte"

### Option B: Using the Test Script
```powershell
cd c:\Users\pc\universety_app\api
python test_create_teacher_complete.py
```

This will automatically:
- Create a teacher account
- Log in
- Test all endpoints
- Display the credentials

## Step 4: Login as Teacher

1. Go to `http://localhost:3000/login`
2. Enter the email and password from Step 3
3. Click "Se connecter"

You should be redirected to the teacher dashboard

## Step 5: View Teacher Profile

Once logged in:
1. Navigate to `/dashboard/teacher/profile`
2. You should see:
   - Personal information
   - Department details
   - Specialties in the department
   - Subjects taught (will be empty for new teachers)

## Step 6: View Teacher Timetable

1. Navigate to `/dashboard/teacher/timetable`
2. You should see:
   - Week navigation
   - Current week's schedule
   - "No classes scheduled" message (normal for new teachers)

## 🧪 Testing Endpoints Directly

### Test Profile Endpoint
```powershell
# First, get a token by logging in
curl -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"email":"jean.dupont@university.com","password":"password123"}'

# Copy the access_token from the response, then:
curl -X GET "http://localhost:8000/teacher/profile" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Schedule Endpoint
```powershell
curl -X GET "http://localhost:8000/teacher/schedule?start_date=2025-10-06&end_date=2025-10-12" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Today's Schedule
```powershell
curl -X GET "http://localhost:8000/teacher/schedule/today" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Expected Behavior

### For a New Teacher (Just Registered)
- ✅ Profile loads successfully
- ✅ Department information displays
- ✅ Specialties list shows
- ✅ Subjects taught is empty (no subjects assigned yet)
- ✅ Schedule shows "No classes scheduled" (no schedule created yet)

### For an Existing Teacher (With Data)
- ✅ Profile shows all information
- ✅ Department with specialties
- ✅ List of subjects they teach
- ✅ Schedule shows weekly classes
- ✅ Each class shows: time, subject, group, room, status

## 🐛 Troubleshooting

### Problem: "Failed to get departments"
**Solution:** Backend is not running. Start it with Step 1.

### Problem: "No teacher record found for this user"
**Solution:** User was created but teacher record is missing. Re-register or check database.

### Problem: "401 Unauthorized"
**Solution:** 
- Token expired or invalid
- Log out and log in again
- Clear localStorage and try again

### Problem: Frontend stuck on "Loading..."
**Solution:**
1. Check browser console for errors
2. Verify backend is running (`http://localhost:8000/docs`)
3. Check network tab in browser dev tools
4. Verify CORS is configured in backend

### Problem: Empty schedule
**Solution:** This is NORMAL for new teachers. Schedule must be created by:
1. Admin assigning classes
2. Department head creating schedules
3. Or manually adding test data to database

## 📝 Next Steps

After verifying the profile and timetable work:

1. **Add test schedule data** (via admin panel or database)
2. **Test schedule display** with actual classes
3. **Test absence marking** (if implemented)
4. **Test profile updates** (department changes, image upload)

## ✅ Success Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Can register teacher with department selection
- [ ] Can login as teacher
- [ ] Profile page loads with teacher info
- [ ] Department and specialties display
- [ ] Timetable page loads (empty is ok)
- [ ] Week navigation works
- [ ] No console errors

If all checkboxes are checked, your teacher profile and timetable system is working correctly! 🎉
