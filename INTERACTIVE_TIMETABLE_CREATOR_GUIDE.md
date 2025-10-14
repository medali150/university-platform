# Interactive Timetable Creator - Documentation 📅

## Overview

A visual, interactive timetable grid (like the photo you shared) where the department head can click on any time slot to create semester-long courses.

## Component

**File**: `frontend/components/department-head/interactive-timetable-creator.tsx`

## Features ✨

### 1. **Visual Grid Layout**
- Days as columns: Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi
- Time slots as rows: 8h30-10h00, 10h10-11h40, 11h50-13h20, 14h30-16h00, 16h10-17h40
- Exactly like the university timetable in your photo!

### 2. **Interactive Cells**
- **Empty cells**: Show "+" icon and "Cliquer pour ajouter"
- **Filled cells**: Show course details with colored background
  - Course name (Matière)
  - Room (📍 Salle)
  - Teacher (👨‍🏫 Enseignant)
  - Group (👥 Groupe)

### 3. **Click to Create**
- Click any cell → Dialog opens
- Fill in: Matière, Enseignant, Salle, Récurrence
- Click "Créer le Cours" → Creates sessions for entire semester!

### 4. **Group Selection**
- Select which group to create schedule for
- Switch between groups instantly
- Each group has its own timetable

### 5. **Week Navigation**
- Navigate weeks with ← → buttons
- "Aujourd'hui" button to jump to current week
- Refresh button to reload schedule

## How to Use 🎯

### Step 1: Select a Group
```
At the top: Select "LI 04" or any group from dropdown
```

### Step 2: Click on a Time Slot
```
Click on "Lundi 8h30-10h00" (for example)
A dialog will open
```

### Step 3: Fill in Details
```
Matière: Select "Développement Mobile"
Enseignant: Select "Abdelkader MAATALLAH"
Salle: Select "LI 02"
Récurrence: "Chaque Semaine"
Dates: 2025-09-01 to 2025-12-31
```

### Step 4: Create
```
Click "Créer le Cours"
→ Creates 15+ sessions automatically
→ Updates student timetable immediately
→ Updates teacher schedule automatically
```

## Visual Example

```
┌─────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│         │    Lundi     │    Mardi     │   Mercredi   │    Jeudi     │  Vendredi    │   Samedi     │
├─────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 8h30 à  │ Développement│ Environnement│   Atelier    │   Atelier    │              │              │
│ 10h00   │    Mobile    │      de      │ développement│  Framework   │              │              │
│         │  Abdelkader  │ développement│ Mobile natif │cross-platform│              │              │
│         │ MAATALLAH    │              │              │              │              │              │
│         │   LI 02      │              │              │              │              │              │
├─────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 10h10 à │   Web 3.0    │     [+]      │     [+]      │Wahid HAMDI   │              │              │
│ 11h40   │    Ahmed     │  Click to    │  Click to    │   LI 04      │              │              │
│         │  NEFZAOUI    │     add      │     add      │              │              │              │
│         │   SI 10      │              │              │              │              │              │
├─────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│  ...    │              │              │              │              │              │              │
└─────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

## Cell States

### Empty Cell
```tsx
┌──────────────────┐
│                  │
│       [+]        │
│  Cliquer pour    │
│     ajouter      │
│                  │
└──────────────────┘
```
- Gray text, hover shows yellow background
- Shows plus icon

### Filled Cell
```tsx
┌──────────────────┐
│ Développement    │
│    Mobile        │
│ 📍 LI 02         │
│ 👨‍🏫 Abdelkader   │
│    MAATALLAH     │
│ 👥 LI 04         │
└──────────────────┘
```
- Blue gradient background
- White text
- Icons for visual clarity

## Dialog Form

When you click a cell, this dialog opens:

```
╔════════════════════════════════════════╗
║        Créer un Cours                  ║
║  Lundi - 8h30 à 10h00                 ║
╠════════════════════════════════════════╣
║                                        ║
║  Matière *                            ║
║  [Développement Mobile ▼]             ║
║                                        ║
║  Enseignant *                         ║
║  [Abdelkader MAATALLAH ▼]             ║
║                                        ║
║  Salle *                              ║
║  [LI 02 (Amphi) - 40 places ▼]       ║
║                                        ║
║  Groupe                               ║
║  [LI 04] (read-only)                  ║
║                                        ║
║  Récurrence *                         ║
║  [Chaque Semaine ▼]                   ║
║                                        ║
║  Début Semestre    Fin Semestre       ║
║  [2025-09-01]      [2025-12-31]       ║
║                                        ║
║         [Annuler]  [Créer le Cours]   ║
╚════════════════════════════════════════╝
```

## API Integration

### 1. Load Resources
```typescript
const resources = await TimetableAPI.getAvailableResources();
// Returns: { matieres, groupes, enseignants, salles }
```

### 2. Create Session
```typescript
const result = await TimetableAPI.createSemesterSchedule({
  matiere_id: "...",
  groupe_id: "...",
  enseignant_id: "...",
  salle_id: "...",
  day_of_week: DayOfWeek.MONDAY,
  start_time: "08:30",
  end_time: "10:00",
  recurrence_type: RecurrenceType.WEEKLY,
  semester_start: "2025-09-01",
  semester_end: "2025-12-31"
});
// Returns: { success, created_count, conflicts }
```

### 3. Load Week Schedule (for display)
```typescript
// Future: Load existing sessions to show in grid
const schedule = await TimetableAPI.getDepartmentSemesterSchedule(
  "2025-09-01",
  "2025-12-31"
);
```

## Color Coding

- **Empty cells**: White background, gray text
- **Hover (empty)**: Yellow tint
- **Filled cells**: Blue gradient (from-blue-500 to-blue-600)
- **Hover (filled)**: Lighter blue
- **Header**: Gray background (bg-gray-100)
- **Time column**: Light gray (bg-gray-50)

## Responsive Design

- **Desktop**: Full grid visible
- **Tablet**: Horizontal scroll for grid
- **Mobile**: Horizontal scroll, compact view

## Usage in App

### Import:
```tsx
import InteractiveTimetableCreator from '@/components/department-head/interactive-timetable-creator';
```

### Use in page:
```tsx
<InteractiveTimetableCreator />
```

### Full page example:
```tsx
// app/dashboard/department-head/timetable/page.tsx
export default function TimetablePage() {
  return (
    <div className="container mx-auto p-6">
      <InteractiveTimetableCreator />
    </div>
  );
}
```

## Key Differences from Old System

| Feature | Old System | New System |
|---------|-----------|------------|
| Creation | Form-based | Visual grid + click |
| View | List of sessions | Weekly timetable grid |
| Time slots | Manual input | Pre-defined slots |
| Days | Dropdown | Visual columns |
| Sessions created | 1 per request | 15+ per request |
| UX | Text-heavy | Visual, colorful |
| Navigation | None | Week navigation |

## Benefits

1. **Visual**: See the whole week at once
2. **Intuitive**: Click where you want to add
3. **Fast**: One click opens dialog
4. **Clear**: Color-coded cells
5. **Efficient**: Creates entire semester
6. **Familiar**: Matches traditional timetable layout

## Tips

- **Empty schedule**: Shows many "+" cells
- **Full schedule**: Colorful grid with course cards
- **Conflicts**: System checks automatically
- **Recurrence**: Choose weekly or biweekly
- **Auto-update**: Teacher & student schedules update instantly

## Troubleshooting

**Issue**: Cells not clickable
- **Fix**: Ensure group is selected first

**Issue**: Dialog doesn't open
- **Fix**: Check console for errors

**Issue**: Sessions not showing
- **Fix**: Click refresh button or navigate weeks

**Issue**: Can't create session
- **Fix**: Fill all required fields (marked with *)

## Future Enhancements

1. **Edit existing sessions**: Click filled cell to edit
2. **Delete sessions**: Right-click or trash icon
3. **Drag & drop**: Move sessions between slots
4. **Copy week**: Duplicate schedule to another week
5. **Templates**: Save and load common schedules
6. **Conflict warnings**: Visual indicators in grid
7. **Multi-select**: Create multiple sessions at once

---

**This is the modern, visual way to create timetables - exactly like your photo!** 🎉✨
