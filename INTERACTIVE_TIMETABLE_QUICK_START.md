# Interactive Timetable Creator - Quick Start 🚀

## What We Built

An **interactive visual timetable grid** where department heads can click on any cell to create courses - exactly like your university photo!

## The Visual Grid

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            Créer l'Emploi du Temps                                      │
│                  Cliquez sur une case pour créer un cours récurrent                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  Groupe: [LI 04 - L2 (DSI) ▼]     Semaine: [← 7 oct - 13 oct →]    [Aujourd'hui] [↻]  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────┬──────────────────┬──────────────────┬──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│         │      Lundi       │      Mardi       │     Mercredi     │      Jeudi       │     Vendredi     │      Samedi      │
├─────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│  8h30   │ ┌──────────────┐ │ ┌──────────────┐ │ ┌──────────────┐ │ ┌──────────────┐ │                  │                  │
│   à     │ │Développement │ │ │Environnement │ │ │   Atelier    │ │ │   Atelier    │ │                  │                  │
│ 10h00   │ │   Mobile     │ │ │      de      │ │ │développement │ │ │  Framework   │ │                  │                  │
│         │ │              │ │ │développement │ │ │Mobile natif  │ │ │cross-platform│ │                  │                  │
│         │ │📍 LI 02      │ │ │              │ │ │              │ │ │              │ │     [VIDE]       │     [VIDE]       │
│         │ │👨‍🏫 Abdelkader│ │ │              │ │ │              │ │ │              │ │                  │                  │
│         │ │  MAATALLAH   │ │ │              │ │ │              │ │ │              │ │      [+]         │      [+]         │
│         │ │👥 LI 04      │ │ │              │ │ │              │ │ │              │ │  Cliquer pour    │  Cliquer pour    │
│         │ └──────────────┘ │ └──────────────┘ │ └──────────────┘ │ └──────────────┘ │     ajouter      │     ajouter      │
├─────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 10h10   │ ┌──────────────┐ │                  │                  │ ┌──────────────┐ │                  │                  │
│   à     │ │   Web 3.0    │ │                  │                  │ │ Wahid HAMDI  │ │                  │                  │
│ 11h40   │ │              │ │                  │                  │ │              │ │                  │                  │
│         │ │📍 SI 10      │ │      [+]         │      [+]         │ │📍 LI 04      │ │      [+]         │      [+]         │
│         │ │👨‍🏫 Ahmed    │ │  Cliquer pour    │  Cliquer pour    │ │👥 LI 04      │ │  Cliquer pour    │  Cliquer pour    │
│         │ │  NEFZAOUI    │ │     ajouter      │     ajouter      │ │              │ │     ajouter      │     ajouter      │
│         │ │👥 LI 04      │ │                  │                  │ │              │ │                  │                  │
│         │ └──────────────┘ │                  │                  │ └──────────────┘ │                  │                  │
├─────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 11h50   │                  │                  │                  │                  │                  │                  │
│   à     │                  │                  │                  │                  │                  │                  │
│ 13h20   │      [+]         │      [+]         │      [+]         │      [+]         │      [+]         │      [+]         │
│         │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │
│         │     ajouter      │     ajouter      │     ajouter      │     ajouter      │     ajouter      │     ajouter      │
├─────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 14h30   │                  │                  │                  │                  │                  │                  │
│   à     │                  │                  │                  │                  │                  │                  │
│ 16h00   │      [+]         │      [+]         │      [+]         │      [+]         │      [+]         │      [+]         │
│         │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │
│         │     ajouter      │     ajouter      │     ajouter      │     ajouter      │     ajouter      │     ajouter      │
├─────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 16h10   │                  │                  │                  │                  │                  │                  │
│   à     │                  │                  │                  │                  │                  │                  │
│ 17h40   │      [+]         │      [+]         │      [+]         │      [+]         │      [+]         │      [+]         │
│         │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │  Cliquer pour    │
│         │     ajouter      │     ajouter      │     ajouter      │     ajouter      │     ajouter      │     ajouter      │
└─────────┴──────────────────┴──────────────────┴──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

## How It Works

### Step 1: Click on Empty Cell
```
You click on: [Mercredi 14h30-16h00]
          ↓
Dialog opens instantly
```

### Step 2: Fill the Form
```
╔════════════════════════════════╗
║      Créer un Cours            ║
║  Mercredi - 14h30 à 16h00      ║
╠════════════════════════════════╣
║ Matière: [SOA ▼]               ║
║ Enseignant: [Abdelkader ▼]     ║
║ Salle: [LI 05 ▼]               ║
║ Groupe: LI 04 (read-only)      ║
║ Récurrence: [Chaque Semaine ▼] ║
║ Dates: [01/09] → [31/12]       ║
║                                ║
║      [Annuler] [Créer]         ║
╚════════════════════════════════╝
```

### Step 3: Result
```
✅ 15 sessions créées!

The cell now shows:
┌──────────────┐
│     SOA      │
│              │
│ 📍 LI 05     │
│ 👨‍🏫 Abdelkader│
│   MAATALLAH  │
│ 👥 LI 04     │
└──────────────┘
```

## File Location

```
frontend/components/department-head/interactive-timetable-creator.tsx
```

## Usage

```tsx
import InteractiveTimetableCreator from '@/components/department-head/interactive-timetable-creator';

// In your page:
<InteractiveTimetableCreator />
```

## Features ✨

✅ **Visual grid layout** - See the whole week at once
✅ **Click to create** - Click any cell to add a course
✅ **Beautiful UI** - Blue gradient cards for filled cells
✅ **Icons** - 📍 for room, 👨‍🏫 for teacher, 👥 for group
✅ **Group selector** - Switch between different groups
✅ **Week navigation** - Navigate through weeks
✅ **Semester creation** - One click creates 15+ sessions
✅ **Responsive** - Works on desktop, tablet, mobile

## What Happens When You Create

1. **Click cell** → Opens dialog
2. **Fill form** → Select matière, enseignant, salle
3. **Click "Créer"** → API call to backend
4. **Backend creates** → 15 sessions for the semester
5. **Grid updates** → Cell shows the new course
6. **Students see** → Course appears in student timetable
7. **Teachers see** → Course appears in teacher timetable (auto-generated)

## Color Scheme

- **Empty cells**: White background, gray text, yellow on hover
- **Filled cells**: Blue gradient (blue-500 → blue-600), white text
- **Headers**: Gray background (gray-100)
- **Time column**: Light gray (gray-50)
- **Success alerts**: Green (green-50 background)
- **Error alerts**: Red (destructive variant)

## Time Slots (Fixed)

1. **8h30 à 10h00** (1h30)
2. **10h10 à 11h40** (1h30)
3. **11h50 à 13h20** (1h30)
4. **14h30 à 16h00** (1h30)
5. **16h10 à 17h40** (1h30)

These match your university's schedule exactly!

## Days (Fixed)

1. **Lundi** (Monday)
2. **Mardi** (Tuesday)
3. **Mercredi** (Wednesday)
4. **Jeudi** (Thursday)
5. **Vendredi** (Friday)
6. **Samedi** (Saturday)

## Quick Test

1. **Open the page** with the component
2. **Select a group** (e.g., "LI 04")
3. **Click on "Lundi 8h30-10h00"**
4. **Fill in**:
   - Matière: "Développement Mobile"
   - Enseignant: "Abdelkader MAATALLAH"
   - Salle: "LI 02"
5. **Click "Créer le Cours"**
6. **See result**: Cell turns blue with course info!

## Comparison

| Old System | New System |
|------------|------------|
| Form with dropdowns | Visual grid |
| Text-based | Colorful cards |
| Manual day/time input | Click on cell |
| List view | Weekly grid |
| Not visual | Very visual |
| Hard to see schedule | See whole week |

## This Is Exactly What You Asked For! 🎉

- ✅ Visual timetable grid like the photo
- ✅ Days as columns
- ✅ Times as rows
- ✅ Click on cell to create
- ✅ Dialog with course details
- ✅ Creates for entire semester
- ✅ Beautiful modern UI

**Just import and use it in your department head dashboard!** 🚀
