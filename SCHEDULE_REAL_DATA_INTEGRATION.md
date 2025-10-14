# Schedule Page Real Data Integration - Complete

## Summary of Changes

### Problem
The department head schedule page was using hardcoded mock data for:
- Groups (LI 02, LI 04, etc.)
- Teachers (Abdelkader MAATALLAH, etc.)
- Subjects (Développement Mobile, etc.)
- Rooms (AMPHI, Salle A1, etc.)

### Solution
Replaced all mock data with real API calls to fetch dynamic data from the backend.

## Changes Made

### 1. State Management Updates
**File**: `frontend/components/department-head/schedule-creator.tsx`

**Before** (Lines ~53-89):
```typescript
const [availableGroups] = useState(['LI 02', 'LI 04', ...]);
const [availableTeachers] = useState(['Abdelkader MAATALLAH', ...]);
const [availableSubjects] = useState(['Développement Mobile', ...]);
const [availableRooms] = useState(['AMPHI', 'Salle A1', ...]);
```

**After**:
```typescript
const [availableGroups, setAvailableGroups] = useState<string[]>([]);
const [availableTeachers, setAvailableTeachers] = useState<any[]>([]);
const [availableSubjects, setAvailableSubjects] = useState<any[]>([]);
const [availableRooms, setAvailableRooms] = useState<any[]>([]);
const [dataLoading, setDataLoading] = useState(true);
```

### 2. New Data Fetching Function
Added `loadInitialData()` function that fetches from these endpoints:
- **Groups**: `GET /department-head/timetable/groups`
- **Teachers**: `GET /department-head/timetable/teachers`
- **Subjects**: `GET /department-head/timetable/subjects`
- **Rooms**: `GET /department-head/timetable/rooms`

All endpoints require authentication via `Bearer` token from `localStorage.getItem('authToken')`.

### 3. Updated Component Lifecycle
```typescript
useEffect(() => {
  if (typeof window !== 'undefined') {
    loadInitialData(); // Load dropdown data first
  }
}, []);

useEffect(() => {
  if (typeof window !== 'undefined' && !dataLoading && selectedGroup) {
    loadSchedule(currentWeekOffset); // Then load schedule
  }
}, [currentWeekOffset, selectedGroup, dataLoading]);
```

### 4. Updated UI Components

#### Group Selector
- Now shows "Chargement..." while fetching
- Handles empty state with "Aucun groupe disponible"
- Automatically selects first group if available

#### Dialog Form Fields
All three select fields updated to use real data:

**Subjects**:
```typescript
{availableSubjects.map(subject => (
  <SelectItem key={subject.id} value={subject.nom || subject.name}>
    {subject.nom || subject.name}
  </SelectItem>
))}
```

**Teachers**:
```typescript
{availableTeachers.map(teacher => {
  const fullName = `${teacher.prenom || ''} ${teacher.nom || ''}`.trim();
  return (
    <SelectItem key={teacher.id} value={fullName}>
      {fullName}
    </SelectItem>
  );
})}
```

**Rooms**:
```typescript
{availableRooms.map(room => (
  <SelectItem key={room.id} value={room.nom || room.name}>
    {room.nom || room.name}
  </SelectItem>
))}
```

### 5. Loading States
Added proper loading states:
- Initial data loading: "Chargement des données..."
- Schedule loading: "Chargement de l'emploi du temps..."
- Dropdown loading: Shows "Chargement..." placeholder

## Backend Endpoints Used

All endpoints are in the `/department-head/timetable` router:

| Endpoint | Method | Returns | Authentication |
|----------|--------|---------|----------------|
| `/department-head/timetable/groups` | GET | List of groups | Required |
| `/department-head/timetable/teachers` | GET | List of teachers | Required |
| `/department-head/timetable/subjects` | GET | List of subjects | Required |
| `/department-head/timetable/rooms` | GET | List of rooms | Required |

## Expected Data Formats

### Groups Response
```json
[
  {
    "id": "cmgfpq...",
    "nom": "LI 04",
    "id_niveau": "..."
  }
]
```

### Teachers Response
```json
[
  {
    "id": "cmgfpq...",
    "nom": "MAATALLAH",
    "prenom": "Abdelkader",
    "email": "teacher1@university.tn"
  }
]
```

### Subjects Response
```json
[
  {
    "id": "cmgfpq...",
    "nom": "Développement Mobile",
    "code": "DEV_MOB",
    "coefficient": 3
  }
]
```

### Rooms Response
```json
[
  {
    "id": "cmgfpq...",
    "nom": "Salle A1",
    "capacite": 30,
    "type_salle": "COURS"
  }
]
```

## Testing

### Prerequisites
1. Backend server running on `http://localhost:8000`
2. User logged in as department head
3. Valid JWT token in localStorage as `authToken`

### Test Steps
1. Navigate to: `http://localhost:3000/dashboard/department-head/schedule`
2. Page should load and show "Chargement des données..."
3. After loading, dropdowns should be populated with real data
4. Click "Ajouter cours" on any empty cell
5. Verify all dropdowns show real data from database
6. Select values and save

### Expected Behavior
- Group selector shows all groups from database
- Subject dropdown shows all subjects
- Teacher dropdown shows all teachers (formatted as "Prenom Nom")
- Room dropdown shows all rooms
- Empty states show helpful messages
- Loading states prevent premature interactions

## Error Handling

The component handles errors gracefully:
- If API fails, console warnings are logged
- Empty arrays are maintained for dropdowns
- User sees "Aucun X disponible" messages
- Component doesn't crash

## Console Debugging

Check browser console for these messages:
- `Error loading groups:` - Groups API failed
- `Error loading teachers:` - Teachers API failed
- `Error loading subjects:` - Subjects API failed
- `Error loading rooms:` - Rooms API failed
- `Groups API returned XXX` - Non-200 status code

## Future Improvements

1. **Add Department Filtering**: Filter teachers/subjects by user's department
2. **Caching**: Cache loaded data to reduce API calls
3. **Refresh Button**: Allow manual data refresh
4. **Error Recovery**: Auto-retry failed requests
5. **Optimistic Updates**: Update UI before API confirms
6. **Search/Filter**: Add search in dropdowns for large datasets

## Files Modified

1. `frontend/components/department-head/schedule-creator.tsx`
   - Added dynamic data fetching
   - Updated all hardcoded arrays to state variables
   - Added loading states
   - Updated form components to use real data

## Verification

To verify the fix is working:

```javascript
// Open browser console on schedule page
console.log('Groups:', availableGroups);
console.log('Teachers:', availableTeachers);
console.log('Subjects:', availableSubjects);
console.log('Rooms:', availableRooms);
```

All should show arrays populated from the database, not hardcoded values.

---

**Status**: ✅ Complete
**Date**: 2025-10-07
**Impact**: High - Enables real schedule management with actual university data
