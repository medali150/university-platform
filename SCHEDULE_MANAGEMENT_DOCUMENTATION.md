# Schedule Management System for Department Heads

## 🎯 Overview

I've implemented a comprehensive schedule management system similar to the university timetable video you referenced. This system allows department heads to create, edit, and manage class schedules with an intuitive visual interface.

## 🏗️ System Architecture

### Backend Components (FastAPI)
- **Schedule Endpoints**: `/schedules/*` routes with full CRUD operations
- **Department Authorization**: Only department heads can manage schedules for their own department
- **Conflict Detection**: Automatic detection of room, teacher, and group conflicts
- **Student Viewing**: Endpoints for students to view their schedules in timetable format

### Frontend Components (Next.js Admin Panel)
- **Schedule Management Page**: Visual timetable interface at `/schedules`
- **API Integration**: Connected to FastAPI backend through admin-api.ts
- **Interactive Grid**: Click-to-create schedule functionality
- **Responsive Design**: Works on desktop and tablet devices

## 📅 Features Implemented

### 1. Visual Timetable Interface
- **Grid Layout**: Time slots (rows) vs. Days of week (columns)
- **Interactive Cells**: Click empty cells to create new schedules
- **Color-coded Entries**: Different colors for different subjects/status
- **Hover Effects**: Visual feedback for interactive elements

### 2. Schedule Creation Workflow
1. **Filter Selection**: Department → Specialty → Level → Group → Week
2. **Time Slot Selection**: Click on desired day/time combination
3. **Form Modal**: Enter subject, room, and date information
4. **Conflict Validation**: Automatic checking before creation
5. **Real-time Updates**: Immediate reflection in timetable

### 3. Conflict Detection System
- **Room Conflicts**: Same room, overlapping times
- **Teacher Conflicts**: Same teacher, overlapping times  
- **Group Conflicts**: Same group, overlapping times
- **Real-time Validation**: Checks before saving

### 4. Authorization & Security
- **Department Ownership**: Only manage schedules for assigned department
- **JWT Authentication**: Secure API access
- **Role Validation**: Department head privileges required

## 🔧 Technical Implementation

### Backend API Endpoints

```python
# Department Head Schedule Management
POST   /schedules/                    # Create new schedule
GET    /schedules/department         # Get department schedules
PUT    /schedules/{schedule_id}      # Update schedule
DELETE /schedules/{schedule_id}      # Delete schedule
POST   /schedules/check-conflicts    # Check for conflicts

# Student Schedule Viewing
GET    /student/my-schedule          # Get student's schedules
GET    /student/weekly-timetable     # Weekly timetable view
GET    /student/today-schedule       # Today's schedule
```

### Frontend Components

```tsx
// Schedule Management Page
/apps/admin-panel/app/schedules/page.tsx

// Key Features:
- Department/Group filtering
- Visual timetable grid
- Schedule creation modal
- Real-time conflict checking
- Responsive design
```

### Database Schema

```prisma
model Schedule {
  id         String        @id @default(cuid())
  date       DateTime      # Schedule date
  startTime  DateTime      # Start time
  endTime    DateTime      # End time
  roomId     String        # Assigned room
  subjectId  String        # Subject being taught
  groupId    String        # Student group
  teacherId  String        # Assigned teacher
  status     ScheduleStatus @default(PLANNED)
  
  // Relations
  room       Room      @relation(fields: [roomId], references: [id])
  subject    Subject   @relation(fields: [subjectId], references: [id])
  group      Group     @relation(fields: [groupId], references: [id])
  teacher    Teacher   @relation(fields: [teacherId], references: [id])
}
```

## 🎨 User Interface Design

### Time Slots Configuration
```javascript
const timeSlots = [
  { id: '1', start: '08:00', end: '09:30', label: '08:00 - 09:30' },
  { id: '2', start: '09:30', end: '11:00', label: '09:30 - 11:00' },
  { id: '3', start: '11:15', end: '12:45', label: '11:15 - 12:45' },
  { id: '4', start: '12:45', end: '14:15', label: '12:45 - 14:15' },
  { id: '5', start: '14:15', end: '15:45', label: '14:15 - 15:45' },
  { id: '6', start: '15:45', end: '17:15', label: '15:45 - 17:15' },
];
```

### Visual Elements
- **Empty Cells**: Show "+" icon for adding schedules
- **Filled Cells**: Display subject name, room, and teacher
- **Color Coding**: Blue theme with status indicators
- **Hover States**: Interactive feedback for all clickable elements

## 📱 User Experience Flow

### Department Head Workflow:
1. **Login**: Access admin panel with department head credentials
2. **Navigate**: Click "Schedule Management" from dashboard
3. **Filter**: Select Department → Specialty → Level → Group → Week
4. **View**: Visual timetable appears with existing schedules
5. **Create**: Click empty time slot to create new schedule
6. **Fill Form**: Select subject, room, and date
7. **Validate**: System checks for conflicts automatically
8. **Save**: Schedule appears immediately in timetable

### Student View:
- **My Schedule**: Personal schedule view
- **Weekly Timetable**: Grid format similar to department head view
- **Today's Schedule**: Quick view of current day's classes

## 🔒 Security & Authorization

### Department Head Permissions:
- **Own Department Only**: Can only create schedules for their department
- **JWT Protected**: All API calls require valid authentication
- **Role Validation**: DEPARTMENT_HEAD role required

### Conflict Prevention:
- **Real-time Validation**: Checks conflicts before saving
- **Multiple Validation Types**: Room, teacher, and group conflicts
- **User-friendly Errors**: Clear messaging for conflict resolution

## 🚀 Setup & Usage Instructions

### 1. Backend Setup:
```bash
# Start API server
cd api/
python start_server.py
```

### 2. Frontend Setup:
```bash
# Start admin panel
cd apps/admin-panel/
npm run dev
```

### 3. Access Schedule Management:
1. Login as department head: `depthead` / `depthead123`
2. Navigate to Dashboard
3. Click "Schedule Management"
4. Follow the filtering workflow to create schedules

### 4. Sample Data:
```bash
# Create sample data for testing
cd api/
python create_sample_data_clean.py
python setup_student_user.py
```

## 🔄 Integration Status

### ✅ Completed Features:
- Visual timetable interface
- Schedule CRUD operations
- Conflict detection system
- Department-based authorization
- Student schedule viewing endpoints
- Real-time API integration
- Responsive design
- Sample data generation

### 🔧 Configuration Files Updated:
- `apps/admin-panel/app/schedules/page.tsx` - Main schedule interface
- `apps/admin-panel/lib/admin-api.ts` - API integration
- `apps/admin-panel/app/dashboard/page.tsx` - Added schedule management link
- `api/app/routers/schedules.py` - Schedule endpoints
- `api/app/schemas/schedule.py` - Data validation schemas

## 🎯 Key Benefits

### For Department Heads:
- **Visual Interface**: Easy-to-understand timetable grid
- **Conflict Prevention**: Automatic validation prevents scheduling errors
- **Department Control**: Full control over their department's schedules
- **Real-time Updates**: Immediate feedback and updates

### For Students:
- **Clear Visibility**: Easy access to their schedules
- **Multiple Views**: Weekly timetable, today's schedule, full schedule
- **Consistent Design**: Same visual format as created by department heads

### For Administrators:
- **Centralized Management**: All schedules managed through single interface
- **Audit Trail**: All schedule changes tracked
- **Scalable Design**: Easy to extend with additional features

## 🔮 Future Enhancements

### Potential Additions:
- **Drag & Drop**: Move schedules between time slots
- **Bulk Operations**: Create multiple schedules at once
- **Templates**: Save and reuse common schedule patterns
- **Notifications**: Email alerts for schedule changes
- **Mobile App**: Native mobile interface for schedule viewing
- **Calendar Integration**: Export to Google Calendar, Outlook
- **Analytics**: Schedule utilization reports

This schedule management system provides a complete solution for university timetable management, combining the visual clarity of traditional timetables with modern web technology and comprehensive conflict prevention.