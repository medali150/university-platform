'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Clock, User, MapPin, BookOpen, Calendar, Loader2, ChevronLeft, ChevronRight, Zap } from 'lucide-react'

interface TimeSlot {
  id: string
  start_time: string
  end_time: string
  label: string
}

interface TimetableEntry {
  id: string
  day_of_week: number // 1 = Monday, 2 = Tuesday, etc.
  time_slot: TimeSlot
  subject: {
    nom: string
    code?: string
  }
  teacher: {
    nom: string
    prenom: string
  }
  room: {
    nom: string
    type: string
  }
  group: {
    nom: string
  }
}

const DAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
const DAY_NUMBERS = [1, 2, 3, 4, 5, 6]

const TIME_SLOTS = [
  { id: '1', start_time: '08:30', end_time: '10:00', label: '8h30 à 10h00' },
  { id: '2', start_time: '10:10', end_time: '11:40', label: '10h10 à 11h40' },
  { id: '3', start_time: '11:50', end_time: '13:20', label: '11h50 à 13h20' },
  { id: '4', start_time: '14:30', end_time: '16:00', label: '14h30 à 16h00' },
  { id: '5', start_time: '16:10', end_time: '17:40', label: '16h10 à 17h40' }
]

export default function TimetablePage() {
  const { user, loading } = useAuth()
  const [timetable, setTimetable] = useState<TimetableEntry[]>([])
  const [loadingTimetable, setLoadingTimetable] = useState(true)
  const [selectedWeek, setSelectedWeek] = useState(getCurrentWeek())
  const [viewMode, setViewMode] = useState<'student' | 'teacher'>('student')

  // Get current week (you can modify this to handle different weeks)
  function getCurrentWeek() {
    const now = new Date()
    const startOfWeek = new Date(now.setDate(now.getDate() - now.getDay() + 1))
    return startOfWeek.toISOString().split('T')[0]
  }

  // Fetch timetable data
  useEffect(() => {
    const fetchTimetable = async () => {
      if (!user) return

      try {
        setLoadingTimetable(true)
        const token = localStorage.getItem('authToken')
        if (!token) return

        // Determine endpoint based on user role
        let endpoint = ''
        if (user.role === 'STUDENT') {
          endpoint = '/timetable/student'
          setViewMode('student')
        } else if (user.role === 'TEACHER') {
          endpoint = '/timetable/teacher'
          setViewMode('teacher')
        } else {
          // For admin/department head, default to teacher view
          endpoint = '/timetable/teacher'
          setViewMode('teacher')
        }

        const response = await fetch(`http://localhost:8000${endpoint}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const data = await response.json()
          setTimetable(data)
        } else {
          console.error('Failed to fetch timetable:', response.status)
          // Mock data for development
          setTimetable(getMockTimetable())
        }
      } catch (error) {
        console.error('Error fetching timetable:', error)
        setTimetable(getMockTimetable())
      } finally {
        setLoadingTimetable(false)
      }
    }

    fetchTimetable()
  }, [user])

  // Mock data for development
  function getMockTimetable(): TimetableEntry[] {
    return [
      {
        id: '1',
        day_of_week: 1, // Monday
        time_slot: TIME_SLOTS[0],
        subject: { nom: 'Algorithmique et programmation 1', code: 'ALGO1' },
        teacher: { nom: 'CHETOUI', prenom: 'Iftikhar' },
        room: { nom: 'TI 12', type: 'LAB' },
        group: { nom: 'TI 12' }
      },
      {
        id: '2',
        day_of_week: 1, // Monday
        time_slot: TIME_SLOTS[1],
        subject: { nom: 'High tech english', code: 'ENG1' },
        teacher: { nom: 'ARFAOUI', prenom: 'Dziriya' },
        room: { nom: 'DSI 23', type: 'LECTURE' },
        group: { nom: 'DSI 23' }
      },
      {
        id: '3',
        day_of_week: 2, // Tuesday
        time_slot: TIME_SLOTS[0],
        subject: { nom: 'Algorithmique et programmation 1', code: 'ALGO1' },
        teacher: { nom: 'CHETOUI', prenom: 'Iftikhar' },
        room: { nom: 'TI 11', type: 'LAB' },
        group: { nom: 'TI 11' }
      },
      {
        id: '4',
        day_of_week: 2, // Tuesday
        time_slot: TIME_SLOTS[1],
        subject: { nom: 'Mathématique Appliquée', code: 'MATH1' },
        teacher: { nom: 'BEN YOUSSEF', prenom: 'Taher' },
        room: { nom: 'TI 11', type: 'LECTURE' },
        group: { nom: 'TI 11' }
      },
      {
        id: '5',
        day_of_week: 3, // Wednesday
        time_slot: TIME_SLOTS[0],
        subject: { nom: 'Architecture des Ordinateurs', code: 'ARCH1' },
        teacher: { nom: 'RHILI', prenom: 'Rana' },
        room: { nom: 'TI 11', type: 'LECTURE' },
        group: { nom: 'TI 11' }
      }
    ]
  }

  // Get timetable entry for specific day and time slot
  function getTimetableEntry(dayNumber: number, timeSlot: TimeSlot): TimetableEntry | null {
    return timetable.find(entry => {
      // Match day and time slot by comparing start/end times
      return entry.day_of_week === dayNumber && 
             entry.time_slot.start_time === timeSlot.start_time &&
             entry.time_slot.end_time === timeSlot.end_time
    }) || null
  }

  // Render a timetable cell
  function renderTimetableCell(dayNumber: number, timeSlot: TimeSlot) {
    const entry = getTimetableEntry(dayNumber, timeSlot)
    
    if (!entry) {
      return (
        <td key={`${dayNumber}-${timeSlot.id}`} className="border border-gray-200 p-2 h-28 bg-gray-50 hover:bg-gray-100 transition-colors">
          <div className="text-center text-gray-400 text-sm h-full flex items-center justify-center">
            <span className="opacity-50">Libre</span>
          </div>
        </td>
      )
    }

    // Generate consistent color based on subject
    const colorMap: { [key: string]: string } = {
      'ALGO': 'from-blue-500 to-blue-600',
      'MATH': 'from-green-500 to-green-600',
      'ARCH': 'from-purple-500 to-purple-600',
      'ENG': 'from-orange-500 to-orange-600'
    }
    
    const subjectCode = entry.subject.code?.substring(0, 4) || 'ALGO'
    const gradientClass = colorMap[subjectCode] || 'from-indigo-500 to-indigo-600'

    return (
      <td key={`${dayNumber}-${timeSlot.id}`} className="border border-gray-200 p-2 h-28">
        <div className={`h-full bg-gradient-to-br ${gradientClass} rounded-lg p-3 text-white shadow-md hover:shadow-lg transition-all cursor-pointer group hover:scale-105 transform`}>
          <div className="flex flex-col h-full justify-between">
            <div>
              <div className="font-bold text-sm leading-tight line-clamp-2 mb-1">
                {entry.subject.nom}
              </div>
              <div className="text-xs opacity-90 flex items-center gap-0.5 mb-1">
                <User size={12} />
                {entry.teacher.prenom} {entry.teacher.nom}
              </div>
            </div>
            <div className="flex justify-between items-end text-xs opacity-90">
              <div className="flex items-center gap-0.5">
                <MapPin size={12} />
                {entry.room.nom}
              </div>
              <Badge variant="secondary" className="text-xs px-1.5 py-0.5 bg-white/20 text-white border-0">
                {entry.group.nom}
              </Badge>
            </div>
          </div>
        </div>
      </td>
    )
  }

  if (loading || loadingTimetable) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-white/60">Chargement de l'emploi du temps...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="space-y-6 p-4 sm:p-6 md:p-8">
      {/* Modern Gradient Header */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-6 sm:p-8 md:p-10 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-2">
            Emploi du Temps 📅
          </h1>
          <p className="text-indigo-100 text-base sm:text-lg">
            {viewMode === 'student' ? 'Votre emploi du temps hebdomadaire' : 'Planning des cours complet'}
          </p>
        </div>
      </div>

      {/* Week Navigation Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-lg shadow-md">
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="icon"
            className="hover:bg-indigo-50 border-indigo-200"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div className="text-center min-w-48">
            <p className="text-sm text-gray-600">Semaine du</p>
            <p className="text-lg font-bold text-gray-900">{selectedWeek}</p>
          </div>
          <Button
            variant="outline"
            size="icon"
            className="hover:bg-indigo-50 border-indigo-200"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        <Button className="bg-indigo-600 hover:bg-indigo-700 text-white">
          <Calendar className="h-4 w-4 mr-2" />
          Aujourd'hui
        </Button>
      </div>

      {/* Statistics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-blue-100 text-blue-600">
              <BookOpen className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded-full">Total</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Cours cette semaine</p>
          <p className="text-3xl font-bold text-gray-900">{timetable.length}</p>
        </div>
        
        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-green-100 text-green-600">
              <Clock className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">Temps</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Heures / semaine</p>
          <p className="text-3xl font-bold text-gray-900">{(timetable.length * 1.5).toFixed(1)}h</p>
        </div>

        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-purple-100 text-purple-600">
              <Zap className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-purple-600 bg-purple-50 px-2 py-1 rounded-full">Cours</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Matières différentes</p>
          <p className="text-3xl font-bold text-gray-900">{new Set(timetable.map(t => t.subject.nom)).size}</p>
        </div>

        <div className="group bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 border-0">
          <div className="flex items-start justify-between mb-4">
            <div className="p-3 rounded-lg bg-orange-100 text-orange-600">
              <User className="h-6 w-6" />
            </div>
            <span className="text-xs font-semibold text-orange-600 bg-orange-50 px-2 py-1 rounded-full">Profs</span>
          </div>
          <p className="text-gray-600 text-sm font-medium mb-1">Enseignants différents</p>
          <p className="text-3xl font-bold text-gray-900">{new Set(timetable.map(t => `${t.teacher.prenom} ${t.teacher.nom}`)).size}</p>
        </div>
      </div>

      {/* Timetable */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen size={20} />
            Emploi du Temps Hebdomadaire
          </CardTitle>
          <CardDescription>
            Planning fixe pour toute l'année académique
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 p-3 text-left font-semibold min-w-32">
                    Horaires
                  </th>
                  {DAYS.map(day => (
                    <th key={day} className="border border-gray-300 p-3 text-center font-semibold min-w-48">
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map(timeSlot => (
                  <tr key={timeSlot.id}>
                    <td className="border border-gray-300 p-3 bg-gray-50 font-medium text-center">
                      <div className="text-sm font-semibold text-gray-700">
                        {timeSlot.start_time}
                      </div>
                      <div className="text-sm text-gray-500">à</div>
                      <div className="text-sm font-semibold text-gray-700">
                        {timeSlot.end_time}
                      </div>
                    </td>
                    {DAY_NUMBERS.map(dayNumber => 
                      renderTimetableCell(dayNumber, timeSlot)
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Légende</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <BookOpen size={16} className="text-blue-600" />
              <span>Nom de la matière</span>
            </div>
            <div className="flex items-center gap-2">
              <User size={16} className="text-gray-600" />
              <span>Enseignant</span>
            </div>
            <div className="flex items-center gap-2">
              <MapPin size={16} className="text-gray-500" />
              <span>Salle</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}