# 🧪 SWAGGER UI TEST SCRIPTS - Copy & Paste Ready

## 📋 How to Use These Scripts:

1. **Start your server**: `cd api && uvicorn main:app --reload`
2. **Open Swagger UI**: Go to `http://127.0.0.1:8000/docs`
3. **Copy and paste** the JSON payloads below into the respective endpoints
4. **Follow the order** for proper testing flow

---

## 🔥 STEP 1: Test Basic Endpoints (No Auth Required)

### 1.1 Health Check - GET `/health`
**Click "Try it out" → Execute**
```
No payload needed - just click Execute
```
**Expected**: `{"status":"healthy","database":"connected","users_count":6}`

### 1.2 Root Endpoint - GET `/`
**Click "Try it out" → Execute**
```
No payload needed - just click Execute
```
**Expected**: API information with endpoints list

### 1.3 Get All Departments - GET `/departments`
**Click "Try it out" → Execute**
```
No payload needed - just click Execute
```
**Expected**: Array of departments with specialties

### 1.4 Get All Specialties - GET `/specialties`
**Click "Try it out" → Execute**
```
No payload needed - just click Execute
```
**Expected**: Array of specialties with department info

---

## 🔐 STEP 2: Authentication (MUST DO FIRST for protected endpoints)

### 2.1 Admin Login - POST `/auth/login`
**Copy this payload:**
```json
{
  "login": "admin.user",
  "password": "admin123"
}
```
**Expected Response**: `{"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}`

### 🚨 IMPORTANT: Authorize in Swagger
1. **Copy the `access_token`** from login response (the long string)
2. **Click the "Authorize" button** at the top of Swagger UI (🔒 icon)
3. **Paste the token** in the format: `Bearer YOUR_TOKEN_HERE`
4. **Click "Authorize"** - you'll see a green lock icon
5. **Click "Close"**

### 2.2 Get Current User - GET `/auth/me`
**After authorization, click "Try it out" → Execute**
```
No payload needed - requires Bearer token
```
**Expected**: Current user information

### 2.3 Get All Users - GET `/auth/users`
**After authorization, click "Try it out" → Execute**
```
No payload needed - requires Bearer token
```
**Expected**: Array of all users (should work now - was 500 error before)

---

## 👨‍🎓 STEP 3: Students Management (Admin Only)

### 3.1 Get All Students - GET `/admin/students`
**After authorization, click "Try it out" → Execute**
```
Parameters (optional):
- page: 1
- page_size: 10
- department_id: (use a department ID from /departments)
- specialty_id: (use a specialty ID from /specialties)
- academic_year: (leave empty)
```
**Expected**: Paginated list of students with group/level info (FIXED - was 500 error before)

### 3.2 Get Single Student - GET `/admin/students/{student_id}`
**Use a student ID from the previous response:**
```
Path parameter: student_id = "cm1jqr9nt0002131xmkvayqxs" (or any ID from students list)
```
**Expected**: Detailed student information with level accessed through group

---

## 👨‍🏫 STEP 4: Teachers Management (Admin Only)

### 4.1 Get All Teachers - GET `/admin/teachers`
**After authorization, click "Try it out" → Execute**
```
Parameters (optional):
- page: 1
- page_size: 10
- search: (leave empty)
- department_id: (leave empty)
```
**Expected**: Paginated list of teachers (was 500 error before)

### 4.2 Get Single Teacher - GET `/admin/teachers/{teacher_id}`
**Use a teacher ID from the previous response:**
```
Path parameter: teacher_id = "cm1jqr9pj0004131x8w3h7qyc" (or any ID from teachers list)
```
**Expected**: Detailed teacher information

---

## 👨‍💼 STEP 5: Department Heads Management (Admin Only)

### 5.1 Get All Department Heads - GET `/admin/department-heads`
**After authorization, click "Try it out" → Execute**
```
Parameters (optional):
- page: 1
- page_size: 10
```
**Expected**: List of department heads (was 500 error before)

---

## 📈 STEP 6: Levels Management (Admin Only)

### 6.1 Get All Levels - GET `/admin/levels`
**After authorization, click "Try it out" → Execute**
```
Parameters (optional):
- page: 1
- page_size: 10
- search: (leave empty)
- specialty_id: (leave empty)
```
**Expected**: Paginated list of academic levels (was 500 error before)

### 6.2 Create New Level - POST `/admin/levels`
**Copy this payload:**
```json
{
  "name": "Test Level 1A",
  "specialtyId": "cm1jqr9ok0001131x9kqj8xyx",
  "description": "Test level created via Swagger"
}
```
**Note**: Use a real specialty ID from `/specialties` endpoint
**Expected**: Created level with 201 status

---

## 📖 STEP 7: Subjects Management (Admin Only)

### 7.1 Get All Subjects - GET `/admin/subjects`
**After authorization, click "Try it out" → Execute**
```
Parameters (optional):
- page: 1
- page_size: 10
- search: (leave empty)
- level_id: (leave empty)
- teacher_id: (leave empty)
```
**Expected**: Paginated list of subjects (was 500 error before)

### 7.2 Get Levels Helper - GET `/admin/subjects/helpers/levels`
**After authorization, click "Try it out" → Execute**
```
No payload needed
```
**Expected**: List of levels for subject creation (was 500 error before)

### 7.3 Get Teachers Helper - GET `/admin/subjects/helpers/teachers`
**After authorization, click "Try it out" → Execute**
```
No payload needed
```
**Expected**: List of teachers for subject assignment (was 500 error before)

### 7.4 Create New Subject - POST `/admin/subjects`
**Copy this payload:**
```json
{
  "name": "Test Mathematics",
  "description": "Test subject created via Swagger",
  "credits": 3,
  "levelId": "cm1jqr9p20003131xqw8h5xyz",
  "teacherId": "cm1jqr9pj0004131x8w3h7qyc",
  "code": "MATH101"
}
```
**Note**: Use real level ID and teacher ID from helper endpoints
**Expected**: Created subject with 201 status

---

## 📊 STEP 8: Admin Dashboard (Admin Only)

### 8.1 Dashboard Statistics - GET `/admin/dashboard/stats`
**After authorization, click "Try it out" → Execute**
```
No payload needed
```
**Expected**: Dashboard statistics (was 404 error before - now fixed)

### 8.2 Dashboard Statistics (Alternative) - GET `/admin/dashboard/statistics`
**After authorization, click "Try it out" → Execute**
```
No payload needed
```
**Expected**: Same statistics as above

### 8.3 Search Users - GET `/admin/dashboard/search`
**After authorization, click "Try it out" → Execute**
```
Parameters:
- query: "admin"
- role: (leave empty or use "ADMIN")
- limit: 10
```
**Expected**: Search results for users matching query

---

## 🧪 STEP 9: Error Handling Tests

### 9.1 Test Unauthorized Access - GET `/admin/students` (without authorization)
**First, click "Authorize" and click "Logout" to remove token, then:**
```
No payload needed - should fail with 401
```
**Expected**: `{"detail":"Not authenticated"}` with 401 status

### 9.2 Test Invalid Endpoint - GET `/non-existent-endpoint`
**Click "Try it out" → Execute**
```
No payload needed
```
**Expected**: 404 Not Found

---

## 🎯 SUCCESS CRITERIA:

✅ **All endpoints should return 200/201 status codes** (not 500 errors)
✅ **Authentication should work** (get valid tokens)
✅ **CRUD operations should complete** (create subjects, levels)
✅ **Pagination should work** (students, teachers, subjects lists)
✅ **Search functionality should work** (no case-sensitive issues)
✅ **Helper endpoints should provide data** (levels, teachers for subjects)
✅ **Dashboard should show statistics** (no aggregation errors)

## 🚨 If You See 500 Errors:
- Check that the database is running
- Verify the server started without errors
- Make sure you're using valid IDs from previous responses
- Check server logs for specific error details

---

**🎉 Expected Result**: All tests should pass without 500 Internal Server Errors. The Prisma syntax issues have all been fixed!