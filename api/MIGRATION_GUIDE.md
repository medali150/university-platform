# Migration: From Login to Email Authentication

This migration removes the `login` field from the User model and uses `email` for authentication instead.

## 🔄 Changes Made

### Backend Changes:
1. **Database Schema** (`prisma/schema.prisma`):
   - Removed `login String @unique` field from User model
   - Email field remains as the unique identifier

2. **User Schemas** (`app/schemas/user.py`):
   - Removed `login` field from `UserBase`, `UserCreate`, and `UserLogin`
   - `UserLogin` now uses `email` instead of `login`

3. **Authentication Routes** (`app/routers/auth.py`):
   - Updated registration to check only email uniqueness
   - Updated login to authenticate using email
   - Updated error messages

### Frontend Changes:
1. **API Client** (`lib/api.ts`):
   - Updated login request to send `email` instead of `login`
   - Updated registration interface to remove `login` field

2. **Forms**:
   - Removed username/login field from registration form
   - Updated validation schemas
   - Updated test credentials display

3. **Authentication Service**:
   - Updated interfaces to use email-only authentication

## 🚀 How to Apply Migration

### Option 1: Automatic Migration (Recommended)
```bash
cd api
python migrate_to_email_auth.py
```

### Option 2: Manual Migration
```bash
cd api

# Generate and apply migration
prisma migrate dev --name remove_login_field

# Generate Prisma client
prisma generate

# Update test data (optional)
python setup_sample_data.py
```

## 📋 New Test Credentials

After migration, use these email-based credentials:

- **Department Head**: `john.doe@university.com` / `depthead123`
- **Teacher**: `teacher@university.com` / `teacher123`
- **Student**: `student@university.edu` / `student123`

## ⚠️ Important Notes

1. **Existing Data**: If you have existing users, make sure they have valid email addresses before migration
2. **Frontend Update**: The frontend now sends `email` instead of `login` to the authentication endpoints
3. **API Compatibility**: This is a breaking change - any existing API clients must be updated
4. **Database**: The migration will drop the `login` column permanently

## 🧪 Testing

After migration:

1. **Frontend**: Go to `http://localhost:3000/login` and test with the new email credentials
2. **API**: Test the endpoints directly:

```bash
# Login with email
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@university.com", "password": "depthead123"}'

# Register with email
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "lastName": "User", 
    "email": "test@example.com",
    "password": "password123",
    "role": "STUDENT"
  }'
```

## 🔧 Rollback Plan

If you need to rollback:

1. Revert the Prisma schema changes
2. Add back the `login` field
3. Generate a new migration
4. Update the authentication code
5. Restore the old API endpoints

This migration simplifies the authentication system and follows standard practices by using email as the primary login identifier.