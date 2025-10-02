'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BookOpen, Users, GraduationCap, Search, Plus, Edit, Trash2, Eye, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react'
import { useState, useEffect } from 'react'
import { SubjectsAPI } from '@/lib/subjects-api'
import { Subject } from '@/types/api'
import { toast } from 'sonner'

export default function SubjectsPage() {
  const { user, isLoading: authLoading } = useRequireRole(['DEPARTMENT_HEAD', 'ADMIN'] as Role[])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<string>('')
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [subjectsLoading, setSubjectsLoading] = useState(true)
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0
  })
  const [stats, setStats] = useState({
    totalSubjects: 0,
    byLevel: [] as { levelName: string; count: number }[],
    byDepartment: [] as { departmentName: string; count: number }[],
    byTeacher: [] as { teacherName: string; count: number }[]
  })

  // Load subjects data
  const loadSubjects = async (page = 1, search = '', levelId = '') => {
    try {
      setSubjectsLoading(true)
      const response = await SubjectsAPI.getSubjects({
        page,
        pageSize: pagination.pageSize,
        search: search || undefined,
        levelId: levelId || undefined
      })
      
      setSubjects(response.subjects)
      setPagination({
        page: response.page,
        pageSize: response.pageSize,
        total: response.total,
        totalPages: response.totalPages
      })
    } catch (error) {
      console.error('Error loading subjects:', error)
      toast.error('Erreur lors du chargement des matières')
      // Set empty data on error
      setSubjects([])
      setPagination({ page: 1, pageSize: 10, total: 0, totalPages: 0 })
    } finally {
      setSubjectsLoading(false)
    }
  }

  // Load stats
  const loadStats = async () => {
    try {
      const statsData = await SubjectsAPI.getSubjectStats()
      setStats(statsData)
    } catch (error) {
      console.error('Error loading stats:', error)
      // Keep default empty stats on error
    }
  }

  // Delete subject
  const handleDeleteSubject = async (id: string) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette matière ?')) {
      return
    }

    try {
      await SubjectsAPI.deleteSubject(id)
      toast.success('Matière supprimée avec succès')
      loadSubjects(pagination.page, searchTerm, selectedLevel)
      loadStats()
    } catch (error) {
      console.error('Error deleting subject:', error)
      toast.error('Erreur lors de la suppression de la matière')
    }
  }

  // Initial data load
  useEffect(() => {
    if (user && !authLoading) {
      loadSubjects()
      loadStats()
    }
  }, [user, authLoading])

  // Search and filter effects
  useEffect(() => {
    if (!user || authLoading) return

    const delayedSearch = setTimeout(() => {
      loadSubjects(1, searchTerm, selectedLevel)
    }, 300)

    return () => clearTimeout(delayedSearch)
  }, [searchTerm, selectedLevel, user, authLoading])

  // Page change handler
  const handlePageChange = (newPage: number) => {
    loadSubjects(newPage, searchTerm, selectedLevel)
  }

  if (authLoading || subjectsLoading) {
    return <div className="flex items-center justify-center h-96">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  }

  if (!user) return null

  const selectedSubjectData = selectedSubject ? subjects.find(s => s.id === selectedSubject) : null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestion des Matières</h1>
          <p className="text-muted-foreground">
            Gérez les matières, crédits et assignations du département
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Nouvelle Matière
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Matières</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">15</div>
            <p className="text-xs text-muted-foreground">5 actives ce semestre</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Crédits</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">72</div>
            <p className="text-xs text-muted-foreground">ECTS disponibles</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Heures d'Enseignement</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">576h</div>
            <p className="text-xs text-muted-foreground">Total planifié</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">Assignés aux matières</p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Rechercher et Filtrer</CardTitle>
          <CardDescription>Trouvez rapidement les matières que vous cherchez</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher par nom, code ou enseignant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">
              Filtrer par Semestre
            </Button>
            <Button variant="outline">
              Filtrer par Statut
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Subjects List */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des Matières</CardTitle>
          <CardDescription>
                        <CardDescription>
              {pagination.total} matière{pagination.total > 1 ? 's' : ''} au total
            </CardDescription>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredSubjects.map((subject) => (
              <div key={subject.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <BookOpen className="h-6 w-6 text-blue-600" />
                  </div>
                  
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold">{subject.name}</h3>
                      <Badge variant="outline">{subject.code}</Badge>
                      {getStatusBadge(subject.status)}
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span>{subject.credits} ECTS</span>
                      <span>•</span>
                      <span>{subject.hours}h de cours</span>
                      <span>•</span>
                      <span>Semestre {subject.semester}</span>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <Users className="h-3 w-3" />
                        <span>Groupes: {subject.groups.join(', ')}</span>
                      </div>
                      <span>•</span>
                      <div className="flex items-center space-x-1">
                        <span>Enseignants: {subject.teachers.join(', ')}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Actions Rapides</CardTitle>
            <CardDescription>Outils de gestion des matières</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <Plus className="mr-2 h-4 w-4" />
              Créer une Nouvelle Matière
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Users className="mr-2 h-4 w-4" />
              Assigner des Enseignants
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <BookOpen className="mr-2 h-4 w-4" />
              Importer depuis Excel
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Search className="mr-2 h-4 w-4" />
              Générer Rapport Complet
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistiques Rapides</CardTitle>
            <CardDescription>Vue d'ensemble du département</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Matières par Semestre</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>S1-S2</span>
                  <span>6 matières</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>S3-S4</span>
                  <span>5 matières</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>S5-S6</span>
                  <span>4 matières</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Répartition des Crédits</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Matières Fondamentales</span>
                  <span>40 ECTS</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Matières Spécialisées</span>
                  <span>24 ECTS</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Projets et Stages</span>
                  <span>8 ECTS</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}