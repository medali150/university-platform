# University Management System - Frontend Integration

This document describes how to run the integrated frontend-backend university management system.

## System Architecture

- **Backend**: FastAPI with PostgreSQL and Prisma ORM
- **Frontend**: Next.js with TypeScript
- **Authentication**: JWT-based with role-based access control
- **Database**: PostgreSQL with admin CRUD operations

## Prerequisites

1. **Backend Setup** (in root directory):
   - Python 3.8+
   - PostgreSQL database running
   - FastAPI server configured and running on `http://127.0.0.1:8000`

2. **Frontend Setup** (in `apps/web` directory):
   - Node.js 18+
   - npm or yarn
   - Environment variables configured

## Running the System

### 1. Start the Backend (FastAPI)

```bash
# From root directory
cd /path/to/universety_app

# Activate virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install fastapi uvicorn prisma databases[postgresql] python-jose[cryptography] python-multipart bcrypt

# Run database migrations
prisma generate
prisma db push

# Start FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The FastAPI backend will be available at: `http://127.0.0.1:8000`
- API Documentation: `http://127.0.0.1:8000/docs`
- Alternative Docs: `http://127.0.0.1:8000/redoc`

### 2. Start the Frontend (Next.js)

```bash
# From apps/web directory
cd apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```

The Next.js frontend will be available at: `http://localhost:3000`

## Environment Configuration

### Backend (.env)
```env
DATABASE_URL="postgresql://username:password@localhost:5432/university_db"
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env.local)
```env
# FastAPI Backend URL
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Admin Credentials (for testing)
NEXT_PUBLIC_ADMIN_LOGIN=mohamedali.gh15@gmail.com
NEXT_PUBLIC_ADMIN_PASSWORD=daligh15

# NextAuth Configuration (if using NextAuth)
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## Admin Credentials

For testing the admin functionality, use these credentials:
- **Login**: `mohamedali.gh15@gmail.com`
- **Password**: `daligh15`
- **Role**: `ADMIN`

## Available Admin Features

### 1. Dashboard (`/admin/dashboard`)
- System overview and statistics
- User counts by role
- University structure information
- System health monitoring

### 2. Student Management (`/admin/students`)
- View all students with filtering
- Create new students
- Edit student information
- Delete students
- Assign students to specialties, levels, and groups

### 3. Teacher Management (`/admin/teachers`)
- View all teachers with filtering
- Create new teachers
- Edit teacher information
- Delete teachers
- Assign teachers to departments and specialties
- Manage academic titles

### 4. Department Head Management (`/admin/department-heads`)
- View all department heads
- Create new department heads
- Assign teachers as department heads
- Demote department heads to teachers
- Manage appointment dates

## API Integration

The frontend uses a comprehensive API client (`lib/api-utils.ts`) that provides:

- **Authentication**: Login, logout, user profile management
- **Admin Dashboard**: Statistics, system health, recent activity
- **Student CRUD**: Complete student lifecycle management
- **Teacher CRUD**: Teacher management with specialties
- **Department Head CRUD**: Department leadership management
- **University Structure**: Departments, specialties, levels, groups

## Development Notes

### API Client Features

1. **Automatic Authentication**: JWT token management with localStorage
2. **Error Handling**: Comprehensive error responses and user feedback
3. **Type Safety**: Full TypeScript support with defined interfaces
4. **Role-Based Access**: Automatic role checking and authorization

### Frontend Architecture

1. **Pages Structure**:
   - `/admin/login` - Admin authentication
   - `/admin/dashboard` - Main admin dashboard
   - `/admin/students` - Student management
   - `/admin/teachers` - Teacher management  
   - `/admin/department-heads` - Department head management

2. **API Integration**:
   - Centralized API client with error handling
   - Automatic token management
   - Type-safe API calls
   - Loading states and error boundaries

### Backend API Endpoints

The FastAPI backend provides these admin endpoints:

- `POST /auth/login` - User authentication
- `GET /auth/me` - Current user profile
- `GET /admin/dashboard/statistics` - Dashboard stats
- `GET /admin/students/` - List students
- `POST /admin/students/` - Create student
- `PUT /admin/students/{id}` - Update student
- `DELETE /admin/students/{id}` - Delete student
- Similar endpoints for teachers and department heads

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the FastAPI backend has proper CORS configuration
2. **Authentication Failures**: Check that JWT tokens are being sent correctly
3. **Database Errors**: Verify PostgreSQL is running and accessible
4. **API Connectivity**: Ensure `NEXT_PUBLIC_API_URL` points to the running FastAPI server

### Debugging

1. **Frontend**: Use browser developer tools and console logs
2. **Backend**: Check FastAPI logs and `/docs` endpoint for API testing
3. **Database**: Use Prisma Studio or database client to verify data
4. **Network**: Use browser network tab to monitor API requests

## Production Deployment

For production deployment:

1. **Backend**: Deploy FastAPI with production WSGI server (e.g., Gunicorn)
2. **Frontend**: Build Next.js application (`npm run build`) and deploy to hosting service
3. **Database**: Use production PostgreSQL instance with proper security
4. **Environment**: Update all environment variables for production URLs and credentials

## Next Steps

- Implement additional CRUD operations for university structure
- Add file upload functionality for user profiles
- Implement advanced filtering and search
- Add data export/import capabilities
- Implement audit logging for admin actions