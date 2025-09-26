# 🛠️ Database Fix & Admin CRUD Guide

## 🐛 **Current Issue**
The error `Could not find field at createOneUser.data.role` indicates that your database schema doesn't match your Prisma schema. The database table is missing the `role` column.

## 🔧 **Step 1: Fix Database Schema**

### Option A: Push Schema to Database (Recommended)
```bash
# Navigate to api directory
cd C:\Users\pc\universety_app\api

# Push schema changes to database
npx prisma db push
```

### Option B: If Prisma is not installed globally
```bash
# Install Prisma CLI if needed
npm install -g prisma

# Then push schema
prisma db push
```

### Option C: Manual Database Update (if above doesn't work)
Connect to your PostgreSQL database and run:
```sql
-- Add role column if missing
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "role" TEXT;

-- Create enum type if not exists
CREATE TYPE "Role" AS ENUM ('STUDENT', 'TEACHER', 'DEPARTMENT_HEAD', 'ADMIN');

-- Update column type
ALTER TABLE "User" ALTER COLUMN "role" TYPE "Role" USING "role"::Role;
```

## 🚀 **Step 2: Start Server & Test**

### 1. Verify Database Connection
```bash
# Test database connection
python -c "
import asyncio
from app.db.prisma_client import get_prisma

async def test():
    prisma = await get_prisma()
    count = await prisma.user.count()
    print(f'✅ Database connected. Users: {count}')

asyncio.run(test())
"
```

### 2. Start the Server
```bash
uvicorn main:app --reload
```

### 3. Create Admin User
```bash
python setup_admin.py
```

## 📋 **Step 3: Use Admin CRUD System**

### Method 1: Using Swagger UI (Easiest)

1. **Open Swagger UI**: http://127.0.0.1:8000/docs

2. **Create Admin User** (if needed):
   - Go to `/auth/register` endpoint
   - Use this JSON:
   ```json
   {
     "firstName": "Admin",
     "lastName": "User",
     "email": "admin@university.com",
     "login": "admin",
     "password": "admin123",
     "role": "ADMIN"
   }
   ```

3. **Login as Admin**:
   - Go to `/auth/login` endpoint
   - Use:
   ```json
   {
     "login": "admin", 
     "password": "admin123"
   }
   ```
   - Copy the `access_token`

4. **Authorize in Swagger**:
   - Click the "Authorize" button (🔒) 
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"

5. **Test Admin Endpoints**:
   
   **Create Student:**
   - Go to `/admin/students/` POST
   - JSON Body:
   ```json
   {
     "firstName": "John",
     "lastName": "Doe",
     "email": "john.doe@university.com", 
     "login": "john.doe",
     "password": "student123",
     "role": "STUDENT"
   }
   ```
   
   **Create Teacher:**
   - Go to `/admin/teachers/` POST
   - JSON Body:
   ```json
   {
     "firstName": "Dr. Jane",
     "lastName": "Smith",
     "email": "jane.smith@university.com",
     "login": "jane.smith", 
     "password": "teacher123",
     "role": "TEACHER"
   }
   ```
   - Query Parameters: `academic_title=Professor&years_of_experience=10`
   
   **Get Dashboard Stats:**
   - Go to `/admin/dashboard/statistics` GET
   - No body needed - just execute

### Method 2: Using cURL Commands

```bash
# 1. Login as admin
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "admin123"}'

# 2. Use the token in subsequent requests (replace TOKEN)
curl -X GET "http://127.0.0.1:8000/admin/dashboard/statistics" \
  -H "Authorization: Bearer TOKEN"

# 3. Create a student
curl -X POST "http://127.0.0.1:8000/admin/students/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Alice",
    "lastName": "Wonder", 
    "email": "alice@university.com",
    "login": "alice.wonder",
    "password": "student123",
    "role": "STUDENT"
  }'
```

### Method 3: Using Python Script

```python
import requests

# Setup
base_url = "http://127.0.0.1:8000"
session = requests.Session()

# 1. Login
login_data = {"login": "admin", "password": "admin123"}
response = session.post(f"{base_url}/auth/login", json=login_data)
token = response.json()["access_token"]
session.headers.update({"Authorization": f"Bearer {token}"})

# 2. Create student
student_data = {
    "firstName": "Bob",
    "lastName": "Builder", 
    "email": "bob@university.com",
    "login": "bob.builder",
    "password": "student123", 
    "role": "STUDENT"
}
response = session.post(f"{base_url}/admin/students/", json=student_data)
print(f"Student created: {response.status_code}")

# 3. Get all students
response = session.get(f"{base_url}/admin/students/")
students = response.json()
print(f"Found {len(students)} students")

# 4. Dashboard stats
response = session.get(f"{base_url}/admin/dashboard/statistics")
stats = response.json()
print(f"Total users: {stats['overview']['totalUsers']}")
```

## 🎯 **Available Admin Endpoints**

### Student Management
- `GET /admin/students/` - List all students
- `POST /admin/students/` - Create student
- `GET /admin/students/{id}` - Get student details
- `PUT /admin/students/{id}` - Update student
- `DELETE /admin/students/{id}` - Delete student

### Teacher Management  
- `GET /admin/teachers/` - List all teachers
- `POST /admin/teachers/` - Create teacher
- `GET /admin/teachers/{id}` - Get teacher details
- `PUT /admin/teachers/{id}` - Update teacher
- `DELETE /admin/teachers/{id}` - Delete teacher
- `POST /admin/teachers/{id}/specialties/{specialty_id}` - Add specialty
- `DELETE /admin/teachers/{id}/specialties/{specialty_id}` - Remove specialty

### Department Head Management
- `GET /admin/department-heads/` - List all department heads
- `POST /admin/department-heads/` - Create department head
- `GET /admin/department-heads/{id}` - Get department head details
- `PUT /admin/department-heads/{id}` - Update department head
- `DELETE /admin/department-heads/{id}` - Delete department head
- `POST /admin/department-heads/assign-from-teacher/{teacher_id}` - Promote teacher
- `POST /admin/department-heads/{id}/demote-to-teacher` - Demote to teacher

### Dashboard & Analytics
- `GET /admin/dashboard/statistics` - University statistics
- `GET /admin/dashboard/recent-activity` - Recent user activity
- `GET /admin/dashboard/system-health` - System health check
- `GET /admin/dashboard/search` - Search users
- `POST /admin/dashboard/bulk-actions/delete-users` - Bulk delete

## 🔍 **Troubleshooting**

### If you get "role field not found":
1. Run `npx prisma db push` to update database schema
2. Restart the server
3. Try again

### If admin login fails:
1. Create admin user via `/auth/register` first
2. Use exact credentials: `admin` / `admin123`
3. Make sure to use ADMIN role

### If endpoints return 403 Forbidden:
1. Make sure you're logged in as admin
2. Check the Authorization header: `Bearer YOUR_TOKEN`
3. Token might have expired - login again

## ✅ **Quick Test Checklist**

- [ ] Database schema updated (`prisma db push`)
- [ ] Server running (`uvicorn main:app --reload`)  
- [ ] Admin user created (via `/auth/register`)
- [ ] Can login as admin (via `/auth/login`)
- [ ] Can access `/admin/dashboard/statistics`
- [ ] Can create student via `/admin/students/`
- [ ] Swagger UI working at http://127.0.0.1:8000/docs

Once the database issue is fixed, all admin CRUD operations will work perfectly! 🎓✨