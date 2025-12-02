'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'
import { toast } from 'sonner'
import { Building, Users, Plus, Edit, Trash2, Search, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { Room } from '@/types/api'

export default function RoomsManagementPage() {
  const { user, isLoading: authLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  const [rooms, setRooms] = useState<Room[]>([])
  const [filteredRooms, setFilteredRooms] = useState<Room[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [buildingFilter, setBuildingFilter] = useState('all')
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingRoom, setEditingRoom] = useState<Room | null>(null)
  const [formData, setFormData] = useState({
    code: '',
    type: 'LECTURE',
    capacity: 30,
    building: ''
  })

  useEffect(() => {
    if (user && !authLoading) {
      loadRooms()
    }
  }, [user, authLoading])

  useEffect(() => {
    filterRooms()
  }, [rooms, searchQuery, typeFilter, buildingFilter])

  const loadRooms = async () => {
    try {
      setLoading(true)
      const data = await api.getRooms()
      setRooms(data)
    } catch (error: any) {
      console.error('Error loading rooms:', error)
      toast.error(error.message || 'Erreur lors du chargement des salles')
    } finally {
      setLoading(false)
    }
  }

  const filterRooms = () => {
    let filtered = [...rooms]

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(room =>
        (room.code && room.code.toLowerCase().includes(query)) ||
        (room.building && room.building.toLowerCase().includes(query))
      )
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter(room => room.type === typeFilter)
    }

    if (buildingFilter !== 'all') {
      filtered = filtered.filter(room => room.building === buildingFilter)
    }

    setFilteredRooms(filtered)
  }

  const openCreateDialog = () => {
    setEditingRoom(null)
    setFormData({ code: '', type: 'LECTURE', capacity: 30, building: '' })
    setIsDialogOpen(true)
  }

  const openEditDialog = (room: Room) => {
    setEditingRoom(room)
    setFormData({
      code: room.code,
      type: room.type,
      capacity: room.capacity,
      building: room.building || ''
    })
    setIsDialogOpen(true)
  }

  const handleSubmit = async () => {
    try {
      if (!formData.code || !formData.type || !formData.capacity) {
        toast.error('Veuillez remplir tous les champs obligatoires')
        return
      }

      if (editingRoom) {
        await api.updateRoom(editingRoom.id, formData)
        toast.success('Salle mise à jour avec succès')
      } else {
        await api.createRoom(formData)
        toast.success('Salle créée avec succès')
      }

      setIsDialogOpen(false)
      loadRooms()
    } catch (error: any) {
      console.error('Error saving room:', error)
      toast.error(error.message || 'Erreur lors de l\'enregistrement')
    }
  }

  const handleDelete = async (room: Room) => {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer la salle ${room.code} ?`)) {
      return
    }

    try {
      await api.deleteRoom(room.id)
      toast.success('Salle supprimée avec succès')
      loadRooms()
    } catch (error: any) {
      console.error('Error deleting room:', error)
      toast.error(error.message || 'Erreur lors de la suppression')
    }
  }

  const uniqueBuildings = Array.from(new Set(rooms.map(r => r.building).filter(Boolean)))

  const getTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'LECTURE': 'Cours',
      'LAB': 'Laboratoire',
      'EXAM': 'Examen',
      'OTHER': 'Autre'
    }
    return labels[type] || type
  }

  const getTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'LECTURE': 'bg-blue-100 text-blue-800',
      'LAB': 'bg-green-100 text-green-800',
      'EXAM': 'bg-orange-100 text-orange-800',
      'OTHER': 'bg-gray-100 text-gray-800'
    }
    return colors[type] || colors.OTHER
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[600px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard/department-head">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour au tableau de bord
          </Button>
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Gestion des Salles</h1>
            <p className="text-muted-foreground mt-1">Gérez les salles de classe du département</p>
          </div>
          <Button onClick={openCreateDialog}>
            <Plus className="mr-2 h-4 w-4" />
            Nouvelle Salle
          </Button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Salles</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{rooms.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Cours</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {rooms.filter(r => r.type === 'LECTURE').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Laboratoires</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {rooms.filter(r => r.type === 'LAB').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Capacité Totale</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {rooms.reduce((sum, r) => sum + r.capacity, 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher une salle..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger>
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

            <Select value={buildingFilter} onValueChange={setBuildingFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Bâtiment" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les bâtiments</SelectItem>
                {uniqueBuildings.map((building) => (
                  <SelectItem key={building} value={building!}>
                    {building}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Rooms Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRooms.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">Aucune salle trouvée</p>
            </CardContent>
          </Card>
        ) : (
          filteredRooms.map((room) => (
            <Card key={room.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl">{room.code}</CardTitle>
                    <Badge className={`mt-2 ${getTypeColor(room.type)}`}>
                      {getTypeLabel(room.type)}
                    </Badge>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditDialog(room)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(room)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <span>{room.capacity} places</span>
                  </div>
                  {room.building && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Building className="h-4 w-4" />
                      <span>{room.building}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingRoom ? 'Modifier la salle' : 'Nouvelle salle'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="code">Code de la salle *</Label>
              <Input
                id="code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                placeholder="Ex: A101, LAB-01"
              />
            </div>

            <div>
              <Label htmlFor="type">Type *</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => setFormData({ ...formData, type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="LECTURE">Cours</SelectItem>
                  <SelectItem value="LAB">Laboratoire</SelectItem>
                  <SelectItem value="EXAM">Examen</SelectItem>
                  <SelectItem value="OTHER">Autre</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="capacity">Capacité *</Label>
              <Input
                id="capacity"
                type="number"
                value={formData.capacity}
                onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) || 0 })}
                min="1"
              />
            </div>

            <div>
              <Label htmlFor="building">Bâtiment</Label>
              <Input
                id="building"
                value={formData.building}
                onChange={(e) => setFormData({ ...formData, building: e.target.value })}
                placeholder="Ex: Bâtiment A, Campus Nord"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleSubmit}>
              {editingRoom ? 'Mettre à jour' : 'Créer'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
