# Subject CRUD Operations Documentation

## Overview

This document describes the Subject CRUD (Create, Read, Update, Delete) operations that have been added to the university platform API. The Subject model represents academic subjects that are taught at different levels by teachers.

## Database Schema

The Subject model in the database has the following structure:

```sql
model Subject {
  id         String     @id @default(cuid())
  name       String
  levelId    String
  teacherId  String
  createdAt  DateTime   @default(now())
  updatedAt  DateTime   @updatedAt

  level      Level      @relation(fields: [levelId], references: [id], onDelete: Cascade)
  teacher    Teacher    @relation(fields: [teacherId], references: [id], onDelete: Cascade)
  schedules  Schedule[]

  @@index([levelId])
  @@index([teacherId])
}
```

## API Endpoints

All Subject CRUD endpoints are protected and require admin authentication.

### Base URL
```
http://127.0.0.1:8000/admin/subjects
```

### Authentication
All endpoints require a Bearer token with admin privileges:
```
Authorization: Bearer <admin_access_token>
```

---

## 1. Get All Subjects

**GET** `/admin/subjects/`

Retrieves a paginated list of all subjects with filtering options.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (≥ 1) |
| page_size | int | 10 | Items per page (1-100) |
| search | string | null | Search in subject name |
| level_id | string | null | Filter by level ID |
| teacher_id | string | null | Filter by teacher ID |

### Response

```json
{
  "subjects": [
    {
      "id": "clx123...",
      "name": "Mathematics",
      "levelId": "clx456...",
      "teacherId": "clx789...",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z",
      "level": {
        "id": "clx456...",
        "name": "License 1",
        "specialty": {
          "name": "Computer Science",
          "department": {
            "name": "Engineering"
          }
        }
      },
      "teacher": {
        "id": "clx789...",
        "user": {
          "firstName": "John",
          "lastName": "Doe"
        },
        "department": {
          "name": "Mathematics Department"
        }
      }
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 10,
  "totalPages": 1
}
```

### Example Usage

```bash
# Get all subjects
curl -X GET "http://127.0.0.1:8000/admin/subjects/" \
  -H "Authorization: Bearer <token>"

# Search subjects by name
curl -X GET "http://127.0.0.1:8000/admin/subjects/?search=Math" \
  -H "Authorization: Bearer <token>"

# Filter by level
curl -X GET "http://127.0.0.1:8000/admin/subjects/?level_id=clx456..." \
  -H "Authorization: Bearer <token>"
```

---

## 2. Get Subject by ID

**GET** `/admin/subjects/{subject_id}`

Retrieves detailed information about a specific subject.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| subject_id | string | Subject ID |

### Response

```json
{
  "id": "clx123...",
  "name": "Mathematics",
  "levelId": "clx456...",
  "teacherId": "clx789...",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "level": {
    "id": "clx456...",
    "name": "License 1",
    "specialty": {
      "name": "Computer Science",
      "department": {
        "name": "Engineering"
      }
    }
  },
  "teacher": {
    "id": "clx789...",
    "user": {
      "firstName": "John",
      "lastName": "Doe"
    },
    "department": {
      "name": "Mathematics Department"
    }
  },
  "schedules": [
    {
      "id": "clx999...",
      "date": "2024-01-15T00:00:00Z",
      "startTime": "2024-01-15T09:00:00Z",
      "endTime": "2024-01-15T10:30:00Z",
      "room": {
        "code": "A101"
      },
      "group": {
        "name": "Group A"
      }
    }
  ]
}
```

### Example Usage

```bash
curl -X GET "http://127.0.0.1:8000/admin/subjects/clx123..." \
  -H "Authorization: Bearer <token>"
```

---

## 3. Create Subject

**POST** `/admin/subjects/`

Creates a new subject.

### Request Body

```json
{
  "name": "Physics",
  "levelId": "clx456...",
  "teacherId": "clx789..."
}
```

### Validation Rules

- `name`: Required, 1-100 characters
- `levelId`: Required, must reference an existing level
- `teacherId`: Required, must reference an existing teacher
- Subject name must be unique within the same level

### Response

Returns the created subject with HTTP status 201.

### Example Usage

```bash
curl -X POST "http://127.0.0.1:8000/admin/subjects/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Physics",
    "levelId": "clx456...",
    "teacherId": "clx789..."
  }'
```

---

## 4. Update Subject

**PUT** `/admin/subjects/{subject_id}`

Updates an existing subject.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| subject_id | string | Subject ID |

### Request Body

```json
{
  "name": "Advanced Physics",
  "levelId": "clx456...",
  "teacherId": "clx999..."
}
```

All fields are optional. Only provided fields will be updated.

### Validation Rules

- `name`: Optional, 1-100 characters
- `levelId`: Optional, must reference an existing level
- `teacherId`: Optional, must reference an existing teacher
- If name is updated, it must be unique within the target level

### Response

Returns the updated subject.

### Example Usage

```bash
# Update only the name
curl -X PUT "http://127.0.0.1:8000/admin/subjects/clx123..." \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Advanced Mathematics"}'

# Update teacher
curl -X PUT "http://127.0.0.1:8000/admin/subjects/clx123..." \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"teacherId": "clx999..."}'
```

---

## 5. Delete Subject

**DELETE** `/admin/subjects/{subject_id}`

Deletes a subject.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| subject_id | string | Subject ID |

### Constraints

- Subject cannot be deleted if it has associated schedules
- All related schedules must be removed first

### Response

Returns HTTP status 204 (No Content) on success.

### Example Usage

```bash
curl -X DELETE "http://127.0.0.1:8000/admin/subjects/clx123..." \
  -H "Authorization: Bearer <token>"
```

---

## 6. Get Subject Schedules

**GET** `/admin/subjects/{subject_id}/schedules`

Retrieves all schedules for a specific subject.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| subject_id | string | Subject ID |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (≥ 1) |
| page_size | int | 10 | Items per page (1-100) |

### Response

```json
{
  "schedules": [
    {
      "id": "clx999...",
      "date": "2024-01-15T00:00:00Z",
      "startTime": "2024-01-15T09:00:00Z",
      "endTime": "2024-01-15T10:30:00Z",
      "status": "PLANNED",
      "room": {
        "code": "A101",
        "type": "LECTURE",
        "capacity": 50
      },
      "group": {
        "name": "Group A"
      },
      "teacher": {
        "user": {
          "firstName": "John",
          "lastName": "Doe"
        }
      },
      "absences": [
        {
          "student": {
            "user": {
              "firstName": "Jane",
              "lastName": "Smith"
            }
          },
          "status": "PENDING"
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 10,
  "totalPages": 1,
  "subject": {
    "id": "clx123...",
    "name": "Mathematics"
  }
}
```

---

## Helper Endpoints

### Get Levels for Subject Creation

**GET** `/admin/subjects/helpers/levels`

Returns all levels available for subject creation.

```json
{
  "levels": [
    {
      "id": "clx456...",
      "name": "License 1",
      "specialty": {
        "name": "Computer Science",
        "department": {
          "name": "Engineering"
        }
      }
    }
  ]
}
```

### Get Teachers for Subject Creation

**GET** `/admin/subjects/helpers/teachers`

Returns all teachers available for subject assignment.

```json
{
  "teachers": [
    {
      "id": "clx789...",
      "user": {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@university.com"
      },
      "department": {
        "name": "Mathematics Department"
      }
    }
  ]
}
```

---

## Error Handling

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "A subject with this name already exists for this level"
}
```

**401 Unauthorized**
```json
{
  "detail": "Authentication required"
}
```

**403 Forbidden**
```json
{
  "detail": "Admin access required"
}
```

**404 Not Found**
```json
{
  "detail": "Subject not found"
}
```

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## Testing

Use the provided test script to verify all CRUD operations:

```bash
cd api
python test_subject_crud.py
```

The test script will:
1. Test admin login
2. Test getting levels and teachers (helper endpoints)
3. Test getting subjects list
4. Test creating a subject
5. Test getting subject details
6. Test updating a subject
7. Test deleting a subject

---

## Integration with Frontend

The Subject CRUD operations integrate with the admin dashboard. Frontend developers should:

1. **Authentication**: Use the admin JWT token from the auth context
2. **Error Handling**: Handle all error responses appropriately
3. **Validation**: Implement client-side validation matching the API constraints
4. **Loading States**: Show loading indicators during API calls
5. **Real-time Updates**: Refresh subject lists after create/update/delete operations

### Frontend API Client Example

```javascript
// Example API client methods for Subject CRUD
export const subjectApi = {
  async getSubjects(params = {}) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${API_URL}/admin/subjects/?${query}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },

  async createSubject(data) {
    const response = await fetch(`${API_URL}/admin/subjects/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  async updateSubject(id, data) {
    const response = await fetch(`${API_URL}/admin/subjects/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  async deleteSubject(id) {
    await fetch(`${API_URL}/admin/subjects/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
};
```

---

## Conclusion

The Subject CRUD operations provide comprehensive management capabilities for academic subjects in the university platform. The API follows RESTful conventions and includes proper validation, error handling, and security measures.

For additional support or feature requests, please refer to the main API documentation or contact the development team.