'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, MessageSquare, UserX, BookOpen, Plus, Users } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useEffect, useState } from 'react'
import { TeacherAPI, TeacherSchedule, TeacherStats } from '@/lib/teacher-api'

export default function TeacherDashboard() {
  const { user, isLoading } = useRequireRole('TEACHER' as Role)
  const [todaySchedule, setTodaySchedule] = useState<TeacherSchedule[]>([])
  const [stats, setStats] = useState<TeacherStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [scheduleData, statsData] = await Promise.all([
          TeacherAPI.getTodaySchedule(),
          TeacherAPI.getStats()
        ])
        
        setTodaySchedule(scheduleData)
        setStats(statsData)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    if (user) {
      fetchDashboardData()
    }
  }, [user])

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome back, Prof. {user.nom}!</h1>
        <p className="text-muted-foreground">
          Manage your classes and track student progress.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Classes</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? "..." : stats?.today_classes || 0}
            </div>
            <p className="text-xs text-muted-foreground">Sessions today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Absences</CardTitle>
            <UserX className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? "..." : stats?.pending_absences || 0}
            </div>
            <p className="text-xs text-muted-foreground">Need attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Make-up Requests</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? "..." : stats?.makeup_requests || 0}
            </div>
            <p className="text-xs text-muted-foreground">Proposed sessions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? "..." : stats?.messages || 0}
            </div>
            <p className="text-xs text-muted-foreground">Unread messages</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Today's Schedule</CardTitle>
            <CardDescription>Your teaching schedule for today</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              </div>
            ) : todaySchedule.length > 0 ? (
              todaySchedule.map((schedule) => (
                <div key={schedule.id} className="flex items-center space-x-4 rounded-md border p-4">
                  <div className="flex-1">
                    <p className="text-sm font-medium">
                      {schedule.matiere.nom} - {schedule.groupe.nom}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {schedule.salle.code} • {schedule.groupe.niveau} {schedule.groupe.specialite}
                    </p>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {schedule.heure_debut} - {schedule.heure_fin}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center p-8 text-muted-foreground">
                <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No classes scheduled for today</p>
              </div>
            )}
            <Link href="/dashboard/teacher/timetable">
              <Button variant="outline" className="w-full">View Full Timetable</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and features</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/dashboard/teacher/groups">
              <Button variant="outline" className="w-full justify-start">
                <Users className="mr-2 h-4 w-4" />
                View My Groups
              </Button>
            </Link>
            <Button variant="outline" className="w-full justify-start">
              <Plus className="mr-2 h-4 w-4" />
              Create Session
            </Button>
            <Link href="/dashboard/teacher/absences">
              <Button variant="outline" className="w-full justify-start">
                <UserX className="mr-2 h-4 w-4" />
                Gérer les Absences
              </Button>
            </Link>
            <Link href="/makeups">
              <Button variant="outline" className="w-full justify-start">
                <BookOpen className="mr-2 h-4 w-4" />
                Propose Make-up
              </Button>
            </Link>
            <Link href="/messages">
              <Button variant="outline" className="w-full justify-start">
                <MessageSquare className="mr-2 h-4 w-4" />
                Send Message
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}