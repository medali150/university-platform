# 🏫 ABSENCE NOTIFICATION SYSTEM - MANUAL TESTING GUIDE

## 📋 Test Account Credentials

### 👨‍🏫 TEACHER ACCOUNT
- **📧 Email:** `wahid@gmail.com`
- **🔑 Password:** `dalighgh15`
- **👤 Name:** Wahid Iset
- **🆔 User ID:** `cmg6q6hrx0009bmnspt6lcc4w`

### 👨‍🎓 STUDENT ACCOUNT
- **📧 Email:** `ahmed.student@university.edu`
- **🔑 Password:** `student2025`
- **👤 Name:** Ahmed Ben Salem
- **🆔 User ID:** `cmgcddtqz0000bmt05gubws8y`

## 🧪 Manual Testing Steps

### Step 1: Login as Teacher
1. Open your frontend application (usually `http://localhost:3000`)
2. Use teacher credentials to login
3. Navigate to the teacher dashboard/absence management section

### Step 2: Mark Student Absent
1. Find the absence marking feature
2. Search for student: **Ahmed Ben Salem** (`ahmed.student@university.edu`)
3. Mark him absent for any subject
4. Fill in details:
   - **Date:** Today's date
   - **Time:** Any time (e.g., 10:30)
   - **Reason:** "Test absence for notification system"

### Step 3: Check Notification Logs
1. **In API Console:** Look for `AbsenceNotificationService` log messages
2. **Expected logs:** 
   ```
   📧 Mock Notification Sent:
      User: ahmed.student@university.edu
      Title: Absence Marked
      Message: You have been marked absent for [Subject]...
   ```

### Step 4: Verify Student Receives Notification
1. Logout from teacher account
2. Login as student using student credentials
3. Check the notifications section/dashboard
4. Look for the absence notification

## 🔍 What to Verify

✅ **Teacher Side:**
- Can successfully mark student absent
- Gets confirmation message
- No errors in browser console

✅ **Notification System:**
- Server logs show notification was sent
- `AbsenceNotificationService.notify_student_absence_marked()` is called
- Mock notification delivery appears in console

✅ **Student Side:**
- Can login successfully
- Receives absence notification
- Notification shows correct details (subject, date, time)
- Can view notification details

## 🛠️ Debugging Tools

### Browser Developer Tools (F12)
- **Network Tab:** Monitor API calls to `/teacher/mark-absence`
- **Console Tab:** Check for JavaScript errors
- **Application Tab:** Check local storage/cookies

### API Server Logs
Monitor for these patterns:
```
✅ Student absence notification executed successfully
📧 Target: ahmed.student@university.edu
📝 Subject: Absence marked for [Subject Name]
🎯 Result: success
```

### Direct API Testing
If frontend has issues, test directly:

```bash
# 1. Login as teacher
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"wahid@gmail.com","password":"dalighgh15"}'

# 2. Mark absence (use token from step 1)
curl -X POST http://localhost:8000/teacher/mark-absence \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "student_email": "ahmed.student@university.edu",
    "student_name": "Ahmed Ben Salem", 
    "subject_name": "Programming",
    "absence_date": "2025-10-04",
    "absence_time": "10:30",
    "reason": "Test absence"
  }'
```

## 📊 Expected Results

### ✅ Success Indicators
1. **Teacher:** Can mark absence without errors
2. **Server:** Shows notification service logs
3. **Student:** Receives absence notification
4. **API:** Returns success responses (200/201)

### ❌ Failure Indicators
1. **500 errors:** Server-side issues
2. **401/403 errors:** Authentication problems  
3. **No notifications:** Service not triggered
4. **Missing logs:** Notification system not called

## 🎯 Notification System Features

The system supports:
- **Email notifications** (mock implementation)
- **In-app notifications** 
- **Multi-channel delivery**
- **Template-based messages**
- **Error handling and logging**

## 🚀 Next Steps After Testing

If notifications work correctly:
1. Install real NotificationAPI SDK: `pip install notificationapi-python-server-sdk`
2. Replace MockNotificationAPI with production implementation
3. Configure email templates and providers
4. Test with real email delivery
5. Deploy to staging environment

---

## 🏁 Ready to Test!

Use the credentials above to test the absence notification system manually in your frontend application. Check the server console for notification logs to verify everything is working correctly!

**API Server:** http://localhost:8000  
**Frontend:** http://localhost:3000 (assuming default)

Good luck with your testing! 🎉