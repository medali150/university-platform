# University Admin CRUD Operations Guide

## Overview
This guide provides comprehensive documentation for admin CRUD (Create, Read, Update, Delete) operations for managing students, teachers, and department heads in the University Management System.

## 🔐 Authentication

All admin endpoints require authentication with `ADMIN` role.

### Login as Admin
```http
POST /auth/login
Content-Type: application/json

{
  "login": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "admin-id",
    "firstName": "System",
    "lastName": "Administrator",
    "email": "admin@university.com",
    "role": "ADMIN"
  }
}
```

### Use Token in Headers
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 👨‍🎓 Student Management

### 1. Get All Students
```http
GET /admin/students/
Authorization: Bearer YOUR_TOKEN

# Optional query parameters:
# ?department_id=dept-id
# ?specialty_id=specialty-id  
# ?academic_year=2024
```

### 2. Get Student by ID
```http
GET /admin/students/{student_id}
Authorization: Bearer YOUR_TOKEN
```

### 3. Create Student
```http
POST /admin/students/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@university.com",
  "login": "john.doe",
  "password": "student123",
  "role": "STUDENT"
}

# Optional query parameters:
# ?specialty_id=specialty-id
# ?level_id=level-id
# ?group_id=group-id
```

### 4. Update Student
```http
PUT /admin/students/{student_id}
Authorization: Bearer YOUR_TOKEN

# Optional query parameters:
# ?specialty_id=new-specialty-id
# ?level_id=new-level-id
# ?group_id=new-group-id
```

### 5. Delete Student
```http
DELETE /admin/students/{student_id}
Authorization: Bearer YOUR_TOKEN
```

## 👨‍🏫 Teacher Management

### 1. Get All Teachers
```http
GET /admin/teachers/
Authorization: Bearer YOUR_TOKEN

# Optional query parameters:
# ?department_id=dept-id
# ?specialty_id=specialty-id
# ?academic_title=Professor
```

### 2. Get Teacher by ID
```http
GET /admin/teachers/{teacher_id}
Authorization: Bearer YOUR_TOKEN
```

### 3. Create Teacher
```http
POST /admin/teachers/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "firstName": "Dr. Jane",
  "lastName": "Smith",
  "email": "jane.smith@university.com",
  "login": "jane.smith",
  "password": "teacher123",
  "role": "TEACHER"
}

# Optional query parameters:
# ?department_id=dept-id
# ?academic_title=Professor
# ?years_of_experience=15
# ?specialty_ids=specialty1,specialty2
```

### 4. Update Teacher
```http
PUT /admin/teachers/{teacher_id}
Authorization: Bearer YOUR_TOKEN

# Optional query parameters:
# ?department_id=new-dept-id
# ?academic_title=new-title
# ?years_of_experience=20
# ?specialty_ids=new-specialty1,new-specialty2
```

### 5. Delete Teacher
```http
DELETE /admin/teachers/{teacher_id}
Authorization: Bearer YOUR_TOKEN
```

### 6. Add Specialty to Teacher
```http
POST /admin/teachers/{teacher_id}/specialties/{specialty_id}
Authorization: Bearer YOUR_TOKEN
```

### 7. Remove Specialty from Teacher
```http
DELETE /admin/teachers/{teacher_id}/specialties/{specialty_id}
Authorization: Bearer YOUR_TOKEN
```

## 👨‍💼 Department Head Management

### 1. Get All Department Heads
```http
GET /admin/department-heads/
Authorization: Bearer YOUR_TOKEN

# Optional query parameters:
# ?department_id=dept-id
```

### 2. Get Department Head by ID
```http
GET /admin/department-heads/{dept_head_id}
Authorization: Bearer YOUR_TOKEN
```

### 3. Create Department Head
```http
POST /admin/department-heads/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "firstName": "Prof. Robert",
  "lastName": "Johnson",
  "email": "robert.johnson@university.com",
  "login": "robert.johnson",
  "password": "head123",
  "role": "DEPARTMENT_HEAD"
}

# Required query parameters:
# ?department_id=dept-id
# Optional:
# ?appointment_date=2024-01-15
```

### 4. Update Department Head
```http
PUT /admin/department-heads/{dept_head_id}
Authorization: Bearer YOUR_TOKEN

# Optional query parameters:
# ?department_id=new-dept-id
# ?appointment_date=2024-06-01
```

### 5. Delete Department Head
```http
DELETE /admin/department-heads/{dept_head_id}
Authorization: Bearer YOUR_TOKEN
```

### 6. Assign Teacher as Department Head
```http
POST /admin/department-heads/assign-from-teacher/{teacher_id}
Authorization: Bearer YOUR_TOKEN

# Required query parameters:
# ?department_id=dept-id
# Optional:
# ?appointment_date=2024-01-15
```

### 7. Demote Department Head to Teacher
```http
POST /admin/department-heads/{dept_head_id}/demote-to-teacher
Authorization: Bearer YOUR_TOKEN
```

## 📊 Admin Dashboard

### 1. Get Dashboard Statistics
```http
GET /admin/dashboard/statistics
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "overview": {
    "totalUsers": 150,
    "totalStudents": 100,
    "totalTeachers": 45,
    "totalDepartmentHeads": 5,
    "recentRegistrations": 12
  },
  "universityStructure": {
    "faculties": 3,
    "departments": 12,
    "specialties": 25,
    "levels": 5,
    "groups": 48
  },
  "roleDistribution": {
    "STUDENT": 100,
    "TEACHER": 45,
    "DEPARTMENT_HEAD": 5
  },
  "departmentStats": {
    "studentsByDepartment": {
      "Computer Science": 35,
      "Mathematics": 28
    },
    "teachersByDepartment": {
      "Computer Science": 12,
      "Mathematics": 10
    }
  }
}
```

### 2. Get Recent Activity
```http
GET /admin/dashboard/recent-activity?limit=20
Authorization: Bearer YOUR_TOKEN
```

### 3. Get System Health
```http
GET /admin/dashboard/system-health
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "database": {
    "status": "healthy",
    "lastChecked": "2024-01-15T10:30:00Z"
  },
  "dataIntegrity": {
    "status": "issues_found",
    "inconsistencies": [
      {
        "type": "missing_data",
        "description": "5 students without assigned specialty"
      },
      {
        "type": "missing_management", 
        "description": "2 departments without assigned heads",
        "details": ["Physics Department", "Chemistry Department"]
      }
    ]
  }
}
```

### 4. Search Users
```http
GET /admin/dashboard/search?query=john&role=STUDENT&limit=50
Authorization: Bearer YOUR_TOKEN
```

### 5. Bulk Delete Users
```http
POST /admin/dashboard/bulk-actions/delete-users
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "user_ids": ["user-id-1", "user-id-2", "user-id-3"]
}
```

## 🧪 Testing with Python

### Install Dependencies
```bash
pip install requests
```

### Run Comprehensive Tests
```bash
python test_admin_crud.py
```

### Sample Test Code
```python
import requests

# Setup
base_url = "http://127.0.0.1:8000"
session = requests.Session()

# Login as admin
login_data = {"login": "admin", "password": "admin123"}
response = session.post(f"{base_url}/auth/login", json=login_data)
token = response.json()["access_token"]
session.headers.update({"Authorization": f"Bearer {token}"})

# Create student
student_data = {
    "firstName": "Alice",
    "lastName": "Wonder",
    "email": "alice@university.com",
    "login": "alice.wonder",
    "password": "student123",
    "role": "STUDENT"
}
response = session.post(f"{base_url}/admin/students/", json=student_data)
print(f"Student created: {response.status_code}")

# Get dashboard statistics
response = session.get(f"{base_url}/admin/dashboard/statistics")
stats = response.json()
print(f"Total users: {stats['overview']['totalUsers']}")
```

## 🌐 Testing with Swagger UI

1. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Open Swagger UI:** http://127.0.0.1:8000/docs

3. **Authenticate:**
   - Click the "Authorize" button (🔒)
   - Login as admin using `/auth/login` endpoint
   - Copy the `access_token` from the response
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"

4. **Test endpoints:** All admin endpoints will now be accessible

## 📝 Common Use Cases

### 1. Bulk Student Registration
```python
# Create multiple students for a department
students = [
    {"firstName": "Student1", "lastName": "Test", "email": "s1@uni.com", 
     "login": "student1", "password": "pass123", "role": "STUDENT"},
    {"firstName": "Student2", "lastName": "Test", "email": "s2@uni.com", 
     "login": "student2", "password": "pass123", "role": "STUDENT"}
]

for student in students:
    response = session.post(
        f"{base_url}/admin/students/?specialty_id=specialty-id",
        json=student
    )
```

### 2. Department Head Assignment
```python
# First create teacher, then assign as department head
teacher_response = session.post(f"{base_url}/admin/teachers/", json=teacher_data)
teacher_id = teacher_response.json()["id"]

# Assign as department head
session.post(
    f"{base_url}/admin/department-heads/assign-from-teacher/{teacher_id}",
    params={"department_id": "dept-id", "appointment_date": "2024-01-15"}
)
```

### 3. System Health Monitoring
```python
# Check system health regularly
health = session.get(f"{base_url}/admin/dashboard/system-health").json()

if health["dataIntegrity"]["status"] != "healthy":
    print("⚠️ Data integrity issues found:")
    for issue in health["dataIntegrity"]["inconsistencies"]:
        print(f"  - {issue['description']}")
```

## 🚨 Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{"detail": "Not authenticated"}
```

**403 Forbidden:**
```json
{"detail": "Insufficient permissions. Admin role required."}
```

**404 Not Found:**
```json
{"detail": "Student not found"}
```

**400 Bad Request:**
```json
{"detail": "User with this email or login already exists"}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🔒 Security Considerations

1. **Role-Based Access:** All endpoints require `ADMIN` role
2. **Input Validation:** All inputs are validated using Pydantic schemas
3. **Password Hashing:** Passwords are hashed using bcrypt
4. **JWT Tokens:** Secure token-based authentication
5. **CORS:** Configurable CORS settings for frontend integration
6. **SQL Injection:** Protected through Prisma ORM parameterized queries

## 📈 Performance Tips

1. **Use Filters:** Apply query parameters to reduce response size
2. **Pagination:** Use `limit` and `offset` for large datasets
3. **Bulk Operations:** Use bulk endpoints for multiple operations
4. **Caching:** Consider caching frequently accessed data
5. **Database Indexes:** Ensure proper indexing on frequently queried fields

## 🔧 Troubleshooting

### Common Issues:

1. **"Department already has a head"**
   - Solution: Remove existing department head first or use update endpoint

2. **"Cannot demote: User does not have teacher record"**
   - Solution: User must have both teacher and department head records

3. **"Specialty not found"**
   - Solution: Create specialty first or use existing specialty ID

4. **Database connection issues**
   - Check Prisma configuration and database connectivity
   - Ensure database migrations are applied

### Debug Mode:
Enable debug logging by setting `DEBUG=true` in environment variables.

---

## 🎯 Next Steps

1. Test all endpoints using the provided test script
2. Integrate with your frontend application
3. Set up monitoring and logging
4. Configure production security settings
5. Implement data backup strategies