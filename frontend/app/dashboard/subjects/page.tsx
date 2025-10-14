'use client'

import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BookOpen, Users, GraduationCap, Search, Plus, Edit, Trash2, ChevronLeft, ChevronRight, AlertTriangle, Loader2 } from 'lucide-react'
import { useState, useEffect } from 'react'
import { SubjectsAPI } from '@/lib/subjects-api'
import { Subject } from '@/types/api'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'

// Simple toast notification since sonner isn't installed
const toast = {
  success: (message: string) => {
    console.log('Success:', message)
    alert('Succès: ' + message)
  },
  error: (message: string) => {
    console.error('Error:', message)
    alert('Erreur: ' + message)
  }
}

export default function SubjectsPage() {
  const { user, isLoading: authLoading } = useRequireRole(['DEPARTMENT_HEAD', 'ADMIN'] as Role[])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<string>('')
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [subjectsLoading, setSubjectsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
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
  
  // Create subject modal state
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [createForm, setCreateForm] = useState({
    name: '',
    coefficient: 1.0,
    levelId: '',
    teacherId: ''
  })
  const [helperData, setHelperData] = useState<{
    levels: any[]
    teachers: any[]
  }>({ levels: [], teachers: [] })
  const [createLoading, setCreateLoading] = useState(false)
  
  // Edit subject modal state
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null)
  const [editForm, setEditForm] = useState({
    name: '',
    coefficient: 1.0,
    levelId: '',
    teacherId: ''
  })
  const [editLoading, setEditLoading] = useState(false)

  // Load subjects data
  const loadSubjects = async (page = 1, search = '', levelId = '') => {
    try {
      setSubjectsLoading(true)
      setError(null)
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
      setError('Erreur lors du chargement des matières')
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

  // Load helper data for create form
  const loadHelperData = async () => {
    try {
      const data = await SubjectsAPI.getHelperData()
      setHelperData(data)
    } catch (error) {
      console.error('Error loading helper data:', error)
      toast.error('Erreur lors du chargement des données')
    }
  }

  // Handle create subject
  const handleCreateSubject = async () => {
    if (!createForm.name.trim() || !createForm.levelId) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }

    if (createForm.coefficient <= 0) {
      toast.error('Le coefficient doit être supérieur à 0')
      return
    }

    try {
      setCreateLoading(true)
      await SubjectsAPI.createSubject({
        name: createForm.name.trim(),
        coefficient: createForm.coefficient,
        levelId: createForm.levelId,
        teacherId: createForm.teacherId && createForm.teacherId !== 'none' ? createForm.teacherId : undefined
      })
      
      toast.success('Matière créée avec succès')
      setCreateModalOpen(false)
      setCreateForm({ name: '', levelId: '', teacherId: '' })
      loadSubjects()
      loadStats()
    } catch (error) {
      console.error('Error creating subject:', error)
      toast.error('Erreur lors de la création de la matière')
    } finally {
      setCreateLoading(false)
    }
  }

  // Open edit modal
  const openEditModal = (subject: Subject) => {
    setEditingSubject(subject)
    setEditForm({
      name: subject.name,
      coefficient: subject.coefficient || 1.0,
      levelId: subject.levelId || '',
      teacherId: subject.teacherId || ''
    })
    setEditModalOpen(true)
  }

  // Handle edit subject
  const handleEditSubject = async () => {
    if (!editingSubject || !editForm.name.trim() || !editForm.levelId) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }

    if (editForm.coefficient <= 0) {
      toast.error('Le coefficient doit être supérieur à 0')
      return
    }

    try {
      setEditLoading(true)
      await SubjectsAPI.updateSubject(editingSubject.id, {
        name: editForm.name.trim(),
        coefficient: editForm.coefficient,
        levelId: editForm.levelId,
        teacherId: editForm.teacherId && editForm.teacherId !== 'none' ? editForm.teacherId : undefined
      })
      
      toast.success('Matière modifiée avec succès')
      setEditModalOpen(false)
      setEditingSubject(null)
      setEditForm({ name: '', levelId: '', teacherId: '' })
      loadSubjects()
      loadStats()
    } catch (error) {
      console.error('Error updating subject:', error)
      toast.error('Erreur lors de la modification de la matière')
    } finally {
      setEditLoading(false)
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
      if (selectedSubject === id) {
        setSelectedSubject(null)
      }
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
      loadHelperData()
    }
  }, [user, authLoading])

  // Reset form when modal closes
  useEffect(() => {
    if (!createModalOpen) {
      setCreateForm({ name: '', coefficient: 1.0, levelId: '', teacherId: '' })
    }
  }, [createModalOpen])

  // Reset edit form when modal closes
  useEffect(() => {
    if (!editModalOpen) {
      setEditForm({ name: '', coefficient: 1.0, levelId: '', teacherId: '' })
      setEditingSubject(null)
    }
  }, [editModalOpen])

  // Search and filter effects
  useEffect(() => {
    if (!user || authLoading) return

    const delayedSearch = setTimeout(() => {
      loadSubjects(1, searchTerm, selectedLevel === 'all' ? '' : selectedLevel)
    }, 300)

    return () => clearTimeout(delayedSearch)
  }, [searchTerm, selectedLevel, user, authLoading])

  // Page change handler
  const handlePageChange = (newPage: number) => {
    loadSubjects(newPage, searchTerm, selectedLevel)
  }

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) return null

  const selectedSubjectData = selectedSubject ? subjects.find(s => s.id === selectedSubject) : null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestion des Matières</h1>
          <p className="text-muted-foreground">
            Gérez les matières académiques de votre département
          </p>
        </div>
        <Dialog open={createModalOpen} onOpenChange={setCreateModalOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setCreateModalOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Nouvelle Matière
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Créer une nouvelle matière</DialogTitle>
              <DialogDescription>
                Ajoutez une nouvelle matière à votre département
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="subject-name">
                  Nom de la matière <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="subject-name"
                  placeholder="Ex: Mathématiques, Informatique..."
                  value={createForm.name}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="subject-coefficient">
                  Coefficient <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="subject-coefficient"
                  type="number"
                  min="0.1"
                  step="0.1"
                  placeholder="1.0"
                  value={createForm.coefficient}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, coefficient: parseFloat(e.target.value) || 1.0 }))}
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="subject-level">
                  Niveau/Spécialité <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={createForm.levelId || undefined}
                  onValueChange={(value) => setCreateForm(prev => ({ ...prev, levelId: value || '' }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un niveau" />
                  </SelectTrigger>
                  <SelectContent>
                    {helperData.levels.map((level) => (
                      <SelectItem key={level.id} value={level.id}>
                        {level.name} - {level.specialty?.department?.name || 'Département non spécifié'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="subject-teacher">
                  Enseignant (optionnel)
                </Label>
                <Select
                  value={createForm.teacherId || 'none'}
                  onValueChange={(value) => setCreateForm(prev => ({ ...prev, teacherId: value === 'none' ? '' : value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un enseignant" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Aucun enseignant</SelectItem>
                    {helperData.teachers.map((teacher) => (
                      <SelectItem key={teacher.id} value={teacher.id}>
                        {teacher.user?.prenom} {teacher.user?.nom} ({teacher.user?.email})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setCreateModalOpen(false)
                  setCreateForm({ name: '', coefficient: 1.0, levelId: '', teacherId: '' })
                }}
                disabled={createLoading}
              >
                Annuler
              </Button>
              <Button onClick={handleCreateSubject} disabled={createLoading}>
                {createLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Création...
                  </>
                ) : (
                  'Créer la matière'
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Edit Subject Modal */}
        {editModalOpen && (
          <Dialog open={editModalOpen} onOpenChange={setEditModalOpen}>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Modifier la matière</DialogTitle>
                <DialogDescription>
                  Modifiez les informations de la matière
                </DialogDescription>
              </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-subject-name">
                  Nom de la matière <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="edit-subject-name"
                  placeholder="Ex: Mathématiques, Informatique..."
                  value={editForm.name}
                  onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="edit-subject-coefficient">
                  Coefficient <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="edit-subject-coefficient"
                  type="number"
                  min="0.1"
                  step="0.1"
                  placeholder="1.0"
                  value={editForm.coefficient}
                  onChange={(e) => setEditForm(prev => ({ ...prev, coefficient: parseFloat(e.target.value) || 1.0 }))}
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="edit-subject-level">
                  Niveau/Spécialité <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={editForm.levelId || undefined}
                  onValueChange={(value) => setEditForm(prev => ({ ...prev, levelId: value || '' }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un niveau" />
                  </SelectTrigger>
                  <SelectContent>
                    {helperData.levels.map((level) => (
                      <SelectItem key={level.id} value={level.id}>
                        {level.name} - {level.specialty?.department?.name || 'Département non spécifié'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="edit-subject-teacher">
                  Enseignant (optionnel)
                </Label>
                <Select
                  value={editForm.teacherId || 'none'}
                  onValueChange={(value) => setEditForm(prev => ({ ...prev, teacherId: value === 'none' ? '' : value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un enseignant" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Aucun enseignant</SelectItem>
                    {helperData.teachers.map((teacher) => (
                      <SelectItem key={teacher.id} value={teacher.id}>
                        {teacher.user?.prenom} {teacher.user?.nom} ({teacher.user?.email})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setEditModalOpen(false)
                  setEditForm({ name: '', coefficient: 1.0, levelId: '', teacherId: '' })
                  setEditingSubject(null)
                }}
                disabled={editLoading}
              >
                Annuler
              </Button>
              <Button onClick={handleEditSubject} disabled={editLoading}>
                {editLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Modification...
                  </>
                ) : (
                  'Modifier la matière'
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center p-4">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-3" />
            <div>
              <p className="text-red-800 font-medium">Erreur de chargement</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              className="ml-auto"
              onClick={() => loadSubjects()}
            >
              Réessayer
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Matières</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalSubjects}</div>
            <p className="text-xs text-muted-foreground">Toutes spécialités</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Niveaux</CardTitle>
            <GraduationCap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.byLevel.length}</div>
            <p className="text-xs text-muted-foreground">Niveaux couverts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Départements</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.byDepartment.length}</div>
            <p className="text-xs text-muted-foreground">Départements actifs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.byTeacher.length}</div>
            <p className="text-xs text-muted-foreground">Enseignants assignés</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Subjects List */}
        <Card>
          <CardHeader>
            <CardTitle>Liste des Matières</CardTitle>
            <CardDescription>
              {pagination.total} matière{pagination.total > 1 ? 's' : ''} au total
            </CardDescription>
            <div className="flex items-center space-x-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher une matière..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Niveau" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les niveaux</SelectItem>
                  {helperData.levels.map((level) => (
                    <SelectItem key={level.id} value={level.id}>
                      {level.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            {subjectsLoading ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 className="h-6 w-6 animate-spin mr-2" />
                <span className="text-muted-foreground">Chargement des matières...</span>
              </div>
            ) : subjects.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground">
                <BookOpen className="mx-auto h-12 w-12 mb-4" />
                <p>Aucune matière trouvée</p>
                {searchTerm && (
                  <p className="text-sm">Essayez de modifier vos critères de recherche</p>
                )}
              </div>
            ) : (
              <>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {subjects.map((subject) => (
                    <div
                      key={subject.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                        selectedSubject === subject.id ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                      onClick={() => setSelectedSubject(subject.id)}
                    >
                      <div className="flex items-start justify-between space-x-3">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium truncate">{subject.name}</h4>
                          <p className="text-sm text-muted-foreground truncate">
                            {subject.level?.name || 'Niveau non spécifié'} • 
                            {subject.level?.specialty?.department?.name || 'Département non spécifié'}
                          </p>
                          {subject.teacher?.user && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Enseignant: {subject.teacher.user.prenom} {subject.teacher.user.nom}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center space-x-1">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              openEditModal(subject)
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteSubject(subject.id)
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {pagination.totalPages > 1 && (
                  <div className="flex items-center justify-between mt-4 pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Page {pagination.page} sur {pagination.totalPages}
                    </p>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={pagination.page <= 1}
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(pagination.page + 1)}
                        disabled={pagination.page >= pagination.totalPages}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Subject Detail */}
        <Card>
          <CardHeader>
            <CardTitle>
              {selectedSubjectData ? 'Détail de la Matière' : 'Sélectionnez une Matière'}
            </CardTitle>
            {selectedSubjectData && (
              <CardDescription>{selectedSubjectData.name}</CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {selectedSubjectData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Nom</label>
                    <p className="font-medium">{selectedSubjectData.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Coefficient</label>
                    <p className="font-medium">{selectedSubjectData.coefficient || 1.0}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Niveau</label>
                    <p className="font-medium">{selectedSubjectData.level?.name || 'Non spécifié'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Département</label>
                    <p className="font-medium">
                      {selectedSubjectData.level?.specialty?.department?.name || 'Non spécifié'}
                    </p>
                  </div>
                </div>

                {selectedSubjectData.teacher?.user && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Enseignant Assigné</label>
                    <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium">
                        {selectedSubjectData.teacher.user.prenom} {selectedSubjectData.teacher.user.nom}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {selectedSubjectData.teacher.user.email}
                      </p>
                      {selectedSubjectData.teacher.department && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Département: {selectedSubjectData.teacher.department.name}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                <div className="border-t pt-4 space-y-2">
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => selectedSubjectData && openEditModal(selectedSubjectData)}
                  >
                    <Edit className="mr-2 h-4 w-4" />
                    Modifier la Matière
                  </Button>
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => handleDeleteSubject(selectedSubjectData.id)}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Supprimer la Matière
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <BookOpen className="mx-auto h-12 w-12 mb-4" />
                <p>Sélectionnez une matière pour voir les détails</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Statistics Section */}
      {stats.totalSubjects > 0 && (
        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Répartition par Niveau</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {stats.byLevel.map((item) => (
                  <div key={item.levelName} className="flex justify-between items-center">
                    <span className="text-sm">{item.levelName}</span>
                    <Badge variant="secondary">{item.count}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Répartition par Département</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {stats.byDepartment.map((item) => (
                  <div key={item.departmentName} className="flex justify-between items-center">
                    <span className="text-sm">{item.departmentName}</span>
                    <Badge variant="secondary">{item.count}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Charge par Enseignant</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {stats.byTeacher.slice(0, 5).map((item) => (
                  <div key={item.teacherName} className="flex justify-between items-center">
                    <span className="text-sm truncate">{item.teacherName}</span>
                    <Badge variant="secondary">{item.count}</Badge>
                  </div>
                ))}
                {stats.byTeacher.length > 5 && (
                  <p className="text-xs text-muted-foreground">
                    et {stats.byTeacher.length - 5} autre{stats.byTeacher.length - 5 > 1 ? 's' : ''}...
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}