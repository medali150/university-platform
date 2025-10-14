'use client'

import { useState, useEffect } from 'react'
import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { BookOpen, Plus, Edit, Trash2, Loader2, Search, X } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'sonner'

interface Subject {
  id: number
  name: string
  coefficient: number
  levelId: string
  teacherId?: string
  level?: {
    id: string
    name: string
    specialty?: {
      id: string
      name: string
      department?: {
        id: string
        name: string
      }
    }
  }
  teacher?: {
    id: string
    user?: {
      id: number
      nom: string
      prenom: string
      email: string
    }
    department?: {
      id: string
      name: string
    }
  }
  createdAt?: string
  updatedAt?: string
}

interface SubjectFormData {
  name: string
  coefficient: number
  levelId: string
  teacherId?: string
}

export default function SubjectsPage() {
  const { user, isLoading: authLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [levels, setLevels] = useState<any[]>([])
  const [teachers, setTeachers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  
  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null)
  const [submitting, setSubmitting] = useState(false)
  
  // Form data
  const [formData, setFormData] = useState<SubjectFormData>({
    name: '',
    coefficient: 1.0,
    levelId: '',
    teacherId: undefined
  })

  // Load subjects and semesters
  useEffect(() => {
    if (user && !authLoading) {
      loadData()
    }
  }, [user, authLoading])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load subjects - API returns { subjects: Subject[] }
      const subjectsResponse = await api.getSubjects()
      // Handle both array and object response
      if (Array.isArray(subjectsResponse)) {
        setSubjects(subjectsResponse)
      } else if (subjectsResponse && subjectsResponse.subjects) {
        setSubjects(subjectsResponse.subjects)
      } else {
        setSubjects([])
      }
      
      // Load helper data (levels and teachers) from department-scoped endpoints
      try {
        const helperData = await api.getSubjectHelperData()
        setLevels(helperData.levels || [])
        setTeachers(helperData.teachers || [])
      } catch (err) {
        console.error('Error loading helper data:', err)
        setLevels([])
        setTeachers([])
      }
      
    } catch (err) {
      console.error('Error loading data:', err)
      setError('Erreur lors du chargement des matières')
      setSubjects([]) // Ensure subjects is always an array
      toast.error('Erreur lors du chargement des matières')
    } finally {
      setLoading(false)
    }
  }

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      coefficient: 1.0,
      levelId: levels.length > 0 ? levels[0].id : '',
      teacherId: undefined
    })
  }

  // Handle create subject
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name || !formData.levelId) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }
    
    try {
      setSubmitting(true)
      
      const newSubject = await api.createSubject({
        name: formData.name,
        coefficient: Number(formData.coefficient),
        levelId: formData.levelId,
        teacherId: formData.teacherId || undefined
      })
      
      // Reload data to get full subject with relations
      await loadData()
      toast.success('Matière créée avec succès')
      setIsCreateDialogOpen(false)
      resetForm()
      
    } catch (err: any) {
      console.error('Error creating subject:', err)
      toast.error(err.message || 'Erreur lors de la création de la matière')
    } finally {
      setSubmitting(false)
    }
  }

  // Handle edit subject
  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedSubject || !formData.name || !formData.levelId) {
      toast.error('Veuillez remplir tous les champs obligatoires')
      return
    }
    
    try {
      setSubmitting(true)
      
      await api.updateSubject(String(selectedSubject.id), {
        name: formData.name,
        coefficient: Number(formData.coefficient),
        levelId: formData.levelId,
        teacherId: formData.teacherId || undefined
      })
      
      // Reload data to get updated subject with relations
      await loadData()
      toast.success('Matière modifiée avec succès')
      setIsEditDialogOpen(false)
      setSelectedSubject(null)
      resetForm()
      
    } catch (err: any) {
      console.error('Error updating subject:', err)
      toast.error(err.message || 'Erreur lors de la modification de la matière')
    } finally {
      setSubmitting(false)
    }
  }

  // Handle delete subject
  const handleDelete = async () => {
    if (!selectedSubject) return
    
    try {
      setSubmitting(true)
      
      await api.deleteSubject(String(selectedSubject.id))
      
      setSubjects(subjects.filter(s => s.id !== selectedSubject.id))
      toast.success('Matière supprimée avec succès')
      setIsDeleteDialogOpen(false)
      setSelectedSubject(null)
      
    } catch (err: any) {
      console.error('Error deleting subject:', err)
      toast.error(err.message || 'Erreur lors de la suppression de la matière')
    } finally {
      setSubmitting(false)
    }
  }

  // Open edit dialog
  const openEditDialog = (subject: Subject) => {
    setSelectedSubject(subject)
    setFormData({
      name: subject.name,
      coefficient: subject.coefficient,
      levelId: subject.levelId,
      teacherId: subject.teacherId
    })
    setIsEditDialogOpen(true)
  }

  // Open delete dialog
  const openDeleteDialog = (subject: Subject) => {
    setSelectedSubject(subject)
    setIsDeleteDialogOpen(true)
  }

  // Filter subjects by search term
  const filteredSubjects = Array.isArray(subjects) 
    ? subjects.filter(subject =>
        subject.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : []

  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <BookOpen className="h-8 w-8" />
            Gestion des Matières
          </h1>
          <p className="text-muted-foreground">
            Créer, modifier et supprimer les matières du département
          </p>
        </div>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>
              <Plus className="h-4 w-4 mr-2" />
              Nouvelle Matière
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Créer une nouvelle matière</DialogTitle>
              <DialogDescription>
                Remplissez les informations de la nouvelle matière
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nom de la matière *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Ex: Programmation Web"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="coefficient">Coefficient *</Label>
                  <Input
                    id="coefficient"
                    type="number"
                    step="0.5"
                    min="0.5"
                    max="10"
                    value={formData.coefficient}
                    onChange={(e) => setFormData({ ...formData, coefficient: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="level">Spécialité *</Label>
                  <select
                    id="level"
                    className="w-full px-3 py-2 border rounded-md"
                    value={formData.levelId}
                    onChange={(e) => setFormData({ ...formData, levelId: e.target.value })}
                    required
                  >
                    <option value="">Sélectionner une spécialité</option>
                    {levels.map(level => (
                      <option key={level.id} value={level.id}>
                        {level.nom || level.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="teacher">Enseignant (optionnel)</Label>
                <select
                  id="teacher"
                  className="w-full px-3 py-2 border rounded-md"
                  value={formData.teacherId || ''}
                  onChange={(e) => setFormData({ ...formData, teacherId: e.target.value || undefined })}
                >
                  <option value="">Aucun enseignant</option>
                  {teachers.map(teacher => (
                    <option key={teacher.id} value={teacher.id}>
                      {teacher.user?.prenom} {teacher.user?.nom}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsCreateDialogOpen(false)
                    resetForm()
                  }}
                  disabled={submitting}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={submitting}>
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Création...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      Créer
                    </>
                  )}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher par nom ou code..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-10"
            />
            {searchTerm && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1 h-8 w-8 p-0"
                onClick={() => setSearchTerm('')}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Subjects List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin" />
            <p className="text-sm text-muted-foreground">Chargement des matières...</p>
          </div>
        </div>
      ) : error ? (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
            <Button onClick={loadData} className="mt-4" variant="outline">
              Réessayer
            </Button>
          </CardContent>
        </Card>
      ) : filteredSubjects.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                {searchTerm ? 'Aucune matière trouvée' : 'Aucune matière'}
              </h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm 
                  ? 'Aucune matière ne correspond à votre recherche'
                  : 'Commencez par créer votre première matière'
                }
              </p>
              {!searchTerm && (
                <Button onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Créer une matière
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSubjects.map((subject) => (
            <Card key={subject.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-lg">{subject.name}</span>
                  <span className="text-sm font-mono text-muted-foreground bg-gray-100 px-2 py-1 rounded">
                    Coef: {subject.coefficient}
                  </span>
                </CardTitle>
                <CardDescription>
                  {subject.level?.name || 'Spécialité non définie'}
                  {subject.teacher && ` • Prof: ${subject.teacher.user?.prenom} ${subject.teacher.user?.nom}`}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground mb-4">
                  <div><strong>Spécialité:</strong> {subject.level?.specialty?.name || 'N/A'}</div>
                  {subject.level?.specialty?.department && (
                    <div><strong>Département:</strong> {subject.level.specialty.department.name}</div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => openEditDialog(subject)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Modifier
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    onClick={() => openDeleteDialog(subject)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Edit Dialog */}
      {isEditDialogOpen && (
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Modifier la matière</DialogTitle>
              <DialogDescription>
                Modifiez les informations de la matière
              </DialogDescription>
            </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Nom de la matière *</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-coefficient">Coefficient *</Label>
                <Input
                  id="edit-coefficient"
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="10"
                  value={formData.coefficient}
                  onChange={(e) => setFormData({ ...formData, coefficient: parseFloat(e.target.value) })}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="edit-level">Spécialité *</Label>
                <select
                  id="edit-level"
                  className="w-full px-3 py-2 border rounded-md"
                  value={formData.levelId}
                  onChange={(e) => setFormData({ ...formData, levelId: e.target.value })}
                  required
                >
                  <option value="">Sélectionner une spécialité</option>
                  {levels.map(level => (
                    <option key={level.id} value={level.id}>
                      {level.nom || level.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="edit-teacher">Enseignant (optionnel)</Label>
              <select
                id="edit-teacher"
                className="w-full px-3 py-2 border rounded-md"
                value={formData.teacherId || ''}
                onChange={(e) => setFormData({ ...formData, teacherId: e.target.value || undefined })}
              >
                <option value="">Aucun enseignant</option>
                {teachers.map(teacher => (
                  <option key={teacher.id} value={teacher.id}>
                    {teacher.user?.prenom} {teacher.user?.nom}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsEditDialogOpen(false)
                  setSelectedSubject(null)
                  resetForm()
                }}
                disabled={submitting}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Modification...
                  </>
                ) : (
                  <>
                    <Edit className="h-4 w-4 mr-2" />
                    Modifier
                  </>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
      )}

      {/* Delete Confirmation Dialog */}
      {isDeleteDialogOpen && (
        <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
            <AlertDialogTitle>Confirmer la suppression</AlertDialogTitle>
            <AlertDialogDescription>
              Êtes-vous sûr de vouloir supprimer la matière "{selectedSubject?.name}" ?
              Cette action est irréversible.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={submitting}>Annuler</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={submitting}
              className="bg-red-600 hover:bg-red-700"
            >
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Suppression...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Supprimer
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      )}
    </div>
  )
}
