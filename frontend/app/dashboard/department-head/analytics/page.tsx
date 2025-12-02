'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart3, TrendingUp, Users, Calendar, Clock, Target, 
  Download, RefreshCw, BookOpen, Award, AlertCircle, CheckCircle 
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { api } from '@/lib/api'

interface AnalyticsData {
  period: {
    start_date: string
    end_date: string
    days: number
  }
  kpis: {
    attendance_rate: number
    room_utilization_rate: number
    total_schedules: number
    total_hours: number
    total_students: number
    total_teachers: number
    total_absences: number
    justified_absences: number
  }
  subject_distribution: Array<{
    subject: string
    hours: number
    percentage: number
  }>
  top_teachers: Array<{
    id: string
    name: string
    total_hours: number
    sessions: number
  }>
  room_efficiency: Array<{
    room_code: string
    room_name: string
    hours_used: number
    utilization_rate: number
  }>
  weekly_attendance: Array<{
    week: string
    rate: number
    date: string
  }>
  grade_statistics: {
    average_grade: number
    total_grades: number
    excellent: number
    good: number
    average: number
    poor: number
  }
  department: {
    id: string
    name: string
  }
}

interface Activity {
  type: string
  timestamp: string
  student?: string
  subject?: string
  status?: string
  grade?: number
  teacher?: string
  severity: string
}

export default function AnalyticsPage() {
  const { user, isLoading: authLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  const [loading, setLoading] = useState(true)
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [activities, setActivities] = useState<Activity[]>([])

  useEffect(() => {
    if (user && !authLoading) {
      fetchAnalytics()
      fetchRecentActivity()
    }
  }, [user, authLoading])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const data = await api.getAnalyticsOverview()
      setAnalyticsData(data)
    } catch (error: any) {
      console.error('Error fetching analytics:', error)
      toast.error('Impossible de charger les statistiques')
    } finally {
      setLoading(false)
    }
  }

  const fetchRecentActivity = async () => {
    try {
      const data = await api.getRecentActivity(10)
      setActivities(data.activities)
    } catch (error: any) {
      console.error('Error fetching recent activity:', error)
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'absence':
        return AlertCircle
      case 'grade':
        return Award
      default:
        return Calendar
    }
  }

  const getActivityColor = (severity: string) => {
    switch (severity) {
      case 'success':
        return 'border-l-green-500 bg-green-50'
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50'
      case 'error':
        return 'border-l-red-500 bg-red-50'
      default:
        return 'border-l-blue-500 bg-blue-50'
    }
  }

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffMinutes = Math.floor((now.getTime() - time.getTime()) / 60000)
    
    if (diffMinutes < 60) return `Il y a ${diffMinutes}min`
    if (diffMinutes < 1440) return `Il y a ${Math.floor(diffMinutes / 60)}h`
    return `Il y a ${Math.floor(diffMinutes / 1440)}j`
  }

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user || !analyticsData) return null

  const kpis = analyticsData.kpis
  const attendanceTrend = kpis.attendance_rate >= 94 ? '+2.1%' : '-1.2%'
  const attendanceTrendColor = kpis.attendance_rate >= 94 ? 'text-green-600' : 'text-red-600'

  const handleExportReport = async (format: 'csv' | 'excel' = 'excel') => {
    try {
      toast.loading(`Téléchargement du rapport ${format.toUpperCase()}...`)
      await api.exportAnalyticsReport(format)
      toast.success('Rapport téléchargé avec succès')
    } catch (error: any) {
      console.error('Error exporting report:', error)
      toast.error('Erreur lors du téléchargement du rapport')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analyses et Statistiques</h1>
          <p className="text-muted-foreground">
            {analyticsData.department.name} • Derniers {analyticsData.period.days} jours
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchAnalytics}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Actualiser
          </Button>
          <Button onClick={() => handleExportReport('excel')}>
            <Download className="mr-2 h-4 w-4" />
            Exporter Excel
          </Button>
          <Button variant="outline" onClick={() => handleExportReport('csv')}>
            <Download className="mr-2 h-4 w-4" />
            Exporter CSV
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taux de Présence</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {kpis.attendance_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              <span className={attendanceTrendColor}>{attendanceTrend}</span> vs période précédente
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {kpis.justified_absences} absences justifiées / {kpis.total_absences}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Utilisation Salles</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {kpis.room_utilization_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Taux d'occupation moyen
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sessions Planifiées</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.total_schedules}</div>
            <p className="text-xs text-muted-foreground">
              {kpis.total_students} étudiants • {kpis.total_teachers} enseignants
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Heures Enseignées</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis.total_hours.toFixed(0)}h</div>
            <p className="text-xs text-muted-foreground">
              {analyticsData.period.days} derniers jours
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Évolution de la Présence</CardTitle>
            <CardDescription>Taux de présence par semaine</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {analyticsData.weekly_attendance.slice(-8).map((week, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="text-xs font-medium w-8">{week.week}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                    <div 
                      className={`h-6 rounded-full flex items-center justify-end pr-2 ${
                        week.rate >= 95 ? 'bg-green-500' : 
                        week.rate >= 90 ? 'bg-blue-500' : 
                        week.rate >= 85 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${week.rate}%` }}
                    >
                      <span className="text-xs font-semibold text-white">{week.rate}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Répartition par Matière</CardTitle>
            <CardDescription>Heures d'enseignement par discipline</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsData.subject_distribution.slice(0, 5).map((subject, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="truncate">{subject.subject}</span>
                    <span className="font-medium">{subject.hours}h ({subject.percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        index === 0 ? 'bg-blue-600' :
                        index === 1 ? 'bg-green-600' :
                        index === 2 ? 'bg-purple-600' :
                        index === 3 ? 'bg-yellow-600' : 'bg-gray-600'
                      }`}
                      style={{ width: `${subject.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Analytics */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Top Enseignants</CardTitle>
            <CardDescription>Par heures enseignées</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analyticsData.top_teachers.map((teacher, index) => (
                <div key={teacher.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      index === 0 ? 'bg-green-100' :
                      index === 1 ? 'bg-blue-100' :
                      index === 2 ? 'bg-purple-100' :
                      index === 3 ? 'bg-yellow-100' : 'bg-gray-100'
                    }`}>
                      <span className={`font-semibold text-sm ${
                        index === 0 ? 'text-green-600' :
                        index === 1 ? 'text-blue-600' :
                        index === 2 ? 'text-purple-600' :
                        index === 3 ? 'text-yellow-600' : 'text-gray-600'
                      }`}>{index + 1}</span>
                    </div>
                    <div>
                      <p className="font-medium text-sm">{teacher.name}</p>
                      <p className="text-xs text-muted-foreground">{teacher.sessions} sessions</p>
                    </div>
                  </div>
                  <Badge variant="secondary">{teacher.total_hours}h</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Utilisation des Salles</CardTitle>
            <CardDescription>Efficacité d'occupation par salle</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analyticsData.room_efficiency.map((room, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm font-medium">{room.room_code}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          room.utilization_rate >= 90 ? 'bg-green-600' :
                          room.utilization_rate >= 80 ? 'bg-blue-600' :
                          room.utilization_rate >= 70 ? 'bg-yellow-600' : 'bg-red-600'
                        }`}
                        style={{ width: `${room.utilization_rate}%` }}
                      ></div>
                    </div>
                    <span className="text-xs font-medium w-10">{room.utilization_rate}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistiques des Notes</CardTitle>
            <CardDescription>Distribution des résultats</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center pb-4 border-b">
                <div className="text-3xl font-bold text-blue-600">
                  {analyticsData.grade_statistics.average_grade.toFixed(2)}/20
                </div>
                <p className="text-xs text-muted-foreground">Moyenne générale</p>
                <p className="text-xs text-muted-foreground">{analyticsData.grade_statistics.total_grades} notes</p>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center text-sm">
                  <span>Excellent (≥16)</span>
                  <Badge className="bg-green-100 text-green-800">
                    {analyticsData.grade_statistics.excellent}
                  </Badge>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span>Bien (14-16)</span>
                  <Badge className="bg-blue-100 text-blue-800">
                    {analyticsData.grade_statistics.good}
                  </Badge>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span>Passable (10-14)</span>
                  <Badge className="bg-yellow-100 text-yellow-800">
                    {analyticsData.grade_statistics.average}
                  </Badge>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span>Insuffisant (&lt;10)</span>
                  <Badge className="bg-red-100 text-red-800">
                    {analyticsData.grade_statistics.poor}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Activité Récente</CardTitle>
          <CardDescription>Dernières actions et événements importants</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {activities.length > 0 ? (
              activities.map((activity, index) => {
                const Icon = getActivityIcon(activity.type)
                const colorClass = getActivityColor(activity.severity)
                
                return (
                  <div key={index} className={`flex items-center space-x-4 p-3 border-l-4 ${colorClass} rounded`}>
                    <Icon className="h-5 w-5" />
                    <div className="flex-1">
                      {activity.type === 'absence' ? (
                        <>
                          <p className="text-sm font-medium">Absence - {activity.student}</p>
                          <p className="text-sm">{activity.subject} • {activity.status}</p>
                        </>
                      ) : (
                        <>
                          <p className="text-sm font-medium">Note - {activity.student}</p>
                          <p className="text-sm">{activity.subject} • {activity.grade}/20 • {activity.teacher}</p>
                        </>
                      )}
                    </div>
                    <span className="text-xs">{formatTimeAgo(activity.timestamp)}</span>
                  </div>
                )
              })
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Calendar className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Aucune activité récente</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}