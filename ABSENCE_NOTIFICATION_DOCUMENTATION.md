# 🔔 Absence Notification System - Complete Documentation

## Overview
The system **automatically sends notifications** to students when teachers mark them as absent in a class.

---

## How It Works

### 1️⃣ Teacher Marks Student Absent
When a teacher uses the absence management endpoint:

**Endpoint**: `POST /absences/`

**Request Body**:
```json
{
  "studentId": "student-id-here",
  "scheduleId": "schedule-id-here",
  "reason": "Optional reason",
  "status": "unjustified"
}
```

### 2️⃣ System Creates Absence Record
The system validates the request and creates an absence record in the database.

### 3️⃣ Notification Sent Automatically ✅
Immediately after creating the absence, the system:

```python
await create_notification(
    prisma=prisma,
    user_id=student.utilisateur.id,
    notification_type="ABSENCE_MARKED",
    title="Absence enregistrée",
    message=f"Vous avez été marqué absent au cours de {subject_name} le {date} à {time}",
    related_id=absence.id
)
```

**Notification Details**:
- **Type**: `ABSENCE_MARKED`
- **Title**: "Absence enregistrée" (Absence recorded)
- **Message**: Includes:
  - Subject name (e.g., "Mathématiques", "Informatique")
  - Date (format: DD/MM/YYYY)
  - Time (format: HH:MM)
- **Related ID**: Links to the absence record
- **Recipient**: The student who was marked absent

### 4️⃣ Student Receives Notification
The student can view the notification in:
- **Frontend**: `/dashboard/notifications` page
- **Bell Icon**: Shows unread count
- **API**: `GET /notifications/` endpoint

---

## API Endpoints

### For Teachers (Mark Absence)
```http
POST /absences/
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "studentId": "clxxx...",
  "scheduleId": "clyyy...",
  "reason": "Non présent",
  "status": "unjustified"
}
```

**Response**:
```json
{
  "message": "Absence créée avec succès",
  "id": "absence-id",
  "notification_sent": true
}
```

### For Students (View Notifications)
```http
GET /notifications/
Authorization: Bearer <student_token>
```

**Response**:
```json
[
  {
    "id": "notif-id",
    "userId": "student-id",
    "type": "ABSENCE_MARKED",
    "title": "Absence enregistrée",
    "message": "Vous avez été marqué absent au cours de Mathématiques le 10/10/2025 à 08:00",
    "relatedId": "absence-id",
    "isRead": false,
    "createdAt": "2025-10-10T08:05:00.000Z"
  }
]
```

### Get Notification Stats
```http
GET /notifications/stats
Authorization: Bearer <student_token>
```

**Response**:
```json
{
  "total": 5,
  "unread": 2
}
```

---

## Code Implementation

### Location: `api/app/routers/absence_management.py`

**Lines 121-135**:
```python
# Send notification to student about absence
try:
    await create_notification(
        prisma=prisma,
        user_id=student.utilisateur.id,
        notification_type="ABSENCE_MARKED",
        title="Absence enregistrée",
        message=f"Vous avez été marqué absent au cours de {schedule.matiere.nom} le {schedule.date.strftime('%d/%m/%Y')} à {schedule.heure_debut.strftime('%H:%M')}",
        related_id=absence.id
    )
    logger.info(f"✅ Notification sent to student {student.utilisateur.email} for absence {absence.id}")
except Exception as e:
    logger.error(f"❌ Failed to send notification: {e}")
```

### Notification Helper Function
**Location**: `api/app/routers/notifications.py` (Lines 35-63)

```python
async def create_notification(
    prisma: Prisma,
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    related_id: str = None
) -> dict:
    """Create a notification for a user"""
    notification = await prisma.notification.create(
        data={
            "userId": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "relatedId": related_id,
            "isRead": False,
            "createdAt": datetime.now()
        }
    )
    
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message
    }
```

---

## Frontend Integration

### Notification Page
**Location**: `frontend/app/dashboard/notifications/page.tsx`

**Features**:
- 📬 Display all notifications
- 🔔 Show unread count in bell icon
- ✅ Mark as read functionality
- 🗑️ Delete notifications
- 🔗 Link to related absence record

### Bell Icon Badge
The bell icon automatically updates with unread count:
```typescript
const stats = await api.getNotificationStats()
// Shows: { total: 10, unread: 3 }
// Badge displays: 3
```

---

## Testing the System

### Method 1: Use the Test Script
```bash
cd api
python test_absence_notification.py
```

This will show:
- Total notifications in system
- Number of absence notifications
- Recent absence notifications with details

### Method 2: Manual Test
1. **Login as Teacher**:
   ```http
   POST /auth/login
   {
     "email": "teacher@university.tn",
     "password": "password"
   }
   ```

2. **Mark Student Absent**:
   ```http
   POST /absences/
   {
     "studentId": "student-id",
     "scheduleId": "schedule-id",
     "reason": "Non présent",
     "status": "unjustified"
   }
   ```

3. **Login as Student**:
   ```http
   POST /auth/login
   {
     "email": "student@university.tn",
     "password": "password"
   }
   ```

4. **Check Notifications**:
   ```http
   GET /notifications/
   ```
   
   You should see the absence notification!

### Method 3: Frontend Test
1. Login as teacher: `http://localhost:3001/login`
2. Navigate to absence management
3. Mark a student absent
4. Logout and login as that student
5. Click the bell icon 🔔
6. See the absence notification!

---

## Database Schema

### Notification Table
```prisma
model Notification {
  id          String   @id @default(cuid())
  userId      String   @map("user_id")
  type        String   // "ABSENCE_MARKED"
  title       String   // "Absence enregistrée"
  message     String   // Full details
  relatedId   String?  @map("related_id") // Links to absence
  isRead      Boolean  @default(false) @map("is_read")
  createdAt   DateTime @default(now()) @map("created_at")
  
  user Utilisateur @relation("UserNotifications", ...)
  
  @@map("notifications")
}
```

### Absence Table
```prisma
model Absence {
  id                   String   @id @default(cuid())
  id_etudiant          String
  id_emploitemps       String
  motif                String?
  statut               AbsenceStatus
  createdAt            DateTime
  
  etudiant    Etudiant    @relation(...)
  emploitemps EmploiTemps @relation(...)
}
```

---

## Notification Types

The system supports multiple notification types:

| Type | Description | Recipient |
|------|-------------|-----------|
| `ABSENCE_MARKED` | Student marked absent | Student |
| `SCHEDULE_CREATED` | New schedule added | Teacher |
| `SCHEDULE_UPDATED` | Schedule modified | Teacher |
| `SCHEDULE_DELETED` | Schedule removed | Teacher |

---

## Error Handling

The notification system is **non-blocking**:
- If notification fails, the absence is still created
- Errors are logged but don't stop the process
- Teacher still gets success response

```python
try:
    await create_notification(...)
    logger.info("✅ Notification sent")
except Exception as e:
    logger.error(f"❌ Failed to send notification: {e}")
    # Absence creation continues regardless
```

---

## Logs

When an absence is created with notification, you'll see in the server logs:

```
✅ Notification sent to student student@university.tn for absence clxxx123
```

If it fails:
```
❌ Failed to send notification: <error details>
```

---

## Future Enhancements (Optional)

### 1. High Absence Alert
Send notification to department head when student has too many absences:
```python
if student_absence_count > 3:
    await create_notification(
        prisma=prisma,
        user_id=dept_head.utilisateur.id,
        notification_type="HIGH_ABSENCE_ALERT",
        title="Alerte: Trop d'absences",
        message=f"L'étudiant {student_name} a {count} absences",
        related_id=student.id
    )
```

### 2. Justification Submitted
Notify department head when student submits justification:
```python
await create_notification(
    prisma=prisma,
    user_id=dept_head_user_id,
    notification_type="JUSTIFICATION_SUBMITTED",
    title="Justification soumise",
    message=f"L'étudiant {student_name} a soumis une justification",
    related_id=absence.id
)
```

### 3. Absence Review Result
Notify student of justification review result:
```python
await create_notification(
    prisma=prisma,
    user_id=student.utilisateur.id,
    notification_type="ABSENCE_REVIEWED",
    title="Justification traitée",
    message=f"Votre justification a été {status}",
    related_id=absence.id
)
```

---

## Status: ✅ FULLY OPERATIONAL

The absence notification system is **already implemented and working**!

- ✅ Backend: Notification sent when absence created
- ✅ Database: Notifications stored correctly
- ✅ Frontend: Notification page displays alerts
- ✅ API: All endpoints functional
- ✅ Real-time: Unread badge updates automatically

**No additional configuration needed - it works out of the box!**

---

## Support

If you encounter issues:
1. Check server logs for notification errors
2. Run `python test_absence_notification.py` to verify
3. Check database: `SELECT * FROM notifications WHERE type = 'ABSENCE_MARKED'`
4. Verify student user ID matches notification userId

---

**Last Updated**: October 10, 2025  
**Version**: 1.0  
**Status**: Production Ready ✅
