# 🔔 Enhanced Absence Notification System

## Overview

The Enhanced Absence Notification System provides comprehensive real-time notifications for all absence-related activities between students, teachers, and administrators. The system uses multi-channel delivery (Email, In-App, Mobile Push, Web Push) to ensure critical absence information reaches the right people at the right time.

## 🏗️ System Architecture

### Core Components

1. **AbsenceNotificationService** (`enhanced_notification_service.py`)
   - Central notification orchestrator
   - Handles all absence-related notification scenarios
   - Multi-channel delivery support
   - Template-based message formatting

2. **Notification API Endpoints** (`absence_notifications.py`)
   - REST API for fetching notifications
   - Real-time notification status tracking
   - User-specific notification filtering

3. **Frontend Components**
   - `AbsenceNotifications.tsx` - Notification display component
   - `NotificationProvider.tsx` - NotificationAPI integration
   - Notifications dashboard page

### Integration Points

- **Teacher Profile Router** - Absence marking workflow
- **Simple Absences Router** - Status update workflow
- **Main Application** - Router registration and API exposure

## 📬 Notification Types

### 1. Student Absence Marked
**Trigger**: Teacher marks student absent
**Recipients**: Student
**Channels**: Email, In-App, Mobile Push

```python
await notification_service.notify_student_absence_marked(
    absence_id="abs_123",
    student_id="student_456",
    teacher_name="Prof. Smith",
    subject_name="Mathematics",
    absence_date="2024-01-15",
    motif="Late arrival"
)
```

### 2. Teacher Justification Received
**Trigger**: Student submits absence justification
**Recipients**: Teacher
**Channels**: Email, In-App

```python
await notification_service.notify_teacher_absence_justified(
    absence_id="abs_123",
    teacher_id="teacher_789",
    student_name="John Doe",
    subject_name="Mathematics",
    absence_date="2024-01-15",
    justification_text="Medical appointment"
)
```

### 3. Student Justification Reviewed
**Trigger**: Admin/Teacher reviews justification
**Recipients**: Student
**Channels**: Email, In-App, Mobile Push

```python
await notification_service.notify_student_justification_reviewed(
    absence_id="abs_123",
    student_id="student_456",
    decision="approved",  # or "rejected"
    subject_name="Mathematics",
    absence_date="2024-01-15",
    reviewer_name="Admin User"
)
```

### 4. High Absences Alert
**Trigger**: Student exceeds absence threshold
**Recipients**: Department Head, Academic Advisor
**Channels**: Email, In-App

```python
await notification_service.notify_department_head_high_absences(
    student_id="student_456",
    student_name="John Doe",
    absence_count=8,
    department_head_id="dept_head_101",
    period="current month"
)
```

### 5. Parent Alert
**Trigger**: Multiple unexcused absences
**Recipients**: Parent/Guardian
**Channels**: Email, SMS

```python
await notification_service.notify_parent_absence_alert(
    student_id="student_456",
    student_name="John Doe",
    parent_contact="parent@email.com",
    absence_count=5,
    period="this week"
)
```

### 6. Daily Absence Summary
**Trigger**: End of day cron job
**Recipients**: Department Heads, Academic Staff
**Channels**: Email

```python
await notification_service.send_daily_absence_summary(
    recipient_id="dept_head_101",
    date="2024-01-15",
    total_absences=25,
    pending_justifications=8,
    high_absence_students=["Student A", "Student B"]
)
```

## 🔧 API Endpoints

### Get Absence Notifications
```http
GET /api/notifications/absence
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "absence_123",
      "type": "absence_marked",
      "title": "Absence Marked",
      "message": "You have been marked absent for Mathematics",
      "timestamp": "2024-01-15T10:30:00Z",
      "read": false,
      "data": {
        "absence_id": "abs_123",
        "teacher_name": "Prof. Smith",
        "subject_name": "Mathematics",
        "absence_date": "2024-01-15"
      }
    }
  ],
  "unread_count": 3
}
```

### Mark Notification as Read
```http
PATCH /api/notifications/{notification_id}/read
Authorization: Bearer <token>
```

### Get Notification Summary
```http
GET /api/notifications/summary
Authorization: Bearer <token>
```

## 💻 Frontend Implementation

### Notification Component Usage
```tsx
import AbsenceNotifications from '@/components/AbsenceNotifications';

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <AbsenceNotifications />
    </div>
  );
}
```

### Notification Provider Setup
```tsx
import NotificationProvider from '@/components/NotificationProvider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <NotificationProvider>
          {children}
        </NotificationProvider>
      </body>
    </html>
  );
}
```

## 🔄 Workflow Integration

### Absence Marking Flow
1. Teacher marks student absent in teacher profile
2. `AbsenceNotificationService.notify_student_absence_marked()` called
3. Student receives real-time notification
4. Notification appears in student's dashboard
5. Email backup sent if in-app fails

### Justification Review Flow
1. Student submits justification via absence management
2. Teacher receives notification about pending review
3. Teacher/Admin updates absence status
4. `AbsenceNotificationService.notify_student_justification_reviewed()` called
5. Student receives approval/rejection notification

### High Absences Alert Flow
1. System monitors absence counts (background job)
2. Threshold exceeded triggers alert
3. Department head receives immediate notification
4. Parent notification sent if configured
5. Academic intervention process initiated

## 🛠️ Configuration

### NotificationAPI Settings
```python
NOTIFICATION_API_CLIENT_ID = "m9dp6o7vnr5t3uf2daxase81zj"
NOTIFICATION_API_SECRET = "your_secret_key"
```

### Notification Channels
- **Email**: Primary channel for formal notifications
- **In-App**: Real-time dashboard notifications
- **Mobile Push**: Critical alerts and immediate actions
- **Web Push**: Browser notifications when app is closed
- **SMS**: Emergency alerts (parent notifications)

## 🧪 Testing

### Run Notification Tests
```bash
cd api
python test_notification_system.py
```

### Test Coverage
- ✅ Student absence marking notifications
- ✅ Teacher justification notifications
- ✅ Student review notifications
- ✅ High absences alerts
- ✅ Multi-channel delivery
- ✅ Error handling and fallbacks

## 📊 Monitoring & Analytics

### Notification Metrics
- Delivery success rates by channel
- User engagement with notifications
- Response times to critical alerts
- Notification preference patterns

### Error Handling
- Graceful degradation when channels fail
- Retry logic for failed deliveries
- Logging and alerting for system issues
- Fallback to alternative channels

## 🔒 Security & Privacy

### Data Protection
- Personal information encrypted in transit
- Notification content sanitized
- User consent for notification channels
- GDPR/Privacy compliance

### Access Control
- Role-based notification permissions
- User preference management
- Opt-out mechanisms available
- Audit trail for sensitive notifications

## 🚀 Future Enhancements

### Planned Features
- **Smart Notifications**: AI-powered notification timing
- **Bulk Operations**: Mass notification management
- **Advanced Templates**: Rich media notification support
- **Integration Hub**: Connect with external systems (LMS, Parent portals)
- **Analytics Dashboard**: Comprehensive notification insights
- **Mobile App**: Native mobile notification experience

### Performance Optimizations
- **Queue System**: Asynchronous notification processing
- **Batch Processing**: Efficient bulk notifications
- **Caching Layer**: Faster notification retrieval
- **CDN Integration**: Global notification delivery

## 📞 Support & Troubleshooting

### Common Issues
1. **Notifications not received**: Check user preferences and channel settings
2. **Delayed notifications**: Verify queue processing and system load
3. **Missing data**: Ensure proper data relationships in database
4. **Template errors**: Validate notification templates and variables

### Debug Mode
Enable detailed logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Contact Support
For technical support or feature requests, contact the development team or create an issue in the project repository.

---

**Last Updated**: January 2024  
**Version**: 2.0.0  
**Maintainer**: University App Development Team