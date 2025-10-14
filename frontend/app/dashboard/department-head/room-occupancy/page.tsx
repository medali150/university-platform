'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ChevronLeft, ChevronRight, Search, Building, Users } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'sonner'

const TIME_SLOTS = [
  { id: 'slot1', label: '08:10-09:50' },
  { id: 'slot2', label: '10:00-11:40' },
  { id: 'slot3', label: '11:50-13:30' },
  { id: 'slot4', label: '14:30-16:10' },
  { id: 'slot5', label: '16:10-17:50' }
]

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

export default function RoomOccupancyPage() {
  const [rooms, setRooms] = useState([])
  const [filteredRooms, setFilteredRooms] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [weekOffset, setWeekOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [roomTypeFilter, setRoomTypeFilter] = useState('all')
  const [weekInfo, setWeekInfo] = useState(null)

  useEffect(() => {
    fetchRoomData()
  }, [weekOffset])

  useEffect(() => {
    filterRooms()
  }, [rooms, searchQuery, roomTypeFilter])

  const fetchRoomData = async () => {
    setLoading(true)
    try {
      const [occupancyResponse, statsResponse] = await Promise.all([
        api.getRoomOccupancy({ week_offset: weekOffset }),
        api.getRoomOccupancyStatistics(weekOffset)
      ])

      if (occupancyResponse.success) {
        setRooms(occupancyResponse.data)
        setWeekInfo(occupancyResponse.week_info)
      }

      if (statsResponse.success) {
        setStatistics(statsResponse.statistics)
      }
    } catch (error) {
      console.error('Error fetching room data:', error)
      toast.error(error.message || 'Impossible de charger les données des salles')
    } finally {
      setLoading(false)
    }
  }

  const filterRooms = () => {
    let filtered = [...rooms]

    if (searchQuery) {
      filtered = filtered.filter(room =>
        room.roomName.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (roomTypeFilter !== 'all') {
      filtered = filtered.filter(room => room.type === roomTypeFilter)
    }

    setFilteredRooms(filtered)
  }

  const formatWeekRange = () => {
    if (!weekInfo) return ''
    const start = new Date(weekInfo.start_date)
    const end = new Date(weekInfo.end_date)
    return `${start.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })} - ${end.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}`
  }

  const getOccupancyColor = (slot) => {
    if (!slot.isOccupied) return 'bg-green-100 hover:bg-green-200 border-green-300'
    if (slot.course?.status === 'CANCELED') return 'bg-red-100 hover:bg-red-200 border-red-300'
    if (slot.course?.status === 'MAKEUP') return 'bg-yellow-100 hover:bg-yellow-200 border-yellow-300'
    return 'bg-blue-100 hover:bg-blue-200 border-blue-300'
  }

  const getStatusBadge = (status) => {
    if (!status) return null
    
    const variants = {
      PLANNED: 'default',
      CANCELED: 'destructive',
      MAKEUP: 'secondary'
    }
    
    const labels = {
      PLANNED: 'Planifié',
      CANCELED: 'Annulé',
      MAKEUP: 'Rattrapage'
    }

    return (
      <Badge variant={variants[status] || 'outline'} className="text-xs">
        {labels[status] || status}
      </Badge>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement des données...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Occupation des Salles</h1>
          <p className="text-muted-foreground mt-1">Visualisez l occupation des salles par semaine</p>
        </div>
      </div>

      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Salles Totales</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_rooms}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Créneaux Totaux</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_slots}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Créneaux Occupés</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{statistics.occupied_slots}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Créneaux Disponibles</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{statistics.available_slots}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Taux d Occupation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{statistics.occupancy_rate}%</div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setWeekOffset(weekOffset - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="px-4 py-2 bg-secondary rounded-md min-w-[250px] text-center">
                <span className="font-medium">{formatWeekRange()}</span>
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setWeekOffset(weekOffset + 1)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
              {weekOffset !== 0 && (
                <Button
                  variant="ghost"
                  onClick={() => setWeekOffset(0)}
                >
                  Aujourd hui
                </Button>
              )}
            </div>

            <div className="flex gap-2 flex-1 max-w-md">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher une salle..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={roomTypeFilter} onValueChange={setRoomTypeFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Type de salle" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les types</SelectItem>
                  <SelectItem value="LECTURE">Cours</SelectItem>
                  <SelectItem value="LAB">Laboratoire</SelectItem>
                  <SelectItem value="EXAM">Examen</SelectItem>
                  <SelectItem value="OTHER">Autre</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredRooms.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">Aucune salle trouvée avec ces filtres</p>
            </CardContent>
          </Card>
        ) : (
          filteredRooms.map((room) => (
            <Card key={room.roomId}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div>
                      <CardTitle className="text-xl">{room.roomName}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline">{room.type}</Badge>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Users className="h-3 w-3" />
                          <span>{room.capacity} places</span>
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Building className="h-3 w-3" />
                          <span>{room.building}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr>
                        <th className="border p-2 bg-muted text-left font-medium w-32">Horaire</th>
                        {DAYS.map((day) => (
                          <th key={day} className="border p-2 bg-muted text-center font-medium min-w-[140px]">
                            {day}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {TIME_SLOTS.map((slot) => (
                        <tr key={slot.id}>
                          <td className="border p-2 bg-muted font-medium text-sm">
                            {slot.label}
                          </td>
                          {DAYS.map((day) => {
                            const timeSlot = room.occupancies[day]?.[slot.id]
                            return (
                              <td key={`${day}-${slot.id}`} className="border p-1">
                                <div
                                  className={`p-2 rounded border transition-colors min-h-[60px] ${getOccupancyColor(timeSlot)}`}
                                >
                                  {timeSlot?.isOccupied && timeSlot?.course ? (
                                    <div className="text-xs space-y-1">
                                      <div className="font-semibold truncate" title={timeSlot.course.subject}>
                                        {timeSlot.course.subject}
                                      </div>
                                      <div className="text-muted-foreground truncate" title={timeSlot.course.teacher}>
                                        {timeSlot.course.teacher}
                                      </div>
                                      <div className="flex items-center justify-between gap-1">
                                        <span className="text-muted-foreground truncate" title={timeSlot.course.group}>
                                          {timeSlot.course.group}
                                        </span>
                                        {getStatusBadge(timeSlot.course.status)}
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="text-center text-xs text-muted-foreground">
                                      Disponible
                                    </div>
                                  )}
                                </div>
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
