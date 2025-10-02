'use client'

import { Button } from '@/components/ui/button'
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react'
import { format, addWeeks, subWeeks, startOfWeek } from 'date-fns'

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
      start: format(start, 'MMM dd'),
      end: format(end, 'MMM dd, yyyy')
    }
  }

  const weekRange = getWeekRange(currentWeek)

  return (
    <div className="flex items-center justify-between py-4">
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="icon"
          onClick={handlePreviousWeek}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        
        <Button
          variant="outline"
          size="icon"
          onClick={handleNextWeek}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
        
        <Button
          variant="outline"
          onClick={handleToday}
          className="ml-2"
        >
          <Calendar className="mr-2 h-4 w-4" />
          Today
        </Button>
      </div>

      <div className="text-lg font-semibold">
        {weekRange.start} - {weekRange.end}
      </div>
    </div>
  )
}