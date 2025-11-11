'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  Calendar, 
  Plus,
  Save,
  AlertCircle,
  CheckCircle,
  Edit,
  Trash,
  RefreshCw
} from 'lucide-react';
import { TimetableAPI, DayOfWeek } from '@/lib/timetable-api';

// Time slots matching the photo (8h30 to 17h40)
const TIME_SLOTS = [
  { id: 'slot1', start: '08:30', end: '10:00', label: '8h30 à 10h00' },
  { id: 'slot2', start: '10:10', end: '11:40', label: '10h10 à 11h40' },
  { id: 'slot3', start: '11:50', end: '13:20', label: '11h50 à 13h20' },
  { id: 'slot4', start: '14:30', end: '16:00', label: '14h30 à 16h00' },
  { id: 'slot5', start: '16:10', end: '17:40', label: '16h10 à 17h40' }
];

const DAYS_OF_WEEK = [
  { id: DayOfWeek.MONDAY, label: 'Lundi', short: 'Lun' },
  { id: DayOfWeek.TUESDAY, label: 'Mardi', short: 'Mar' },
  { id: DayOfWeek.WEDNESDAY, label: 'Mercredi', short: 'Mer' },
  { id: DayOfWeek.THURSDAY, label: 'Jeudi', short: 'Jeu' },
  { id: DayOfWeek.FRIDAY, label: 'Vendredi', short: 'Ven' },
  { id: DayOfWeek.SATURDAY, label: 'Samedi', short: 'Sam' }
];

interface CellSession {
  day: DayOfWeek;
  timeSlot: typeof TIME_SLOTS[0];
}

interface EditingSession {
  id: string;
  subject_id: string;
  teacher_id: string;
  room_id: string;
  day: DayOfWeek;
  timeSlot: typeof TIME_SLOTS[0];
}

export default function InteractiveTimetableCreator() {
  const [loading, setLoading] = useState(false);
  const [resources, setResources] = useState<any>({
    subjects: [],
    groups: [],
    teachers: [],
    rooms: []
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedCell, setSelectedCell] = useState<CellSession | null>(null);
  const [editingSession, setEditingSession] = useState<EditingSession | null>(null);
  const [currentWeekStart, setCurrentWeekStart] = useState<string>(() => TimetableAPI.getWeekStart());
  const [weekSchedule, setWeekSchedule] = useState<any>(null);
  const [selectedGroup, setSelectedGroup] = useState<string>('');

  // Form state for session creation
  const [sessionForm, setSessionForm] = useState({
    subject_id: '',
    teacher_id: '',
    room_id: '',
    semester_end: '2026-06-30'  // Default to end of academic year
  });

  // Load resources on mount
  useEffect(() => {
    loadResources();
  }, []);

  // Load schedule when group or week changes
  useEffect(() => {
    if (selectedGroup) {
      loadWeekSchedule();
    }
  }, [selectedGroup, currentWeekStart]);

  const loadResources = async () => {
    try {
      setLoading(true);
      const data = await TimetableAPI.getAvailableResources();
      setResources(data);
      
      // Pre-select first group
      if (data.groups.length > 0) {
        setSelectedGroup(data.groups[0].id);
      }
      
      // Pre-select first items in form
      if (data.subjects.length > 0) {
        setSessionForm(prev => ({ ...prev, subject_id: data.subjects[0].id }));
      }
      if (data.teachers.length > 0) {
        setSessionForm(prev => ({ ...prev, teacher_id: data.teachers[0].id }));
      }
      if (data.rooms.length > 0) {
        setSessionForm(prev => ({ ...prev, room_id: data.rooms[0].id }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const loadWeekSchedule = async () => {
    if (!selectedGroup) return;
    
    try {
      setLoading(true);
      setError(null);
      const timetable = await TimetableAPI.getGroupWeeklySchedule(selectedGroup, currentWeekStart);
      setWeekSchedule({ timetable });
    } catch (err) {
      console.error('Error loading schedule:', err);
      setError(err instanceof Error ? err.message : 'Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleCellClick = (day: DayOfWeek, timeSlot: typeof TIME_SLOTS[0]) => {
    const existingSession = getCellSession(day, timeSlot);
    
    if (existingSession) {
      // Edit existing session - extract IDs from the session object
      setEditingSession({
        id: existingSession.id,
        subject_id: existingSession.id, // We need to store subject_id separately
        teacher_id: existingSession.id, // We need to store teacher_id separately
        room_id: existingSession.id, // We need to store room_id separately
        day: day,
        timeSlot: timeSlot
      });
      setSessionForm({
        subject_id: existingSession.id, // These should come from actual session data
        teacher_id: existingSession.id,
        room_id: existingSession.id,
        semester_end: '2026-06-30'
      });
    } else {
      setEditingSession(null);
    }
    
    setSelectedCell({ day, timeSlot });
    setIsDialogOpen(true);
    setError(null);
    setSuccess(null);
  };

  const handleCreateSession = async () => {
    if (!selectedCell || !selectedGroup) {
      setError('Veuillez sélectionner un groupe');
      return;
    }

    if (!sessionForm.subject_id || !sessionForm.teacher_id || !sessionForm.room_id) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const scheduleData = {
        subject_id: sessionForm.subject_id,
        group_id: selectedGroup,
        teacher_id: sessionForm.teacher_id,
        room_id: sessionForm.room_id,
        day_of_week: TimetableAPI.dayOfWeekToFrench(selectedCell.day),
        start_time: selectedCell.timeSlot.start,
        end_time: selectedCell.timeSlot.end,
        recurrence: 'WEEKLY',  // Always create recurring schedules
        semester_start: currentWeekStart,
        semester_end: sessionForm.semester_end
      };

      const result = await TimetableAPI.createSemesterSchedule(scheduleData);

      if (result.success) {
        setSuccess(`✅ Session créée avec succès!`);
        setIsDialogOpen(false);
        await loadWeekSchedule();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la création');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSession = async () => {
    if (!editingSession) return;

    try {
      setLoading(true);
      setError(null);

      await TimetableAPI.updateSession(editingSession.id, {
        room_id: sessionForm.room_id
      });

      setSuccess('✅ Session modifiée avec succès!');
      setIsDialogOpen(false);
      setEditingSession(null);
      await loadWeekSchedule();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la modification');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async () => {
    if (!editingSession) return;

    if (!confirm('Voulez-vous vraiment supprimer cette session?')) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await TimetableAPI.cancelSession(editingSession.id);

      setSuccess('✅ Session supprimée avec succès!');
      setIsDialogOpen(false);
      setEditingSession(null);
      await loadWeekSchedule();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (editingSession) {
      await handleUpdateSession();
    } else {
      await handleCreateSession();
    }
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    if (direction === 'next') {
      setCurrentWeekStart(TimetableAPI.getNextWeekStart(currentWeekStart));
    } else {
      setCurrentWeekStart(TimetableAPI.getPreviousWeekStart(currentWeekStart));
    }
  };

  const goToCurrentWeek = () => {
    setCurrentWeekStart(TimetableAPI.getWeekStart());
  };

  const formatWeekRange = () => {
    const start = new Date(currentWeekStart);
    const end = new Date(TimetableAPI.getWeekEnd(currentWeekStart));
    
    return `${start.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })} - ${end.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}`;
  };

  const getCellSession = (day: DayOfWeek, timeSlot: typeof TIME_SLOTS[0]) => {
    if (!weekSchedule?.timetable) return null;
    
    const dayLabel = day; // DayOfWeek is already in French
    const daySessions = weekSchedule.timetable[dayLabel];
    
    if (!daySessions || !Array.isArray(daySessions)) return null;
    
    return daySessions.find((session: any) => 
      session.startTime === timeSlot.start && session.endTime === timeSlot.end
    );
  };

  if (!resources) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-muted-foreground mb-4" />
          <p className="text-muted-foreground">Chargement des ressources...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Calendar className="h-6 w-6" />
            Créer l'Emploi du Temps
          </CardTitle>
          <CardDescription>
            Cliquez sur une case pour créer un cours pour la semaine en cours
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Success Message */}
      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            {/* Group Selection */}
            <div>
              <Label>Groupe</Label>
              <Select value={selectedGroup} onValueChange={setSelectedGroup}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un groupe" />
                </SelectTrigger>
                <SelectContent>
                  {resources.groups.map((group: any) => {
                    // Safely extract niveau and specialite names
                    const niveauName = typeof group.niveau === 'object' ? group.niveau?.nom : group.niveau;
                    const specialiteName = typeof group.specialite === 'object' ? group.specialite?.nom : group.specialite;
                    
                    return (
                      <SelectItem key={group.id} value={group.id}>
                        {group.nom}
                        {niveauName && ` - ${niveauName}`}
                        {specialiteName && ` (${specialiteName})`}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>

            {/* Week Navigation */}
            <div>
              <Label>Semaine</Label>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => navigateWeek('prev')}
                  disabled={loading}
                >
                  ←
                </Button>
                <span className="text-sm text-center flex-1">{formatWeekRange()}</span>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => navigateWeek('next')}
                  disabled={loading}
                >
                  →
                </Button>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={goToCurrentWeek}
                disabled={loading}
              >
                Aujourd'hui
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={loadWeekSchedule}
                disabled={loading}
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Timetable Grid */}
      <Card>
        <CardContent className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300">
              <thead>
                <tr>
                  <th className="border border-gray-300 p-3 bg-gray-100 text-left font-semibold w-32">
                    Horaires
                  </th>
                  {DAYS_OF_WEEK.map((day) => (
                    <th 
                      key={day.id} 
                      className="border border-gray-300 p-3 bg-gray-100 text-center font-semibold min-w-[150px]"
                    >
                      <div>{day.label}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map((timeSlot) => (
                  <tr key={timeSlot.id}>
                    <td className="border border-gray-300 p-3 bg-gray-50 font-medium text-sm align-top">
                      <div className="text-center">
                        <div className="font-bold">{timeSlot.start}</div>
                        <div className="text-xs text-muted-foreground">à</div>
                        <div className="font-bold">{timeSlot.end}</div>
                      </div>
                    </td>
                    {DAYS_OF_WEEK.map((day) => {
                      const session = getCellSession(day.id, timeSlot);
                      return (
                        <td 
                          key={`${day.id}-${timeSlot.id}`}
                          className={`border border-gray-300 p-2 align-top cursor-pointer transition-colors ${
                            session 
                              ? 'bg-blue-50 hover:bg-blue-100' 
                              : 'hover:bg-yellow-50'
                          }`}
                          style={{ minHeight: '100px' }}
                          onClick={() => handleCellClick(day.id, timeSlot)}
                        >
                          {session ? (
                            <div className="h-full min-h-[90px]">
                              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-3 h-full shadow-sm">
                                <div className="font-bold text-sm mb-2 line-clamp-2">
                                  {session.subject}
                                </div>
                                <div className="text-xs opacity-90 space-y-1">
                                  <div className="truncate">
                                    📍 {session.room}
                                  </div>
                                  <div className="truncate">
                                    👨‍🏫 {session.teacher}
                                  </div>
                                  <div className="truncate">
                                    👥 {session.group}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="h-full min-h-[90px] flex flex-col items-center justify-center text-gray-400 hover:text-blue-600 transition-colors">
                              <Plus className="h-8 w-8 mb-2" />
                              <span className="text-xs font-medium">Cliquer pour ajouter</span>
                            </div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Info */}
      <Alert className="border-blue-200 bg-blue-50">
        <AlertCircle className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>Comment utiliser:</strong>
          <ul className="mt-2 space-y-1 text-sm">
            <li>• Sélectionnez un groupe ci-dessus</li>
            <li>• Cliquez sur une case vide pour créer un cours</li>
            <li>• Le cours sera créé pour la semaine en cours</li>
            <li>• Les emplois du temps des enseignants et étudiants seront mis à jour automatiquement</li>
          </ul>
        </AlertDescription>
      </Alert>

      {/* Session Creation/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingSession ? 'Modifier le Cours' : 'Créer un Cours'}</DialogTitle>
            <DialogDescription>
              {selectedCell && (
                <>
                  {TimetableAPI.dayOfWeekToFrench(selectedCell.day)} - {selectedCell.timeSlot.label}
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Matière */}
            <div>
              <Label htmlFor="subject">Matière *</Label>
              <Select
                value={sessionForm.subject_id}
                onValueChange={(value) => setSessionForm(prev => ({ ...prev, subject_id: value }))}
                disabled={!!editingSession}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {resources.subjects.map((subject: any) => (
                    <SelectItem key={subject.id} value={subject.id}>
                      {subject.nom} {subject.code && `(${subject.code})`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Enseignant */}
            <div>
              <Label htmlFor="teacher">Enseignant *</Label>
              <Select
                value={sessionForm.teacher_id}
                onValueChange={(value) => setSessionForm(prev => ({ ...prev, teacher_id: value }))}
                disabled={!!editingSession}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {resources.teachers.map((teacher: any) => (
                    <SelectItem key={teacher.id} value={teacher.id}>
                      {teacher.prenom} {teacher.nom}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Salle */}
            <div>
              <Label htmlFor="room">Salle *</Label>
              <Select
                value={sessionForm.room_id}
                onValueChange={(value) => setSessionForm(prev => ({ ...prev, room_id: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {resources.rooms.map((room: any) => (
                    <SelectItem key={room.id} value={room.id}>
                      {room.code} ({room.type}) - {room.capacite} places
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Groupe (read-only display) */}
            <div>
              <Label>Groupe</Label>
              <Input 
                value={resources.groups.find((g: any) => g.id === selectedGroup)?.nom || ''} 
                disabled 
                className="bg-gray-50"
              />
            </div>

            {/* Info message about recurring schedules */}
            {!editingSession && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800">
                  ℹ️ Ce cours sera créé automatiquement pour toutes les semaines jusqu'à la fin du semestre ({sessionForm.semester_end})
                </p>
              </div>
            )}
          </div>

          <div className="flex justify-between gap-2 pt-4">
            <div>
              {editingSession && (
                <Button 
                  variant="destructive" 
                  onClick={handleDeleteSession} 
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Suppression...
                    </>
                  ) : (
                    <>
                      <Trash className="mr-2 h-4 w-4" />
                      Supprimer
                    </>
                  )}
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Annuler
              </Button>
              <Button onClick={handleSubmit} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {editingSession ? 'Modification...' : 'Création...'}
                  </>
                ) : (
                  <>
                    {editingSession ? (
                      <>
                        <Edit className="mr-2 h-4 w-4" />
                        Modifier
                      </>
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        Créer le Cours
                      </>
                    )}
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
