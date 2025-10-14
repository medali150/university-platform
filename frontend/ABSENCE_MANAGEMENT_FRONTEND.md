# Frontend Absence Management System Documentation

## 🎯 Overview
This document provides comprehensive guidance for using the absence management system in the frontend application for both teachers (enseignants) and students (étudiants).

## 📱 Frontend Components

### 1. **Teacher Absence Management** (`/dashboard/teacher/absences`)
Located at: `frontend/components/teacher/TeacherAbsenceManagement.tsx`

#### Features:
- **Create Absence**: Mark student absences during class sessions
- **View Absences**: See all absences for classes they teach
- **Delete Absences**: Remove incorrectly marked absences
- **Real-time Statistics**: Dashboard with absence counts and status breakdown

#### Usage Flow:
1. **Access**: Teachers navigate to `/dashboard/teacher/absences`
2. **Create Absence**:
   - Click "Marquer une Absence" button
   - Select the class session from dropdown
   - Choose the absent student
   - Enter reason for absence
   - Click "Créer l'Absence"
3. **Manage Absences**:
   - Search and filter absences by status
   - Click on any absence to view details
   - Delete absences if needed

### 2. **Student Absence Management** (`/dashboard/student/absences`)
Located at: `frontend/components/student/StudentAbsenceManagement.tsx`

#### Features:
- **View Personal Absences**: See all their recorded absences
- **Submit Justifications**: Provide explanations for absences
- **Upload Documents**: Attach supporting files
- **Track Status**: Monitor justification review progress
- **Statistics Dashboard**: Personal absence statistics

#### Usage Flow:
1. **Access**: Students navigate to `/dashboard/student/absences`
2. **View Absences**: See list of all recorded absences
3. **Justify Absence**:
   - Select an unjustified absence
   - Click "Justifier cette Absence"
   - Enter detailed justification text
   - Upload supporting documents (optional)
   - Submit justification
4. **Monitor Status**: Check review status and department head feedback

## 🔧 API Integration

### Frontend API Client
Location: `frontend/lib/api.ts`

#### New Absence Management Methods:
```typescript
// Get absences with filtering
api.getAbsences(query?: {
  page?: number;
  pageSize?: number;
  studentId?: string;
  teacherId?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
})

// Create new absence
api.createAbsence(data: {
  studentId: string;
  scheduleId: string;
  reason: string;
  status: string;
})

// Get student-specific absences
api.getStudentAbsences(studentId: string)

// Submit justification
api.justifyAbsence(absenceId: string, data: {
  justificationText: string;
  supportingDocuments: string[];
})

// Review absence (Department Head)
api.reviewAbsence(absenceId: string, data: {
  reviewStatus: string;
  reviewNotes: string;
})

// Delete absence
api.deleteAbsence(absenceId: string)

// Get statistics
api.getAbsenceStatistics(departmentId?: string, dateFrom?: string, dateTo?: string)
```

### Utility Functions
Location: `frontend/lib/absence-api.ts`

```typescript
AbsenceUtils.getStatusLabel(status) // Get French label for status
AbsenceUtils.getStatusColor(status) // Get CSS classes for status styling
AbsenceUtils.formatDate(dateString) // Format date to French locale
AbsenceUtils.formatTime(timeString) // Format time to HH:MM
AbsenceUtils.canJustifyAbsence(absence) // Check if absence can be justified
AbsenceUtils.canReviewAbsence(absence) // Check if absence can be reviewed
```

## 🎨 UI Components Used

### Cards and Layout:
- `Card`, `CardContent`, `CardHeader`, `CardTitle` - Main layout containers
- `Dialog`, `DialogContent` - Modal windows for forms
- `Badge` - Status indicators with color coding

### Form Elements:
- `Button` - Actions and navigation
- `Input` - Text inputs and file uploads
- `Textarea` - Multi-line text inputs
- `Select` - Dropdown selections

### Icons:
- `UserX` - Absence indicators
- `Calendar`, `Clock` - Date/time displays
- `Search` - Search functionality
- `Plus` - Create new actions
- `Check`, `X` - Approval/rejection actions
- `FileText` - Document/justification indicators

## 📊 Status Management

### Absence Status Flow:
1. **unjustified** (Initial) → Red badge, "Non justifiée"
2. **pending_review** (After justification) → Yellow badge, "En attente"
3. **approved** (Department head approval) → Green badge, "Approuvée"
4. **rejected** (Department head rejection) → Red badge, "Rejetée"
5. **justified** (System approved) → Blue badge, "Justifiée"

### Status Color Coding:
```css
unjustified: text-red-600 bg-red-100
pending_review: text-yellow-600 bg-yellow-100
justified: text-blue-600 bg-blue-100
approved: text-green-600 bg-green-100
rejected: text-red-600 bg-red-100
```

## 🔗 Navigation Integration

### Teacher Dashboard Links:
- Main dashboard includes "Gérer les Absences" quick action
- Direct link to `/dashboard/teacher/absences`

### Student Dashboard Links:
- "Mes Absences" card in quick actions
- Direct link to `/dashboard/student/absences`

## 📱 Responsive Design

### Mobile Optimizations:
- Grid layouts adapt to screen size (md:grid-cols-2, lg:grid-cols-4)
- Cards stack vertically on mobile
- Modal dialogs are full-width on small screens
- Touch-friendly button sizes

### Desktop Features:
- Side-by-side absence list and detail view
- Hover effects and transitions
- Larger statistical cards display

## 🔒 Security Features

### Role-Based Access:
- Teachers: Can only see absences for their classes
- Students: Can only see their own absences
- Authentication required via `useRequireRole` hook

### Data Validation:
- Form validation before submission
- Required field checking
- File type restrictions for uploads

## 🧪 Testing the System

### Teacher Testing Flow:
1. Login as teacher
2. Navigate to `/dashboard/teacher/absences`
3. Create absence for a student in your class
4. Verify absence appears in list
5. View absence details
6. Test deletion functionality

### Student Testing Flow:
1. Login as student
2. Navigate to `/dashboard/student/absences`
3. View personal absences
4. Submit justification for unjustified absence
5. Upload supporting documents
6. Check status updates

## 🚨 Error Handling

### Common Error Scenarios:
- **Network errors**: Toast notifications with retry suggestions
- **Validation errors**: Form field highlighting and messages
- **Authentication errors**: Automatic redirect to login
- **Permission errors**: Clear access denied messages

### User Feedback:
- Success toasts for completed actions
- Loading states during API calls
- Empty states when no data available
- Clear error messages for failed operations

## 🔄 Real-time Updates

### Notification Integration:
- Automatic page refresh after absence creation
- Status updates reflect immediately
- Statistics recalculate after changes

### Data Synchronization:
- Fetch latest data on component mount
- Refresh data after mutations
- Consistent state management

---

**Status**: ✅ **COMPLETE** - Frontend absence management system ready for use

The frontend components provide a complete, user-friendly interface for the absence management system with proper role-based access control, responsive design, and comprehensive functionality for both teachers and students.