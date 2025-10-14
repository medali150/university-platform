# Debug Subject Filtering Issue

## Issue
Subjects not appearing in dropdown after selecting specialty in timetable creation form.

## Backend Check ✅

The backend endpoint `/department-head/timetable/subjects` at line 132-154 in `department_head_timetable.py`:

```python
subjects = await prisma.matiere.find_many(
    where={
        "specialite": {
            "id_departement": department.id
        }
    },
    include={
        "specialite": {
            "include": {"departement": True}
        },
        "enseignant": True
    },
    order=[{"nom": "asc"}]
)
```

✅ **Correctly includes** `specialite` with nested `departement`
✅ **Returns proper structure** for filtering by `subject.specialite.id`

## Frontend Check

### Data Loading (Lines 223-258)
- Uses `api.getTimetableSubjects()` which calls `/department-head/timetable/subjects`
- Stores in state: `setSubjects(subjectsRes.value as Subject[])`
- Has console logging: `console.log('📚 Subjects loaded:', subjectsRes.value.length, 'items')`

### Subject Filtering (Lines 773-782)
```tsx
const filteredSubjects = subjects.filter(subject => subject.specialite.id === formData.speciality_id)
console.log('🔍 Filtering subjects:', {
  totalSubjects: subjects.length,
  selectedSpecialityId: formData.speciality_id,
  filteredCount: filteredSubjects.length,
  subjects: subjects.map(s => ({ 
    id: s.id, 
    nom: s.nom, 
    specialiteId: s.specialite.id, 
    specialiteNom: s.specialite.nom 
  }))
})
```

✅ **Filtering logic is correct**
✅ **Console logging is present**

## Possible Issues

### 1. Data Type Mismatch
The most likely issue is that `subject.specialite.id` and `formData.speciality_id` are different types:
- One might be a **string**
- The other might be a **number**

**JavaScript strict equality (`===`) will fail if types don't match**

### 2. Data Not Loading
Subjects might not be loading at all - check browser console for:
- "📚 Subjects loaded: X items"
- "❌ Subjects loading failed:"

### 3. Empty Subjects Array
If subjects array is empty, no subjects will ever show regardless of filtering

## Solution

### Fix 1: Use Type-Safe Comparison
Change the filter to handle type differences:

```tsx
const filteredSubjects = subjects.filter(subject => 
  String(subject.specialite.id) === String(formData.speciality_id)
)
```

### Fix 2: Add Detailed Logging
The existing console.log shows all subject data including specialiteId - check browser console output.

### Fix 3: Check Data Loading
Open browser DevTools and check:
1. Network tab - is `/department-head/timetable/subjects` returning data?
2. Console tab - what does the filtering log show?
3. Are subjects loaded? (`totalSubjects: X`)
4. Are specialiteIds matching? (compare values in log)

## Next Steps

1. **Check browser console** for the filtering log output
2. **Verify subjects are loading** (totalSubjects should be > 0)
3. **Compare speciality IDs** in the log - are they same type?
4. **Apply type-safe comparison** if types don't match

## Quick Test

In browser console after selecting specialty, you should see:
```
🔍 Filtering subjects: {
  totalSubjects: 15,
  selectedSpecialityId: "abc123",
  filteredCount: 5,
  subjects: [
    { id: "...", nom: "...", specialiteId: "abc123", ... },
    ...
  ]
}
```

If `filteredCount: 0` but subjects have matching specialiteId, it's a type mismatch issue.
