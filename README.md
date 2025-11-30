# 🎓 University Platform

A comprehensive full-stack university management platform built with modern web technologies. This platform provides complete solutions for managing students, teachers, courses, timetables, absences, and administrative tasks.

![Platform Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14.2.33-black.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [User Roles](#-user-roles)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 👨‍🎓 Student Portal
- **Personal Dashboard**: View schedules, grades, and announcements
- **Course Management**: Access course materials, assignments, and resources
- **Absence Tracking**: View attendance records and submit justifications
- **Grade Monitoring**: Real-time access to grades and academic performance
- **Timetable View**: Interactive weekly and daily schedule display
- **Messaging System**: Communicate with teachers and administrators
- **Profile Management**: Update personal information and preferences

### 👨‍🏫 Teacher Portal
- **Class Management**: Manage multiple classes and student groups
- **Attendance Tracking**: Mark absences and monitor student attendance
- **Grade Entry**: Input and manage student grades and assessments
- **Course Materials**: Upload and share learning resources
- **Timetable Management**: View teaching schedule and room assignments
- **Student Analytics**: Track individual and group performance
- **Communication Tools**: Send notifications and messages to students

### 👔 Admin Panel
- **User Management**: Create and manage student, teacher, and admin accounts
- **Department Administration**: Manage departments, specialties, and levels
- **Timetable Supervision**: Create and modify institutional schedules
- **Bulk Import**: Import users and data via CSV/Excel files
- **Analytics Dashboard**: Comprehensive reporting and statistics
- **System Configuration**: Manage global settings and permissions
- **Department Head Management**: Assign and manage department leadership

### 🎯 Department Head Features
- **Department Analytics**: View department-specific statistics and reports
- **Teacher Oversight**: Monitor teacher performance and schedules
- **Student Management**: Access department student data and performance
- **Resource Allocation**: Manage department resources and facilities

### 🔔 General Features
- **Real-time Notifications**: Instant updates for important events
- **AI-Powered Chatbot**: Intelligent classroom assistance (Groq AI integration)
- **Responsive Design**: Fully optimized for desktop, tablet, and mobile
- **Role-Based Access Control**: Secure, hierarchical permission system
- **Multi-language Support**: Ready for internationalization
- **Dark Mode**: Eye-friendly interface options
- **PDF Generation**: Export reports and documents
- **Email Integration**: Automated email notifications via SMTP

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL
- **ORM**: Prisma (Python Client v0.11.0)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Email**: SMTP integration
- **AI Integration**: Groq API for classroom chatbot
- **File Storage**: Cloudinary for media uploads
- **Server**: Uvicorn (ASGI server)

### Frontend
- **Framework**: Next.js 14.2.33 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form
- **UI Components**: Custom component library
- **Icons**: Heroicons, Lucide React
- **Notifications**: Custom notification system

### Admin Panel
- **Framework**: Next.js 14 (Separate App)
- **Port**: 3001
- **Features**: Advanced administrative controls
- **Security**: Enhanced authentication and audit logging

### DevOps & Tools
- **Containerization**: Docker & Docker Compose
- **API Testing**: Postman/Thunder Client
- **Database Tools**: Prisma Studio
- **Version Control**: Git
- **Package Manager**: npm (Frontend), pip (Backend)

## 📁 Project Structure

```
university_platform/
├── api/                          # Backend API (FastAPI)
│   ├── app/
│   │   ├── core/                 # Core functionality
│   │   │   ├── config.py         # Configuration management
│   │   │   ├── deps.py           # Dependency injection
│   │   │   ├── encryption.py     # Encryption utilities
│   │   │   ├── jwt.py            # JWT token handling
│   │   │   └── security.py       # Password hashing & security
│   │   ├── db/
│   │   │   └── prisma_client.py  # Database client
│   │   ├── models/               # Pydantic models
│   │   │   └── absence_models.py
│   │   ├── routers/              # API endpoints
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── admin.py          # Admin operations
│   │   │   ├── teacher_profile.py
│   │   │   ├── student.py
│   │   │   ├── courses.py
│   │   │   ├── absence_management.py
│   │   │   ├── classroom_ai.py   # AI chatbot
│   │   │   └── ...
│   │   ├── schemas/              # Request/Response schemas
│   │   ├── services/             # Business logic
│   │   └── utils/                # Utility functions
│   ├── prisma/
│   │   ├── schema.prisma         # Database schema
│   │   ├── seed.py               # Database seeding
│   │   └── migrations/           # Migration history
│   ├── main.py                   # Application entry point
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Backend container
│   └── .env                      # Environment variables
│
├── frontend/                     # Main Frontend (Next.js)
│   ├── app/                      # Next.js app directory
│   │   ├── login/
│   │   ├── register/
│   │   ├── dashboard/
│   │   │   ├── student/
│   │   │   ├── teacher/
│   │   │   └── admin/
│   │   ├── classroom/
│   │   ├── subjects/
│   │   └── ...
│   ├── components/               # React components
│   │   ├── auth/
│   │   ├── student/
│   │   ├── teacher/
│   │   ├── admin/
│   │   ├── layout/
│   │   └── ui/
│   ├── contexts/                 # React contexts
│   │   └── AuthContext.tsx
│   ├── lib/                      # Utility libraries
│   │   ├── api.ts                # API client
│   │   ├── auth-api.ts
│   │   └── ...
│   ├── styles/
│   │   └── globals.css
│   ├── types/                    # TypeScript types
│   ├── package.json
│   ├── Dockerfile
│   └── next.config.js
│
├── apps/
│   └── admin-panel/              # Separate Admin Panel
│       ├── app/
│       │   ├── login/
│       │   ├── dashboard/
│       │   ├── students/
│       │   ├── teachers/
│       │   ├── department-heads/
│       │   ├── timetable-admin/
│       │   ├── bulk-import/
│       │   └── global-management/
│       ├── contexts/
│       │   └── AdminAuthContext.tsx
│       ├── lib/
│       ├── package.json
│       └── next.config.ts
│
├── docker-compose.yml            # Docker orchestration
├── .gitignore
└── README.md                     # This file
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Docker** (Optional) - [Download](https://www.docker.com/products/docker-desktop)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/medali150/university-platform.git
cd university-platform
```

### 2. Backend Setup

```bash
# Navigate to API directory
cd api

# Create virtual environment
python -m venv ../.venv

# Activate virtual environment
# Windows (PowerShell)
..\.venv\Scripts\Activate.ps1
# Windows (CMD)
..\.venv\Scripts\activate.bat
# Linux/macOS
source ../.venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Generate Prisma client
python -m prisma generate
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

### 4. Admin Panel Setup

```bash
# Navigate to admin panel directory
cd ../apps/admin-panel

# Install dependencies
npm install
```

## ⚙️ Configuration

### 1. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE universety_db;
```

### 2. Environment Variables

Create `.env` file in the `api/` directory:

```env
# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/universety_db"

# JWT Configuration
SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP Email Configuration
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
EMAIL_FROM="noreply@university.edu"

# Cloudinary (File Uploads)
CLOUDINARY_CLOUD_NAME="your-cloud-name"
CLOUDINARY_API_KEY="your-api-key"
CLOUDINARY_API_SECRET="your-api-secret"

# Groq AI (Classroom Chatbot)
GROQ_API_KEY="your-groq-api-key"

# CORS
FRONTEND_URL="http://localhost:3000"
ADMIN_PANEL_URL="http://localhost:3001"
```

Create `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `.env.local` file in the `apps/admin-panel/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Database Migration

```bash
cd api

# Run migrations
python -m prisma migrate deploy

# Seed database with sample data
python prisma/seed.py
```

## 🎯 Running the Application

### Method 1: Manual Start

#### Start Backend API (Terminal 1)
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

#### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Frontend will be available at: `http://localhost:3000`

#### Start Admin Panel (Terminal 3)
```bash
cd apps/admin-panel
npm run dev
```
Admin Panel will be available at: `http://localhost:3001`

### Method 2: Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 🔑 Default Credentials

After seeding the database, use these credentials to log in:

### Admin Account
- **Email**: `admin@university.edu`
- **Password**: `password123`
- **Role**: Administrator

### Teacher Account
- **Email**: `john.smith@university.edu`
- **Password**: `password123`
- **Role**: Teacher

### Student Account
- **Email**: `student1@university.edu`
- **Password**: `password123`
- **Role**: Student

### Department Head Account
- **Email**: `dept.head@university.edu`
- **Password**: `password123`
- **Role**: Department Head

## 📚 API Documentation

### Interactive API Docs

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main API Endpoints

#### Authentication
```
POST   /auth/login              # User login
POST   /auth/register           # User registration
POST   /auth/refresh            # Refresh access token
POST   /auth/forgot-password    # Password reset request
POST   /auth/reset-password     # Reset password
GET    /auth/me                 # Get current user
```

#### Students
```
GET    /student/profile         # Get student profile
GET    /student/courses         # Get enrolled courses
GET    /student/grades          # Get grades
GET    /student/absences        # Get absence records
GET    /student/timetable       # Get student schedule
```

#### Teachers
```
GET    /teacher/profile         # Get teacher profile
GET    /teacher/groups          # Get assigned groups
GET    /teacher/schedule        # Get teaching schedule
POST   /teacher/absence/mark    # Mark student absence
GET    /teacher/students        # Get students list
```

#### Admin
```
GET    /admin/users             # List all users
POST   /admin/users             # Create new user
PUT    /admin/users/{id}        # Update user
DELETE /admin/users/{id}        # Delete user
GET    /admin/dashboard         # Dashboard statistics
POST   /admin/bulk-import       # Bulk import users
```

#### Courses & Timetable
```
GET    /courses                 # List all courses
GET    /courses/{id}            # Get course details
GET    /timetable               # Get timetable
POST   /timetable               # Create schedule entry
```

#### Absences
```
GET    /absences                # List absences
POST   /absences/justify        # Submit justification
PUT    /absences/{id}/approve   # Approve absence (admin)
```

#### AI Classroom
```
POST   /classroom/ai/chat       # Chat with AI assistant
GET    /classroom/ai/history    # Get chat history
```

## 🗄️ Database Schema

### Main Models

- **Utilisateur** (User): Base user model with role-based access
- **Etudiant** (Student): Student-specific information
- **Enseignant** (Teacher): Teacher-specific information
- **ChefDepartement** (Department Head): Department leadership
- **Departement** (Department): Academic departments
- **Specialite** (Specialty): Academic specializations
- **Niveau** (Level): Academic levels (Year 1, 2, 3, etc.)
- **Groupe** (Group): Student groups/classes
- **Matiere** (Subject/Course): Academic subjects
- **Salle** (Room): Classrooms and facilities
- **EmploiTemps** (Schedule): Timetable entries
- **Absence**: Absence records
- **Note** (Grade): Student grades
- **Moyenne** (Average): Grade averages
- **Notification**: System notifications
- **Message**: Messaging system

### Relationships

```
Utilisateur 1---1 Etudiant/Enseignant/ChefDepartement
Etudiant N---1 Groupe
Groupe N---1 Niveau
Niveau N---1 Specialite
Specialite N---1 Departement
Enseignant N---1 Departement
Matiere N---1 Enseignant
EmploiTemps N---1 Enseignant
EmploiTemps N---1 Groupe
EmploiTemps N---1 Matiere
EmploiTemps N---1 Salle
Absence N---1 Etudiant
Absence N---1 EmploiTemps
Note N---1 Etudiant
Note N---1 Matiere
```

## 👥 User Roles

### 1. **Student** (`ETUDIANT`)
- View personal schedule and courses
- Check grades and attendance
- Submit absence justifications
- Access course materials
- Use classroom AI chatbot
- Communicate with teachers

### 2. **Teacher** (`ENSEIGNANT`)
- Manage assigned classes
- Mark attendance
- Enter and manage grades
- Upload course materials
- View student information
- Send notifications to students

### 3. **Department Head** (`CHEF_DEPARTEMENT`)
- All teacher permissions
- View department analytics
- Manage department resources
- Oversee teachers in department
- Access department reports

### 4. **Administrator** (`ADMINISTRATEUR`)
- Full system access
- User management (CRUD)
- System configuration
- Timetable supervision
- Bulk data import
- Global analytics
- Department management

## 💻 Development

### Code Structure Best Practices

#### Backend (FastAPI)
```python
# Use dependency injection
from app.core.deps import get_current_user, get_prisma

@router.get("/endpoint")
async def endpoint(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(get_current_user)
):
    # Your logic here
    pass
```

#### Frontend (React/Next.js)
```typescript
// Use TypeScript for type safety
interface UserProfile {
  id: string;
  name: string;
  email: string;
}

// Use React hooks appropriately
const MyComponent: React.FC = () => {
  const [data, setData] = useState<UserProfile | null>(null);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  return <div>...</div>;
};
```

### Database Migrations

```bash
# Create a new migration
python -m prisma migrate dev --name description_of_changes

# Apply migrations
python -m prisma migrate deploy

# Reset database (CAUTION: Deletes all data)
python -m prisma migrate reset

# Generate Prisma client after schema changes
python -m prisma generate
```

### Adding New Features

1. **Backend**: Create route in `api/app/routers/`
2. **Frontend**: Add component in `frontend/components/`
3. **API Integration**: Update `frontend/lib/api.ts`
4. **Types**: Define TypeScript types in `frontend/types/`
5. **Test**: Verify functionality

## 🧪 Testing

### Backend Testing
```bash
cd api
pytest
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### E2E Testing
```bash
cd frontend
npm run test:e2e
```

## 📦 Deployment

### Production Build

#### Backend
```bash
cd api
pip install -r requirements.txt
python -m prisma generate
python -m prisma migrate deploy
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
npm start
```

#### Admin Panel
```bash
cd apps/admin-panel
npm run build
npm start
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Checklist
- [ ] Update `SECRET_KEY` with strong random value
- [ ] Configure production database
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for production domains
- [ ] Set up email service (SMTP)
- [ ] Configure Cloudinary for production
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## 🔒 Security

### Best Practices Implemented

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password security
- **CORS Configuration**: Restricted cross-origin requests
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: Prisma ORM with parameterized queries
- **Rate Limiting**: API rate limiting (recommended to implement)
- **HTTPS Only**: Force HTTPS in production
- **Environment Variables**: Sensitive data in .env files
- **Role-Based Access Control**: Hierarchical permissions

### Security Recommendations

1. Regularly update dependencies
2. Enable database backups
3. Implement API rate limiting
4. Use HTTPS in production
5. Monitor for suspicious activity
6. Regular security audits
7. Keep secrets out of version control

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- **Python**: Follow PEP 8 style guide
- **TypeScript**: Use ESLint and Prettier
- **Commits**: Use conventional commit messages
- **Documentation**: Update README for significant changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Development Team** - [medali150](https://github.com/medali150)

## 🙏 Acknowledgments

- FastAPI for the excellent Python framework
- Next.js team for the React framework
- Prisma for the amazing ORM
- The open-source community

## 📞 Support

For support, please:
- Open an issue on GitHub
- Contact the development team
- Check the documentation at `/docs`

## 🗺️ Roadmap

### Version 1.1 (Upcoming)
- [ ] Mobile application (React Native)
- [ ] Advanced analytics dashboard
- [ ] Real-time chat functionality
- [ ] Video conferencing integration
- [ ] Advanced reporting system
- [ ] Multi-language support
- [ ] Parent portal
- [ ] Library management system

### Version 1.2 (Future)
- [ ] AI-powered grade predictions
- [ ] Automated scheduling system
- [ ] Integration with payment systems
- [ ] Document management system
- [ ] Advanced notification system
- [ ] Mobile push notifications

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Active Development
- **Last Updated**: November 2025
- **Maintainers**: Active

---

**Built with ❤️ for educational institutions**

For more information, visit our [documentation](http://localhost:8000/docs) or contact the development team.
