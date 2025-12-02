'use client'

import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight, Calendar, Clock } from 'lucide-react'
import { format, addWeeks, subWeeks, startOfWeek, isToday } from 'date-fns'
import { fr } from 'date-fns/locale'

interface WeekNavigatorProps {
  currentWeek: Date
  onWeekChange: (week: Date) => void
}

export function WeekNavigator({ currentWeek, onWeekChange }: WeekNavigatorProps) {
  const handlePreviousWeek = () => {
    const previousWeek = subWeeks(currentWeek, 1)
    onWeekChange(startOfWeek(previousWeek, { weekStartsOn: 1 }))
  }

  const handleNextWeek = () => {
    const nextWeek = addWeeks(currentWeek, 1)
    onWeekChange(startOfWeek(nextWeek, { weekStartsOn: 1 }))
  }

  const handleToday = () => {
    const today = new Date()
    onWeekChange(startOfWeek(today, { weekStartsOn: 1 }))
  }

  const getWeekRange = (date: Date) => {
    const start = startOfWeek(date, { weekStartsOn: 1 })
    const end = addWeeks(start, 1)
    return {
      start: format(start, 'dd MMM', { locale: fr }),
      end: format(end, 'dd MMM yyyy', { locale: fr }),
      startDate: start
    }
  }

  const weekRange = getWeekRange(currentWeek)
  const isCurrentWeek = isToday(currentWeek)

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-gradient-to-r from-slate-50 to-indigo-50 rounded-lg border border-indigo-100 mb-4">
      <div className="flex items-center gap-2">
        <button
          onClick={handlePreviousWeek}
          className="p-2 hover:bg-indigo-100 rounded-lg transition-all duration-200 text-gray-600 hover:text-indigo-600 hover:shadow-md"
          title="Semaine précédente"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        
        <button
          onClick={handleNextWeek}
          className="p-2 hover:bg-indigo-100 rounded-lg transition-all duration-200 text-gray-600 hover:text-indigo-600 hover:shadow-md"
          title="Semaine suivante"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
        
        <button
          onClick={handleToday}
          className={`ml-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
            isCurrentWeek
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg hover:shadow-xl'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-indigo-50 hover:border-indigo-300'
          }`}
          title="Semaine actuelle"
        >
          <Calendar className="h-4 w-4" />
          Aujourd'hui
        </button>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-gray-600">
          <Clock className="h-4 w-4 text-indigo-600" />
          <span className="text-sm font-semibold text-gray-900">
            {weekRange.start} - {weekRange.end}
          </span>
        </div>
      </div>
    </div>
  )
}