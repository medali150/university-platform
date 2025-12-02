'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, MessageSquare, UserX, BookOpen, Plus, Users, TrendingUp, Award, Clock, Loader2, AlertCircle, CheckCircle, Activity, BarChart3 } from 'lucide-react'
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
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-white/60">Chargement du tableau de bord...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="space-y-6 p-4 sm:p-6 md:p-8">
      {/* Header Section */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-6 sm:p-8 md:p-10 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-2">
            Bienvenue, Prof. {user.nom}! 👋
          </h1>
          <p className="text-blue-100 text-base sm:text-lg">
            Gérez vos classes et suivez la progression des étudiants
          </p>
        </div>
      </div>

      {/* KPI Cards - Modern Design */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            title: 'Cours d\'aujourd\'hui',
            value: loading ? '...' : stats?.today_classes || 0,
            icon: Calendar,
            color: 'from-blue-500 to-blue-600',
            trend: '+12%'
          },
          {
            title: 'Absences en attente',
            value: loading ? '...' : stats?.pending_absences || 0,
            icon: UserX,
            color: 'from-orange-500 to-orange-600',
            trend: 'Action requise'
          },
          {
            title: 'Demandes de rattrapage',
            value: loading ? '...' : stats?.makeup_requests || 0,
            icon: BookOpen,
            color: 'from-green-500 to-green-600',
            trend: '+5%'
          },
          {
            title: 'Messages',
            value: loading ? '...' : stats?.messages || 0,
            icon: MessageSquare,
            color: 'from-purple-500 to-purple-600',
            trend: 'Non lus'
          }
        ].map((kpi, idx) => {
          const Icon = kpi.icon
          return (
            <div 
              key={idx}
              className="group relative overflow-hidden rounded-lg bg-white p-6 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${kpi.color} opacity-0 group-hover:opacity-5 transition-opacity`}></div>
              <div className="relative z-10">
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-br ${kpi.color} text-white`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">
                    {kpi.trend}
                  </span>
                </div>
                <h3 className="text-gray-600 text-sm font-medium mb-1">{kpi.title}</h3>
                <p className="text-3xl font-bold text-gray-900">{kpi.value}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Today's Schedule and Quick Actions */}
      <div className="grid gap-6 md:grid-cols-3 lg:grid-cols-4">
        {/* Today's Schedule */}
        <div className="md:col-span-2 lg:col-span-2">
          <Card className="border-0 shadow-lg h-full">
            <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-cyan-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/20 text-blue-600">
                  <Calendar className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle>Emploi du temps d'aujourd'hui</CardTitle>
                  <CardDescription>Vos cours et horaires</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-3">
                {loading ? (
                  <div className="flex items-center justify-center p-8">
                    <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                  </div>
                ) : todaySchedule.length > 0 ? (
                  todaySchedule.map((schedule) => (
                    <div 
                      key={schedule.id} 
                      className="p-4 border rounded-lg hover:shadow-md hover:border-blue-200 transition-all bg-gradient-to-r from-white to-gray-50 hover:from-blue-50 hover:to-cyan-50 group"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <p className="text-sm font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                            {schedule.matiere.nom}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            📚 {schedule.groupe.nom} • {schedule.groupe.niveau} {schedule.groupe.specialite}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            🏛️ Salle {schedule.salle.code}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-bold text-blue-600">
                            ⏰ {schedule.heure_debut}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            à {schedule.heure_fin}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center p-8 text-gray-500">
                    <Calendar className="h-12 w-12 mx-auto mb-4 opacity-20" />
                    <p className="text-sm">Pas de cours aujourd'hui</p>
                  </div>
                )}
                <Link href="/dashboard/teacher/timetable" className="w-full mt-4">
                  <Button variant="outline" className="w-full hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600">
                    <Calendar className="mr-2 h-4 w-4" />
                    Voir l'emploi du temps complet
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="md:col-span-1 lg:col-span-2">
          <Card className="border-0 shadow-lg h-full">
            <CardHeader className="pb-4 bg-gradient-to-r from-purple-50 to-pink-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-500/20 text-purple-600">
                  <Activity className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle>Actions rapides</CardTitle>
                  <CardDescription>Accès aux fonctionnalités principales</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Link href="/dashboard/teacher/groups" className="w-full">
                  <Button variant="outline" className="w-full justify-start h-12 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 transition-all group">
                    <Users className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                    <span className="text-xs sm:text-sm">Voir mes groupes</span>
                  </Button>
                </Link>
                <Link href="/dashboard/teacher/grades" className="w-full">
                  <Button variant="outline" className="w-full justify-start h-12 hover:bg-green-50 hover:border-green-200 hover:text-green-600 transition-all group">
                    <BookOpen className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                    <span className="text-xs sm:text-sm">📝 Gestion notes</span>
                  </Button>
                </Link>
                <Link href="/dashboard/teacher/absences" className="w-full">
                  <Button variant="outline" className="w-full justify-start h-12 hover:bg-orange-50 hover:border-orange-200 hover:text-orange-600 transition-all group">
                    <UserX className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                    <span className="text-xs sm:text-sm">Absences</span>
                  </Button>
                </Link>
                <Link href="/makeups" className="w-full">
                  <Button variant="outline" className="w-full justify-start h-12 hover:bg-purple-50 hover:border-purple-200 hover:text-purple-600 transition-all group">
                    <Clock className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                    <span className="text-xs sm:text-sm">Rattrapage</span>
                  </Button>
                </Link>
                <Link href="/messages" className="w-full sm:col-span-2">
                  <Button variant="outline" className="w-full justify-start h-12 hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-600 transition-all group">
                    <MessageSquare className="mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
                    <span className="text-xs sm:text-sm">Messages</span>
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Analytics Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-4 bg-gradient-to-r from-green-50 to-emerald-50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-500/20 text-green-600">
                <BarChart3 className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>Résumé d'aujourd'hui</CardTitle>
                <CardDescription>Aperçu des activités</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {[
                { label: 'Cours complétés', value: stats?.today_classes || 0, max: 5, color: 'from-green-500 to-green-600' },
                { label: 'Étudiants présents', value: stats?.messages || 0, max: 100, color: 'from-blue-500 to-blue-600' },
                { label: 'Absences traitées', value: stats?.pending_absences || 0, max: 10, color: 'from-orange-500 to-orange-600' }
              ].map((item, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">{item.label}</span>
                    <span className="text-sm font-bold text-gray-900">{item.value}/{item.max}</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className={`h-full bg-gradient-to-r ${item.color} rounded-full transition-all`}
                      style={{ width: `${Math.min((item.value / item.max) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-4 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-600">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>Cette semaine</CardTitle>
                <CardDescription>Statistiques hebdomadaires</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {[
                { label: 'Cours enseignés', value: '12', icon: Calendar },
                { label: 'Étudiants suivis', value: '87', icon: Users },
                { label: 'Taux de présence', value: '94%', icon: CheckCircle },
                { label: 'Évaluations données', value: '24', icon: Award }
              ].map((item, idx) => {
                const Icon = item.icon
                return (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-slate-50 to-gray-50 hover:shadow-md transition-all">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-gray-200">
                        <Icon className="h-4 w-4 text-gray-600" />
                      </div>
                      <span className="text-sm text-gray-700">{item.label}</span>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{item.value}</span>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}