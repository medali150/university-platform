'use client'

import { useState, useEffect } from 'react'
import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, MessageSquare, UserX, BookOpen, BarChart3, Users, Settings, Loader2, GraduationCap, FileText, Clock, Building, TrendingUp, Activity, Award, AlertCircle, CheckCircle, Search, Filter, Download, RefreshCw } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'

export default function DepartmentHeadDashboard() {
  const { user, isLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedView, setSelectedView] = useState<'overview' | 'students' | 'teachers' | 'subjects' | 'schedules' | 'groups' | 'analytics'>('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterActive, setFilterActive] = useState(false)
  
  // Comprehensive data states
  const [departmentData, setDepartmentData] = useState<any>(null)
  const [students, setStudents] = useState<any[]>([])
  const [teachers, setTeachers] = useState<any[]>([])
  const [subjects, setSubjects] = useState<any[]>([])
  const [groups, setGroups] = useState<any[]>([])
  const [levels, setLevels] = useState<any[]>([])
  const [specialties, setSpecialties] = useState<any[]>([])
  const [schedules, setSchedules] = useState<any[]>([])
  const [rooms, setRooms] = useState<any[]>([])
  const [departmentHeads, setDepartmentHeads] = useState<any[]>([])
  const [recentActivity, setRecentActivity] = useState<any[]>([])
  const [analyticsData, setAnalyticsData] = useState<any>(null)

  // Load comprehensive data when user is available
  useEffect(() => {
    if (user && !isLoading) {
      loadComprehensiveData()
    }
  }, [user, isLoading])

  const loadComprehensiveData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🔄 Loading department head dashboard data...')
      
      // Use department-head-specific endpoints
      const dashboardData = await api.getDepartmentHeadDashboardData()
      
      console.log('✅ Dashboard data received:', dashboardData)
      
      // Extract department info from specialities
      if (dashboardData.specialities && dashboardData.specialities.length > 0) {
        const firstSpec = dashboardData.specialities[0]
        if (firstSpec.departement) {
          setDepartmentData({
            id: firstSpec.departement.id || firstSpec.id_departement,
            nom: firstSpec.departement.nom,
            name: firstSpec.departement.nom
          })
        }
      }
      
      // Set data states
      setGroups(dashboardData.groups || [])
      setTeachers(dashboardData.teachers || [])
      setSubjects(dashboardData.subjects || [])
      setSpecialties(dashboardData.specialities || [])
      setRooms(dashboardData.rooms || [])
      setSchedules(dashboardData.schedules || [])
      
      // Calculate students from groups
      const studentCount = (dashboardData.groups || []).reduce((sum: number, group: any) => {
        return sum + (group._count?.etudiants || 0)
      }, 0)
      
      setStudents(Array(studentCount).fill({})) // Placeholder for student count
      
      // Extract levels from groups
      const uniqueLevels = (dashboardData.groups || []).map((g: any) => g.niveau).filter(Boolean)
      setLevels(uniqueLevels)
      
      // Generate recent activity from real data
      const activities = []
      
      if (dashboardData.groups && dashboardData.groups.length > 0) {
        activities.push({
          id: 1,
          type: 'groups',
          message: `${dashboardData.groups.length} groupes dans le département`,
          details: `Classes organisées`,
          time: 'Maintenant'
        })
      }
      
      if (dashboardData.teachers && dashboardData.teachers.length > 0) {
        activities.push({
          id: 2,
          type: 'teachers',
          message: `${dashboardData.teachers.length} enseignants actifs`,
          details: `Personnel du département`,
          time: 'Maintenant'
        })
      }
      
      if (dashboardData.specialities && dashboardData.specialities.length > 0) {
        activities.push({
          id: 3,
          type: 'specialities',
          message: `${dashboardData.specialities.length} spécialités disponibles`,
          details: `Formations proposées: ${dashboardData.specialities.map((s: any) => s.nom).join(', ')}`,
          time: 'Maintenant'
        })
      }
      
      if (dashboardData.subjects && dashboardData.subjects.length > 0) {
        activities.push({
          id: 4,
          type: 'subjects',
          message: `${dashboardData.subjects.length} matières disponibles`,
          details: `Cours dispensés dans le département`,
          time: 'Maintenant'
        })
      }
      
      if (dashboardData.schedules && dashboardData.schedules.length > 0) {
        activities.push({
          id: 5,
          type: 'schedules',
          message: `${dashboardData.schedules.length} horaires planifiés`,
          details: `Emplois du temps actifs`,
          time: 'Maintenant'
        })
      }
      
      setRecentActivity(activities)
      
      // Calculate analytics data
      const avgStudentsPerGroup = groups.length > 0 
        ? Math.round((students.length / groups.length) * 10) / 10 
        : 0
      
      setAnalyticsData({
        avgStudentsPerGroup,
        teacherStudentRatio: teachers.length > 0 ? Math.round((students.length / teachers.length) * 10) / 10 : 0,
        occupancyRate: rooms.length > 0 ? Math.round((schedules.length / rooms.length) * 100) : 0,
        completionRate: schedules.length > 0 ? Math.round((schedules.filter((s: any) => s.isCompleted).length / schedules.length) * 100) : 0
      })
      
      console.log('✅ Dashboard loaded successfully')
      
    } catch (err: any) {
      console.error('❌ Error loading dashboard data:', err)
      setError('Erreur lors du chargement des données: ' + (err.message || 'Erreur inconnue'))
    } finally {
      setLoading(false)
    }
  }

  // Filtered data based on search
  const filteredStudents = students.filter(s => 
    `${s.prenom} ${s.nom}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.email?.toLowerCase().includes(searchQuery.toLowerCase())
  )
  
  const filteredTeachers = teachers.filter(t =>
    `${t.prenom} ${t.nom}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.email?.toLowerCase().includes(searchQuery.toLowerCase())
  )
  
  const filteredSubjects = subjects.filter(s =>
    (s.nom || s.name)?.toLowerCase().includes(searchQuery.toLowerCase())
  )
  
  const filteredGroups = groups.filter(g =>
    (g.name || g.nom)?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-sm text-muted-foreground">Chargement du tableau de bord...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <AlertCircle className="h-8 w-8 text-red-500" />
          <p className="text-sm text-muted-foreground">Accès refusé. Connexion requise.</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Vue d'ensemble du département</h1>
          <p className="text-muted-foreground">
            Bon retour, {user.prenom}. Voici l'état de votre service.
          </p>
        </div>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
            <Button onClick={loadComprehensiveData} className="mt-4" disabled={loading}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Réessayer
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 relative">
      {loading && (
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center rounded-lg">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <p className="text-sm text-muted-foreground">Actualisation des données...</p>
          </div>
        </div>
      )}
      
      {/* Header Section with Modern Design */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-8 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-4xl font-bold tracking-tight mb-2">
                Vue d'ensemble du département
              </h1>
              {departmentData && (
                <p className="text-blue-100 text-lg font-medium">📍 {departmentData.nom || departmentData.name}</p>
              )}
              <p className="text-blue-100 mt-2">
                Bienvenue, Chef. Gestion complète de votre département
              </p>
            </div>
            <Button 
              variant="ghost" 
              size="lg"
              onClick={loadComprehensiveData}
              className="text-white hover:bg-white/20"
            >
              <RefreshCw className="h-5 w-5 mr-2" />
              Actualiser
            </Button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert className="border-red-200 bg-red-50 animate-in fade-in">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-600 ml-2">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* KPI Cards - Modern Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { 
            title: 'Étudiants', 
            value: students.length, 
            icon: GraduationCap, 
            color: 'from-blue-500 to-blue-600',
            trend: '+12%'
          },
          { 
            title: 'Enseignants', 
            value: teachers.length, 
            icon: Users, 
            color: 'from-green-500 to-green-600',
            trend: '+5%'
          },
          { 
            title: 'Matières', 
            value: subjects.length, 
            icon: BookOpen, 
            color: 'from-purple-500 to-purple-600',
            trend: '=0%'
          },
          { 
            title: 'Salles', 
            value: rooms.length, 
            icon: Building, 
            color: 'from-orange-500 to-orange-600',
            trend: '+8%'
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

      {/* Analytics Cards */}
      {analyticsData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              label: 'Étudiants par groupe',
              value: analyticsData.avgStudentsPerGroup.toFixed(1),
              unit: 'moy',
              icon: Users,
              color: 'bg-blue-50 text-blue-700'
            },
            {
              label: 'Ratio Prof/Étudiants',
              value: analyticsData.teacherStudentRatio.toFixed(1),
              unit: ':1',
              icon: Award,
              color: 'bg-purple-50 text-purple-700'
            },
            {
              label: 'Taux d\'occupation',
              value: analyticsData.occupancyRate,
              unit: '%',
              icon: Activity,
              color: 'bg-green-50 text-green-700'
            },
            {
              label: 'Taux de complétude',
              value: analyticsData.completionRate,
              unit: '%',
              icon: CheckCircle,
              color: 'bg-orange-50 text-orange-700'
            }
          ].map((stat, idx) => {
            const Icon = stat.icon
            return (
              <div key={idx} className={`rounded-lg p-6 ${stat.color} border border-current border-opacity-10`}>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-sm font-medium">{stat.label}</h3>
                  <Icon className="h-5 w-5 opacity-50" />
                </div>
                <p className="text-3xl font-bold">
                  {stat.value}{stat.unit}
                </p>
                <div className="mt-2 h-1 bg-current bg-opacity-20 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-current bg-opacity-70 rounded-full transition-all"
                    style={{ width: `${Math.min(parseInt(stat.value), 100)}%` }}
                  ></div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className="flex gap-4 items-center">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <Input
            placeholder="Rechercher un étudiant, enseignant, matière..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 h-11 bg-white border-gray-200"
          />
        </div>
        <Button 
          variant={filterActive ? "default" : "outline"}
          size="lg"
          className="gap-2"
          onClick={() => setFilterActive(!filterActive)}
        >
          <Filter className="h-4 w-4" />
          Filtres
        </Button>
        <Button variant="outline" size="lg" className="gap-2">
          <Download className="h-4 w-4" />
          Exporter
        </Button>
      </div>

      {/* Modern Navigation Tabs */}
      <div className="overflow-x-auto">
        <div className="flex gap-2 p-1 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg w-fit md:w-full">
          {[
            { key: 'overview', label: 'Vue d\'ensemble', icon: BarChart3 },
            { key: 'students', label: `Étudiants (${students.length})`, icon: GraduationCap },
            { key: 'teachers', label: `Enseignants (${teachers.length})`, icon: Users },
            { key: 'subjects', label: `Matières (${subjects.length})`, icon: BookOpen },
            { key: 'schedules', label: `Horaires (${schedules.length})`, icon: Calendar },
            { key: 'groups', label: `Groupes (${groups.length})`, icon: FileText },
            { key: 'analytics', label: 'Analytique', icon: TrendingUp }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setSelectedView(key as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                selectedView === key
                  ? 'bg-white text-blue-600 shadow-md scale-105'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Quick Actions with Modern Design */}
      {selectedView === 'overview' && (
        <div className="mb-6">
          <Card className="border-0 shadow-lg bg-gradient-to-br from-white to-gray-50">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-bold">⚡ Actions Rapides</CardTitle>
                  <CardDescription>Accédez instantanément aux fonctionnalités clés</CardDescription>
                </div>
                <Activity className="h-8 w-8 text-blue-500 opacity-50" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {[
                  { href: '/dashboard/department-head/department-schedule', label: 'Emplois du Temps du Département', icon: Calendar },
                  { href: '/dashboard/department-head/all-timetables', label: 'Tous les Emplois du Temps', icon: Calendar },
                  { href: '/dashboard/department-head/schedule', label: 'Créer/Modifier les Emplois', icon: Clock },
                  { href: '/dashboard/department-head/subjects', label: 'Gestion des Matières', icon: BookOpen },
                  { href: '/dashboard/department-head/averages', label: 'Gestion des Moyennes', icon: BarChart3 },
                  { href: '/dashboard/department-head/analytics', label: 'Analytique Avancée', icon: TrendingUp },
                ].map((action, idx) => {
                  const Icon = action.icon
                  return (
                    <Link key={idx} href={action.href}>
                      <Button 
                        variant="outline" 
                        className="w-full justify-start h-12 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 transition-all group"
                      >
                        <Icon className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />
                        <span className="text-xs">{action.label}</span>
                      </Button>
                    </Link>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Comprehensive Statistics Cards - Modern Version */}
      {selectedView === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { title: 'Spécialités', value: specialties.length, icon: Award, color: 'purple' },
            { title: 'Niveaux', value: levels.length, icon: TrendingUp, color: 'indigo' },
            { title: 'Salles', value: rooms.length, icon: Building, color: 'gray' },
            { title: 'Horaires', value: schedules.length, icon: Clock, color: 'teal' }
          ].map((stat, idx) => {
            const Icon = stat.icon
            const colorClasses: any = {
              purple: 'from-purple-500 to-purple-600',
              indigo: 'from-indigo-500 to-indigo-600',
              gray: 'from-gray-500 to-gray-600',
              teal: 'from-teal-500 to-teal-600'
            }
            return (
              <div 
                key={idx}
                className="group relative overflow-hidden rounded-lg bg-white p-6 shadow-sm hover:shadow-lg transition-all"
              >
                <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${colorClasses[stat.color as keyof typeof colorClasses]} opacity-5 rounded-full -translate-y-1/2 translate-x-1/2 group-hover:opacity-10 transition-opacity`}></div>
                <div className="relative z-10">
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${colorClasses[stat.color as keyof typeof colorClasses]} text-white mb-4`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Activity and Summary Section */}
      {selectedView === 'overview' && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Activity className="h-5 w-5 text-blue-600" />
                Activité récente
              </CardTitle>
              <CardDescription>Mises à jour en temps réel du département</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentActivity.slice(0, 5).map((activity, idx) => (
                  <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 hover:shadow-md transition-shadow">
                    <div className={`w-2 h-2 rounded-full mt-2 ${idx % 2 === 0 ? 'bg-blue-600' : 'bg-purple-600'}`}></div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                      <p className="text-xs text-gray-500 mt-1">{activity.details}</p>
                    </div>
                    <span className="text-xs text-gray-400 whitespace-nowrap ml-2">{activity.time}</span>
                  </div>
                ))}
                {recentActivity.length === 0 && (
                  <p className="text-center py-6 text-gray-500 text-sm">Aucune activité récente</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <BarChart3 className="h-5 w-5 text-purple-600" />
                Résumé exécutif
              </CardTitle>
              <CardDescription>Vue globale des indicateurs clés</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { label: 'Total étudiants', value: students.length, total: 500, color: 'blue' },
                  { label: 'Personnel enseignant', value: teachers.length, total: 100, color: 'green' },
                  { label: 'Formations proposées', value: specialties.length, total: 20, color: 'purple' },
                  { label: 'Cours planifiés', value: schedules.length, total: 200, color: 'orange' }
                ].map((item, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">{item.label}</span>
                      <span className="text-sm font-bold text-gray-900">{item.value}</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full bg-gradient-to-r from-${item.color}-500 to-${item.color}-600 rounded-full transition-all`}
                        style={{ width: `${Math.min((item.value / item.total) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Students View - Modern Card Design */}
      {selectedView === 'students' && (
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-cyan-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/20 text-blue-600">
                  <GraduationCap className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-xl">Étudiants ({filteredStudents.length})</CardTitle>
                  <CardDescription>Tous les étudiants du département</CardDescription>
                </div>
              </div>
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
              {filteredStudents.map((student, index) => (
                <div 
                  key={student.id || index} 
                  className="p-4 border rounded-lg hover:shadow-md hover:border-blue-200 transition-all group cursor-pointer bg-gradient-to-br from-white to-gray-50 hover:from-blue-50 hover:to-cyan-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">{student.prenom} {student.nom}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{student.email}</div>
                    </div>
                    <div className="p-2 rounded-lg bg-blue-100 text-blue-600 group-hover:bg-blue-200 transition-colors">
                      <GraduationCap className="h-4 w-4" />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3 text-xs">
                    <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-700">ID: {student.id?.slice(-4)}</span>
                    <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700">{student.role}</span>
                  </div>
                </div>
              ))}
              {filteredStudents.length === 0 && (
                <div className="col-span-full text-center py-12 text-gray-500">
                  <GraduationCap className="h-12 w-12 mx-auto opacity-20 mb-3" />
                  <p>Aucun étudiant trouvé</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Teachers View - Modern Card Design */}
      {selectedView === 'teachers' && (
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-4 bg-gradient-to-r from-green-50 to-emerald-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-500/20 text-green-600">
                  <Users className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-xl">Enseignants ({filteredTeachers.length})</CardTitle>
                  <CardDescription>Personnel enseignant du département</CardDescription>
                </div>
              </div>
              <Award className="h-5 w-5 text-green-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
              {filteredTeachers.map((teacher, index) => (
                <div 
                  key={teacher.id || index} 
                  className="p-4 border rounded-lg hover:shadow-md hover:border-green-200 transition-all group cursor-pointer bg-gradient-to-br from-white to-gray-50 hover:from-green-50 hover:to-emerald-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 group-hover:text-green-600 transition-colors">{teacher.prenom} {teacher.nom}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{teacher.email}</div>
                    </div>
                    <div className="p-2 rounded-lg bg-green-100 text-green-600 group-hover:bg-green-200 transition-colors">
                      <Users className="h-4 w-4" />
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3 text-xs">
                    <span className="px-2 py-1 rounded-full bg-green-100 text-green-700">ID: {teacher.id?.slice(-4)}</span>
                    <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700">{teacher.role}</span>
                  </div>
                  {teacher.teacherInfo?.department && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <div className="text-xs text-green-600 font-medium">
                        📍 {teacher.teacherInfo.department.name || teacher.teacherInfo.department}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {filteredTeachers.length === 0 && (
                <div className="col-span-full text-center py-12 text-gray-500">
                  <Users className="h-12 w-12 mx-auto opacity-20 mb-3" />
                  <p>Aucun enseignant trouvé</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Subjects View - Modern Design */}
      {selectedView === 'subjects' && (
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-4 bg-gradient-to-r from-purple-50 to-pink-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-500/20 text-purple-600">
                  <BookOpen className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-xl">Matières ({filteredSubjects.length})</CardTitle>
                  <CardDescription>Cours et matières enseignées</CardDescription>
                </div>
              </div>
              <Award className="h-5 w-5 text-purple-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
              {filteredSubjects.map((subject, index) => (
                <div 
                  key={subject.id || index} 
                  className="p-4 border rounded-lg hover:shadow-md hover:border-purple-200 transition-all group cursor-pointer bg-gradient-to-br from-white to-gray-50 hover:from-purple-50 hover:to-pink-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 group-hover:text-purple-600 transition-colors">{subject.nom || subject.name || 'Matière sans nom'}</div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        {subject.specialite?.nom && `📚 ${subject.specialite.nom}`}
                      </div>
                    </div>
                    <div className="p-2 rounded-lg bg-purple-100 text-purple-600 group-hover:bg-purple-200 transition-colors">
                      <BookOpen className="h-4 w-4" />
                    </div>
                  </div>
                  {subject.enseignant && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <div className="text-xs text-gray-600">
                        👨‍🏫 {subject.enseignant.prenom} {subject.enseignant.nom}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {filteredSubjects.length === 0 && (
                <div className="col-span-full text-center py-12 text-gray-500">
                  <BookOpen className="h-12 w-12 mx-auto opacity-20 mb-3" />
                  <p>Aucune matière trouvée</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Schedules View - Timeline Design */}
      {selectedView === 'schedules' && (
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-4 bg-gradient-to-r from-orange-50 to-amber-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-500/20 text-orange-600">
                  <Calendar className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-xl">Horaires ({schedules.length})</CardTitle>
                  <CardDescription>Planning des cours et activités</CardDescription>
                </div>
              </div>
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {schedules.map((schedule, index) => (
                <div 
                  key={schedule.id || index} 
                  className="p-4 border rounded-lg hover:shadow-md hover:border-orange-200 transition-all bg-gradient-to-r from-white to-gray-50 hover:from-orange-50 hover:to-amber-50 group"
                >
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 group-hover:text-orange-600 transition-colors mb-1">
                        {schedule.subject?.name || 'Cours non défini'}
                      </div>
                      <div className="flex gap-2 mt-2 text-xs">
                        <span className="px-2 py-1 rounded-full bg-orange-100 text-orange-700 font-medium">
                          ⏰ {schedule.startTime} - {schedule.endTime}
                        </span>
                        <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                          🏛️ Salle {schedule.room?.name || 'N/A'}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-orange-600">{schedule.dayOfWeek}</div>
                      <div className="text-xs text-gray-500 mt-1">📍 {schedule.group?.name || 'Groupe N/A'}</div>
                    </div>
                  </div>
                </div>
              ))}
              {schedules.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <Calendar className="h-12 w-12 mx-auto opacity-20 mb-3" />
                  <p>Aucun horaire planifié</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Groups View - Dual Layout */}
      {selectedView === 'groups' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-4 bg-gradient-to-r from-red-50 to-pink-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-red-500/20 text-red-600">
                  <Users className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle>Groupes ({filteredGroups.length})</CardTitle>
                  <CardDescription>Classes et groupes d'étudiants</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {filteredGroups.map((group, index) => (
                  <div 
                    key={group.id || index} 
                    className="p-3 border rounded-lg hover:shadow-md hover:border-red-200 transition-all bg-gradient-to-r from-white to-gray-50 hover:from-red-50 hover:to-pink-50 group cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900 group-hover:text-red-600 transition-colors">
                          {group.name || group.nom || 'Groupe sans nom'}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          📊 {group.studentCount || 0} étudiants • Niveau: {group.level?.name || 'N/A'}
                        </div>
                      </div>
                      <Users className="h-5 w-5 text-red-400 opacity-50" />
                    </div>
                  </div>
                ))}
                {filteredGroups.length === 0 && (
                  <div className="text-center py-8 text-gray-500 text-sm">
                    <Users className="h-8 w-8 mx-auto opacity-20 mb-2" />
                    Aucun groupe trouvé
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-4 bg-gradient-to-r from-indigo-50 to-blue-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-600">
                  <Award className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle>Spécialités ({specialties.length})</CardTitle>
                  <CardDescription>Formations du département</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {specialties.map((specialty, index) => (
                  <div 
                    key={specialty.id || index} 
                    className="p-3 border rounded-lg hover:shadow-md hover:border-indigo-200 transition-all bg-gradient-to-r from-white to-gray-50 hover:from-indigo-50 hover:to-blue-50 group cursor-pointer"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 group-hover:text-indigo-600 transition-colors">
                          {specialty.name || specialty.nom || 'Spécialité sans nom'}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {specialty.description || 'Description non disponible'}
                        </div>
                      </div>
                      <Award className="h-5 w-5 text-indigo-400 opacity-50 flex-shrink-0" />
                    </div>
                  </div>
                ))}
                {specialties.length === 0 && (
                  <div className="text-center py-8 text-gray-500 text-sm">
                    <Award className="h-8 w-8 mx-auto opacity-20 mb-2" />
                    Aucune spécialité trouvée
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analytics View - Advanced Charts and Metrics */}
      {selectedView === 'analytics' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { title: 'Croissance mensuelles', value: '+15%', change: 'positive', icon: TrendingUp },
              { title: 'Taux de satisfaction', value: '87%', change: 'positive', icon: Award },
              { title: 'Taux d\'assiduité', value: '92%', change: 'positive', icon: CheckCircle },
              { title: 'Charge de travail', value: '78%', change: 'warning', icon: Activity }
            ].map((metric, idx) => {
              const Icon = metric.icon
              const bgColor = metric.change === 'positive' 
                ? 'from-green-50 to-emerald-50' 
                : 'from-yellow-50 to-amber-50'
              const borderColor = metric.change === 'positive' ? 'border-green-200' : 'border-yellow-200'
              const textColor = metric.change === 'positive' ? 'text-green-600' : 'text-yellow-600'
              
              return (
                <Card key={idx} className={`border-0 shadow-lg bg-gradient-to-br ${bgColor} border ${borderColor}`}>
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="text-sm text-gray-600 font-medium">{metric.title}</p>
                        <p className={`text-3xl font-bold ${textColor} mt-2`}>{metric.value}</p>
                      </div>
                      <div className={`p-2 rounded-lg ${textColor} bg-white/50`}>
                        <Icon className="h-5 w-5" />
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">
                      ↑ Données actualisées
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-purple-50">
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                Tendances et Prévisions
              </CardTitle>
              <CardDescription>Analyse des données historiques</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {[
                  { label: 'Croissance des étudiants', current: students.length, projected: students.length + 20, trend: 'up' },
                  { label: 'Expansion des enseignants', current: teachers.length, projected: teachers.length + 5, trend: 'up' },
                  { label: 'Nouvelles matières', current: subjects.length, projected: subjects.length + 3, trend: 'up' }
                ].map((forecast, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">{forecast.label}</span>
                      <span className="text-sm text-green-600 font-bold">+{forecast.projected - forecast.current}</span>
                    </div>
                    <div className="flex gap-2">
                      <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                          style={{ width: `${(forecast.current / forecast.projected) * 100}%` }}
                        ></div>
                      </div>
                      <div className="flex-1 h-3 bg-gradient-to-r from-blue-100 to-blue-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-green-400 to-green-500 rounded-full opacity-60"
                          style={{ width: '100%' }}
                        ></div>
                      </div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Actuel: {forecast.current}</span>
                      <span>Prévu: {forecast.projected}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}