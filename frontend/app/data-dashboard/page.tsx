'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { User, Department } from '@/types/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Loader2, Users, GraduationCap, UserCheck, Building2, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function DataDashboardPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Data states
  const [departments, setDepartments] = useState<Department[]>([])
  const [students, setStudents] = useState<User[]>([])
  const [teachers, setTeachers] = useState<User[]>([])
  const [departmentHeads, setDepartmentHeads] = useState<any[]>([])
  
  // Filter states
  const [selectedDepartment, setSelectedDepartment] = useState<string>('')
  
  // Load initial data
  useEffect(() => {
    loadAllData()
  }, [])
  
  // Reload filtered data when department changes
  useEffect(() => {
    if (selectedDepartment) {
      loadFilteredData()
    }
  }, [selectedDepartment])

  const loadAllData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Load departments first
      const deptData = await api.getDepartments()
      setDepartments(deptData)
      
      // Load all users data in parallel
      const [studentsData, teachersData, deptHeadsData] = await Promise.allSettled([
        api.getStudents(),
        api.getTeachers(),
        api.getDepartmentHeads()
      ])
      
      if (studentsData.status === 'fulfilled') {
        setStudents(studentsData.value)
      } else {
        console.error('Failed to load students:', studentsData.reason)
      }
      
      if (teachersData.status === 'fulfilled') {
        setTeachers(teachersData.value)
      } else {
        console.error('Failed to load teachers:', teachersData.reason)
      }
      
      if (deptHeadsData.status === 'fulfilled') {
        setDepartmentHeads(deptHeadsData.value)
      } else {
        console.error('Failed to load department heads:', deptHeadsData.reason)
      }
      
    } catch (err) {
      console.error('Error loading data:', err)
      setError('Erreur lors du chargement des données')
    } finally {
      setLoading(false)
    }
  }
  
  const loadFilteredData = async () => {
    if (!selectedDepartment) return
    
    setLoading(true)
    try {
      const filters = { department_id: selectedDepartment }
      
      const [studentsData, teachersData, deptHeadsData] = await Promise.allSettled([
        api.getStudents(filters),
        api.getTeachers(filters),
        api.getDepartmentHeads(filters)
      ])
      
      if (studentsData.status === 'fulfilled') {
        setStudents(studentsData.value)
      }
      
      if (teachersData.status === 'fulfilled') {
        setTeachers(teachersData.value)
      }
      
      if (deptHeadsData.status === 'fulfilled') {
        setDepartmentHeads(deptHeadsData.value)
      }
      
    } catch (err) {
      console.error('Error loading filtered data:', err)
      setError('Erreur lors du filtrage des données')
    } finally {
      setLoading(false)
    }
  }
  
  const clearFilter = () => {
    setSelectedDepartment('')
    loadAllData()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Link href="/" className="text-blue-600 hover:text-blue-800">
              <ArrowLeft className="h-6 w-6" />
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord des Données</h1>
          </div>
          <p className="text-gray-600">
            Visualisation des données réelles de la base de données: départements, étudiants, enseignants et chefs de département
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Filtres
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Label htmlFor="department-select">Filtrer par département</Label>
                <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
                  <SelectTrigger id="department-select">
                    <SelectValue placeholder="Tous les départements" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map(dept => (
                      <SelectItem key={dept.id} value={dept.id}>
                        {dept.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <Button onClick={loadAllData} disabled={loading}>
                  {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                  Actualiser
                </Button>
                {selectedDepartment && (
                  <Button variant="outline" onClick={clearFilter}>
                    Tout afficher
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="mb-8 border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <p className="text-red-600">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          
          {/* Departments Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Départements</CardTitle>
              <Building2 className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{departments.length}</div>
              <p className="text-xs text-muted-foreground">
                Total des départements
              </p>
            </CardContent>
          </Card>

          {/* Students Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Étudiants</CardTitle>
              <GraduationCap className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{students.length}</div>
              <p className="text-xs text-muted-foreground">
                {selectedDepartment ? 'Dans le département sélectionné' : 'Total des étudiants'}
              </p>
            </CardContent>
          </Card>

          {/* Teachers Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
              <Users className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{teachers.length}</div>
              <p className="text-xs text-muted-foreground">
                {selectedDepartment ? 'Dans le département sélectionné' : 'Total des enseignants'}
              </p>
            </CardContent>
          </Card>

          {/* Department Heads Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Chefs de Département</CardTitle>
              <UserCheck className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{departmentHeads.length}</div>
              <p className="text-xs text-muted-foreground">
                {selectedDepartment ? 'Dans le département sélectionné' : 'Total des chefs'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Data Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Departments List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Départements
              </CardTitle>
              <CardDescription>Liste de tous les départements</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <div className="space-y-2">
                  {departments.map(dept => (
                    <div 
                      key={dept.id} 
                      className={`p-3 rounded-lg border ${
                        selectedDepartment === dept.id 
                          ? 'border-blue-300 bg-blue-50' 
                          : 'border-gray-200'
                      }`}
                    >
                      <div className="font-medium">{dept.name}</div>
                      <div className="text-sm text-gray-600">ID: {dept.id}</div>
                    </div>
                  ))}
                  {departments.length === 0 && (
                    <p className="text-gray-500 text-center py-4">Aucun département trouvé</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Students List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5" />
                Étudiants ({students.length})
              </CardTitle>
              <CardDescription>
                {selectedDepartment 
                  ? `Étudiants du département sélectionné` 
                  : 'Liste de tous les étudiants'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {students.map(student => (
                    <div key={student.id} className="p-3 rounded-lg border border-gray-200">
                      <div className="font-medium">
                        {student.prenom} {student.nom}
                      </div>
                      <div className="text-sm text-gray-600">{student.email}</div>
                      <div className="text-xs text-gray-500">
                        ID: {student.id} | Rôle: {student.role}
                      </div>
                    </div>
                  ))}
                  {students.length === 0 && (
                    <p className="text-gray-500 text-center py-4">Aucun étudiant trouvé</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Teachers List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Enseignants ({teachers.length})
              </CardTitle>
              <CardDescription>
                {selectedDepartment 
                  ? `Enseignants du département sélectionné` 
                  : 'Liste de tous les enseignants'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {teachers.map(teacher => (
                    <div key={teacher.id} className="p-3 rounded-lg border border-gray-200">
                      <div className="font-medium">
                        {teacher.prenom} {teacher.nom}
                      </div>
                      <div className="text-sm text-gray-600">{teacher.email}</div>
                      <div className="text-xs text-gray-500">
                        ID: {teacher.id} | Rôle: {teacher.role}
                      </div>
                    </div>
                  ))}
                  {teachers.length === 0 && (
                    <p className="text-gray-500 text-center py-4">Aucun enseignant trouvé</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Department Heads List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserCheck className="h-5 w-5" />
                Chefs de Département ({departmentHeads.length})
              </CardTitle>
              <CardDescription>
                {selectedDepartment 
                  ? `Chefs du département sélectionné` 
                  : 'Liste de tous les chefs de département'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : (
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {departmentHeads.map(deptHead => (
                    <div key={deptHead.id} className="p-3 rounded-lg border border-gray-200">
                      <div className="font-medium">
                        {deptHead.firstName ? `${deptHead.firstName} ${deptHead.lastName}` : 'Nom non disponible'}
                      </div>
                      <div className="text-sm text-gray-600">
                        {deptHead.email || 'Email non disponible'}
                      </div>
                      <div className="text-xs text-gray-500">
                        ID: {deptHead.id}
                        {deptHead.departmentHeadInfo?.department?.name && 
                          ` | Département: ${deptHead.departmentHeadInfo.department.name}`
                        }
                      </div>
                    </div>
                  ))}
                  {departmentHeads.length === 0 && (
                    <p className="text-gray-500 text-center py-4">Aucun chef de département trouvé</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <div className="mt-8 flex justify-center">
          <Link href="/register">
            <Button>
              Retour à l'inscription
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}