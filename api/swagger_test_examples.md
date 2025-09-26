# University Management API - Swagger Test Scripts
# ================================================
# Copy these JSON payloads to test the API endpoints in Swagger UI
# Access Swagger UI at: http://127.0.0.1:8000/docs

## 1. User Registration Examples

### Register Admin User
```json
{
  "firstName": "John",
  "lastName": "Doe", 
  "email": "john.doe@university.com",
  "login": "johndoe",
  "password": "securepassword123",
  "role": "ADMIN"
}
```

### Register Department Head
```json
{
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@university.com", 
  "login": "janesmith",
  "password": "securepassword456",
  "role": "DEPARTMENT_HEAD"
}
```

### Register Teacher
```json
{
  "firstName": "Bob",
  "lastName": "Johnson",
  "email": "bob.johnson@university.com",
  "login": "bobjohnson", 
  "password": "securepassword789",
  "role": "TEACHER"
}
```

### Register Student
```json
{
  "firstName": "Alice",
  "lastName": "Wilson",
  "email": "alice.wilson@university.com",
  "login": "alicewilson",
  "password": "securepassword000", 
  "role": "STUDENT"
}
```

## 2. User Login Example

### Login Request
```json
{
  "login": "johndoe",
  "password": "securepassword123"
}
```

**Response will contain:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 3. Department Creation Examples

### Create Computer Science Department
```json
{
  "name": "Computer Science"
}
```

### Create Mathematics Department  
```json
{
  "name": "Mathematics"
}
```

### Create Physics Department
```json
{
  "name": "Physics"
}
```

### Create Engineering Department
```json
{
  "name": "Engineering"
}
```

## 4. Specialty Creation Examples
*(Note: Replace "DEPARTMENT_ID_HERE" with actual department ID from previous step)*

### Create AI Specialty
```json
{
  "name": "Artificial Intelligence",
  "departmentId": "DEPARTMENT_ID_HERE"
}
```

### Create Software Engineering Specialty
```json
{
  "name": "Software Engineering", 
  "departmentId": "DEPARTMENT_ID_HERE"
}
```

### Create Data Science Specialty
```json
{
  "name": "Data Science",
  "departmentId": "DEPARTMENT_ID_HERE"
}
```

## 5. Department Head Assignment
*(Note: Replace IDs with actual values)*

```json
{
  "userId": "USER_ID_HERE",
  "departmentId": "DEPARTMENT_ID_HERE"
}
```

## 6. Admin Assignment
*(Note: Replace with actual user ID)*

```json
{
  "userId": "USER_ID_HERE", 
  "level": "ADMIN"
}
```

## 7. Authorization Header
For protected endpoints, add this header in Swagger UI:

**Header Name:** `Authorization`
**Header Value:** `Bearer YOUR_ACCESS_TOKEN_HERE`

## Testing Steps in Swagger UI:

### Step 1: Test Basic Endpoints
1. Go to http://127.0.0.1:8000/docs
2. Try GET `/` - should return API info
3. Try GET `/health` - should return health status

### Step 2: User Management
1. Use POST `/auth/register` with Admin user data
2. Use POST `/auth/login` with the same credentials  
3. Copy the `access_token` from response
4. Click "Authorize" button in Swagger UI
5. Enter: `Bearer YOUR_ACCESS_TOKEN`
6. Try GET `/auth/me` - should return current user info
7. Try GET `/auth/users` - should return all users

### Step 3: Department Management
1. Use POST `/departments/` with department data (requires Admin)
2. Use GET `/departments/` to see created departments
3. Copy a department ID for next step

### Step 4: Specialty Management  
1. Use POST `/specialties/` with specialty data (requires Department Head or Admin)
2. Use GET `/specialties/` to see created specialties

### Step 5: Admin Functions
1. Use POST `/admin/department-heads` to assign department heads
2. Use GET `/admin/department-heads` to see all department heads
3. Use POST `/admin/admins` to assign admin roles
4. Use GET `/admin/admins` to see all admins

## Expected HTTP Status Codes:

- **200**: Success
- **400**: Bad Request (validation error, duplicate data)
- **401**: Unauthorized (missing or invalid token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error

## Role-Based Access Control:

- **ADMIN**: Can access all endpoints
- **DEPARTMENT_HEAD**: Can manage departments and specialties
- **TEACHER**: Can view most data
- **STUDENT**: Can view basic information

## Troubleshooting:

1. **401 Unauthorized**: Make sure to include Bearer token in Authorization header
2. **403 Forbidden**: Check if current user has required role for the endpoint
3. **400 Bad Request**: Check if all required fields are provided and valid
4. **404 Not Found**: Ensure referenced IDs (departmentId, userId) exist

## Testing with curl:

### Basic Health Check
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### Register User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@university.com", 
    "login": "johndoe",
    "password": "securepassword123",
    "role": "ADMIN"
  }'
```

### Login User
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "johndoe",
    "password": "securepassword123"
  }'
```

### Create Department (with auth token)
```bash
curl -X POST "http://127.0.0.1:8000/departments/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Computer Science"
  }'
```