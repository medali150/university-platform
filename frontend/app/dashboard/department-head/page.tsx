'use client'

import { useState, useEffect } from 'react'
import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, MessageSquare, UserX, BookOpen, BarChart3, Users, Settings, Loader2, GraduationCap, FileText, Clock, Building } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function DepartmentHeadDashboard() {
  const { user, isLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedView, setSelectedView] = useState<'overview' | 'students' | 'teachers' | 'subjects' | 'schedules' | 'groups'>('overview')
  
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
      
      // Get user's department (for now using first department as fallback)
      const departments = await api.getDepartments()
      const userDepartment = departments[0] // TODO: Get actual user's department from user profile
      setDepartmentData(userDepartment)
      
      if (!userDepartment) {
        setError('Département non trouvé')
        return
      }
      
      // Fetch comprehensive department data
      const comprehensiveData = await api.getDepartmentComprehensiveData(userDepartment.id)
      
      // Set all data states
      setStudents(comprehensiveData.students)
      setTeachers(comprehensiveData.teachers)
      setSubjects(comprehensiveData.subjects)
      setGroups(comprehensiveData.groups)
      setLevels(comprehensiveData.levels)
      setSpecialties(comprehensiveData.specialties)
      setSchedules(comprehensiveData.schedules)
      setRooms(comprehensiveData.rooms)
      setDepartmentHeads(comprehensiveData.departmentHeads)
      
      // Generate recent activity from real data
      const activities = []
      if (comprehensiveData.students.length > 0) {
        activities.push({
          id: 1,
          type: 'students',
          message: `${comprehensiveData.students.length} étudiants dans le département`,
          details: `Département: ${userDepartment.name}`,
          time: 'Maintenant'
        })
      }
      if (comprehensiveData.teachers.length > 0) {
        activities.push({
          id: 2,
          type: 'teachers',
          message: `${comprehensiveData.teachers.length} enseignants actifs`,
          details: `Personnel du département ${userDepartment.name}`,
          time: 'Maintenant'
        })
      }
      if (comprehensiveData.specialties.length > 0) {
        activities.push({
          id: 3,
          type: 'specialties',
          message: `${comprehensiveData.specialties.length} spécialités disponibles`,
          details: 'Formations proposées dans le département',
          time: 'Maintenant'
        })
      }
      
      setRecentActivity(activities)
      
    } catch (err) {
      console.error('Error loading comprehensive data:', err)
      setError('Erreur lors du chargement des données du département')
    } finally {
      setLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm text-muted-foreground">Chargement du tableau de bord...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
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
            <Button onClick={loadStatistics} className="mt-4" disabled={loading}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Settings className="h-4 w-4 mr-2" />
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
        <div className="absolute inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin" />
            <p className="text-sm text-muted-foreground">Chargement des données complètes...</p>
          </div>
        </div>
      )}
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Vue d'ensemble du département
          {departmentData?.name && <span className="text-lg font-normal text-muted-foreground ml-2">- {departmentData.name}</span>}
        </h1>
        <p className="text-muted-foreground">
          Bon retour, {user.prenom}. Voici les données complètes de votre département.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-600">
            {error}
            <Button onClick={loadComprehensiveData} className="ml-4" size="sm" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Réessayer
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Navigation Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { key: 'overview', label: 'Vue d\'ensemble', icon: BarChart3 },
          { key: 'students', label: `Étudiants (${students.length})`, icon: GraduationCap },
          { key: 'teachers', label: `Enseignants (${teachers.length})`, icon: Users },
          { key: 'subjects', label: `Matières (${subjects.length})`, icon: BookOpen },
          { key: 'schedules', label: `Horaires (${schedules.length})`, icon: Calendar },
          { key: 'groups', label: `Groupes (${groups.length})`, icon: FileText }
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setSelectedView(key as any)}
            className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === key
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Actions Rapides</CardTitle>
            <CardDescription>Accès rapide aux fonctionnalités principales</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link href="/dashboard/department-head/timetable">
                <Button variant="outline" className="w-full justify-start">
                  <Clock className="mr-2 h-4 w-4" />
                  Gestion des Emplois du Temps
                </Button>
              </Link>
              <Button variant="outline" className="w-full justify-start" disabled>
                <MessageSquare className="mr-2 h-4 w-4" />
                Gestion des Absences
              </Button>
              <Button variant="outline" className="w-full justify-start" disabled>
                <Settings className="mr-2 h-4 w-4" />
                Configuration Département
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Comprehensive Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Étudiants</CardTitle>
            <GraduationCap className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{students.length}</div>
            <p className="text-xs text-muted-foreground">Dans le département</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
            <Users className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{teachers.length}</div>
            <p className="text-xs text-muted-foreground">Personnel actif</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Spécialités</CardTitle>
            <BookOpen className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{specialties.length}</div>
            <p className="text-xs text-muted-foreground">Formations proposées</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Matières</CardTitle>
            <FileText className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{subjects.length}</div>
            <p className="text-xs text-muted-foreground">Cours disponibles</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Groupes</CardTitle>
            <Users className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{groups.length}</div>
            <p className="text-xs text-muted-foreground">Classes organisées</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Niveaux</CardTitle>
            <BarChart3 className="h-4 w-4 text-indigo-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-indigo-600">{levels.length}</div>
            <p className="text-xs text-muted-foreground">Années d'étude</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Horaires</CardTitle>
            <Calendar className="h-4 w-4 text-teal-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-teal-600">{schedules.length}</div>
            <p className="text-xs text-muted-foreground">Créneaux planifiés</p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Salles</CardTitle>
            <Building className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{rooms.length}</div>
            <p className="text-xs text-muted-foreground">Espaces disponibles</p>
          </CardContent>
        </Card>
      </div>

      {/* Dynamic Content Based on Selected View */}
      {selectedView === 'overview' && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Activité récente
              </CardTitle>
              <CardDescription>Données du département en temps réel</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-center space-x-4 rounded-md border p-4">
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.message}</p>
                      <p className="text-sm text-muted-foreground">{activity.details}</p>
                    </div>
                    <div className="text-sm text-muted-foreground">{activity.time}</div>
                  </div>
                ))}
                {recentActivity.length === 0 && (
                  <p className="text-center py-4 text-muted-foreground">Aucune activité récente</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Résumé du département
              </CardTitle>
              <CardDescription>Aperçu des données clés</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total étudiants</span>
                  <span className="text-sm font-medium">{students.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Personnel enseignant</span>
                  <span className="text-sm font-medium">{teachers.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Formations disponibles</span>
                  <span className="text-sm font-medium">{specialties.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Cours planifiés</span>
                  <span className="text-sm font-medium">{schedules.length}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Students View */}
      {selectedView === 'students' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5" />
              Étudiants du département ({students.length})
            </CardTitle>
            <CardDescription>
              {departmentData ? `Département: ${departmentData.name}` : 'Liste des étudiants'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
              {students.map((student, index) => (
                <div key={student.id || index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                  <div className="font-medium">{student.prenom} {student.nom}</div>
                  <div className="text-sm text-gray-600">{student.email}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    ID: {student.id} | Rôle: {student.role}
                  </div>
                </div>
              ))}
              {students.length === 0 && (
                <div className="col-span-full text-center py-8 text-gray-500">
                  Aucun étudiant trouvé dans ce département
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Teachers View */}
      {selectedView === 'teachers' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Enseignants du département ({teachers.length})
            </CardTitle>
            <CardDescription>
              {departmentData ? `Département: ${departmentData.name}` : 'Personnel enseignant'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
              {teachers.map((teacher, index) => (
                <div key={teacher.id || index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                  <div className="font-medium">{teacher.prenom} {teacher.nom}</div>
                  <div className="text-sm text-gray-600">{teacher.email}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    ID: {teacher.id} | Rôle: {teacher.role}
                  </div>
                  {teacher.teacherInfo?.department && (
                    <div className="text-xs text-blue-600 mt-1">
                      Dept: {teacher.teacherInfo.department.name}
                    </div>
                  )}
                </div>
              ))}
              {teachers.length === 0 && (
                <div className="col-span-full text-center py-8 text-gray-500">
                  Aucun enseignant trouvé dans ce département
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Subjects View */}
      {selectedView === 'subjects' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Matières disponibles ({subjects.length})
            </CardTitle>
            <CardDescription>Cours et matières enseignées</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
              {subjects.map((subject, index) => (
                <div key={subject.id || index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                  <div className="font-medium">{subject.name || subject.nom || 'Matière sans nom'}</div>
                  <div className="text-sm text-gray-600">{subject.code || 'Code non défini'}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {subject.credits ? `${subject.credits} crédits` : 'Crédits non définis'}
                  </div>
                  {subject.description && (
                    <div className="text-xs text-gray-600 mt-2">{subject.description}</div>
                  )}
                </div>
              ))}
              {subjects.length === 0 && (
                <div className="col-span-full text-center py-8 text-gray-500">
                  Aucune matière trouvée
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Schedules View */}
      {selectedView === 'schedules' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Horaires planifiés ({schedules.length})
            </CardTitle>
            <CardDescription>Planning des cours et activités</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {schedules.map((schedule, index) => (
                <div key={schedule.id || index} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{schedule.subject?.name || 'Cours non défini'}</div>
                      <div className="text-sm text-gray-600">
                        {schedule.startTime} - {schedule.endTime}
                      </div>
                      <div className="text-xs text-gray-500">
                        Salle: {schedule.room?.name || 'Non définie'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">{schedule.dayOfWeek}</div>
                      <div className="text-xs text-gray-500">{schedule.group?.name || 'Groupe non défini'}</div>
                    </div>
                  </div>
                </div>
              ))}
              {schedules.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Aucun horaire planifié
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Groups View */}
      {selectedView === 'groups' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Groupes ({groups.length})
              </CardTitle>
              <CardDescription>Classes et groupes d'étudiants</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {groups.map((group, index) => (
                  <div key={group.id || index} className="p-3 border rounded-lg">
                    <div className="font-medium">{group.name || group.nom || 'Groupe sans nom'}</div>
                    <div className="text-sm text-gray-600">
                      {group.studentCount || 0} étudiants
                    </div>
                    <div className="text-xs text-gray-500">
                      Niveau: {group.level?.name || 'Non défini'}
                    </div>
                  </div>
                ))}
                {groups.length === 0 && (
                  <div className="text-center py-4 text-gray-500">
                    Aucun groupe trouvé
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Spécialités ({specialties.length})
              </CardTitle>
              <CardDescription>Formations du département</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {specialties.map((specialty, index) => (
                  <div key={specialty.id || index} className="p-3 border rounded-lg">
                    <div className="font-medium">{specialty.name || specialty.nom || 'Spécialité sans nom'}</div>
                    <div className="text-sm text-gray-600">{specialty.description || 'Description non disponible'}</div>
                    <div className="text-xs text-gray-500">
                      Département: {departmentData?.name || 'Non défini'}
                    </div>
                  </div>
                ))}
                {specialties.length === 0 && (
                  <div className="text-center py-4 text-gray-500">
                    Aucune spécialité trouvée
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}