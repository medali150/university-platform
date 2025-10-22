'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
  X,
  Edit,
  Trash,
  RefreshCw
} from 'lucide-react';
import TimetableAPI, { 
  SemesterScheduleCreate, 
  DayOfWeek, 
  RecurrenceType,
  AvailableResources,
  TimetableResponse 
} from '@/lib/timetable-api';

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
  matiere_id: string;
  enseignant_id: string;
  salle_id: string;
  day: DayOfWeek;
  timeSlot: typeof TIME_SLOTS[0];
}

export default function InteractiveTimetableCreator() {
  const [loading, setLoading] = useState(false);
  const [resources, setResources] = useState<AvailableResources>({
    matieres: [],
    groupes: [],
    enseignants: [],
    salles: []
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedCell, setSelectedCell] = useState<CellSession | null>(null);
  const [editingSession, setEditingSession] = useState<EditingSession | null>(null);
  const [currentWeekStart, setCurrentWeekStart] = useState<string>(() => {
    return TimetableAPI.getWeekStart(new Date());
  });
  const [weekSchedule, setWeekSchedule] = useState<TimetableResponse | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string>('');

  // Form state for session creation
  const [sessionForm, setSessionForm] = useState({
    matiere_id: '',
    enseignant_id: '',
    salle_id: '',
    recurrence_type: RecurrenceType.WEEKLY,
    semester_start: '2025-09-01',
    semester_end: '2025-12-31'
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
      if (data.groupes.length > 0) {
        setSelectedGroup(data.groupes[0].id);
      }
      
      // Pre-select first items in form
      if (data.matieres.length > 0) {
        setSessionForm(prev => ({ ...prev, matiere_id: data.matieres[0].id }));
      }
      if (data.enseignants.length > 0) {
        setSessionForm(prev => ({ ...prev, enseignant_id: data.enseignants[0].id }));
      }
      if (data.salles.length > 0) {
        setSessionForm(prev => ({ ...prev, salle_id: data.salles[0].id }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const loadWeekSchedule = async () => {
    if (!selectedGroup) {
      console.log('No group selected, skipping load');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      console.log('Loading schedule for group:', selectedGroup, 'week:', currentWeekStart);
      const schedule = await TimetableAPI.getGroupWeeklySchedule(selectedGroup, currentWeekStart);
      console.log('Schedule loaded successfully:', schedule);
      console.log('Timetable data:', JSON.stringify(schedule.timetable, null, 2));
      setWeekSchedule(schedule);
    } catch (err) {
      console.error('Error loading schedule:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to load schedule';
      console.error('Error details:', errorMessage);
      setError(`Erreur de chargement: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const getWeekEnd = (weekStart: string): string => {
    const date = new Date(weekStart);
    date.setDate(date.getDate() + 6);
    return date.toISOString().split('T')[0];
  };

  const handleCellClick = (day: DayOfWeek, timeSlot: typeof TIME_SLOTS[0]) => {
    const existingSession = getCellSession(day, timeSlot);
    
    if (existingSession) {
      // Edit existing session
      setEditingSession({
        id: existingSession.id,
        matiere_id: existingSession.matiere.id,
        enseignant_id: existingSession.enseignant.id,
        salle_id: existingSession.salle.id,
        day: day,
        timeSlot: timeSlot
      });
      setSessionForm({
        matiere_id: existingSession.matiere.id,
        enseignant_id: existingSession.enseignant.id,
        salle_id: existingSession.salle.id,
        recurrence_type: RecurrenceType.WEEKLY,
        semester_start: sessionForm.semester_start,
        semester_end: sessionForm.semester_end
      });
    } else {
      // Create new session
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

    if (!sessionForm.matiere_id || !sessionForm.enseignant_id || !sessionForm.salle_id) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const scheduleData: SemesterScheduleCreate = {
        matiere_id: sessionForm.matiere_id,
        groupe_id: selectedGroup,
        enseignant_id: sessionForm.enseignant_id,
        salle_id: sessionForm.salle_id,
        day_of_week: selectedCell.day,
        start_time: selectedCell.timeSlot.start,
        end_time: selectedCell.timeSlot.end,
        recurrence_type: sessionForm.recurrence_type,
        semester_start: sessionForm.semester_start,
        semester_end: sessionForm.semester_end
      };

      const result = await TimetableAPI.createSemesterSchedule(scheduleData);

      if (result.success) {
        setSuccess(
          `✅ ${result.created_count} sessions créées! ` +
          (result.conflicts_count > 0 ? `⚠️ ${result.conflicts_count} conflit(s)` : '')
        );
        setIsDialogOpen(false);
        
        // Navigate to the first week of the semester where sessions were created
        const semesterStartDate = new Date(sessionForm.semester_start);
        const firstWeekStart = TimetableAPI.getWeekStart(semesterStartDate);
        setCurrentWeekStart(firstWeekStart);
        
        // Reload schedule to show new sessions
        setTimeout(async () => {
          await loadWeekSchedule();
        }, 100);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la création');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSession = async () => {
    if (!editingSession) return;

    if (!sessionForm.matiere_id || !sessionForm.enseignant_id || !sessionForm.salle_id) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Note: Currently only updating room, can be extended
      await TimetableAPI.updateSession(editingSession.id, {
        salle_id: sessionForm.salle_id
      });

      setSuccess('✅ Session modifiée avec succès!');
      setIsDialogOpen(false);
      setEditingSession(null);
      
      // Reload schedule
      await loadWeekSchedule();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la modification');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async () => {
    if (!editingSession) return;

    if (!confirm('Voulez-vous vraiment supprimer cette session? Cette action est irréversible.')) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await TimetableAPI.cancelSession(editingSession.id);

      setSuccess('✅ Session supprimée avec succès!');
      setIsDialogOpen(false);
      setEditingSession(null);
      
      // Reload schedule
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
      const nextDate = new Date(currentWeekStart);
      nextDate.setDate(nextDate.getDate() + 7);
      setCurrentWeekStart(TimetableAPI.getWeekStart(nextDate));
    } else {
      setCurrentWeekStart(TimetableAPI.getPreviousWeekStart(currentWeekStart));
    }
  };

  const goToCurrentWeek = () => {
    setCurrentWeekStart(TimetableAPI.getWeekStart(new Date()));
  };

  const formatWeekRange = () => {
    const start = new Date(currentWeekStart);
    const end = new Date(currentWeekStart);
    end.setDate(end.getDate() + 6);
    
    return `${start.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })} - ${end.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}`;
  };

  // Check if a cell has a session
  const getCellSession = (day: DayOfWeek, timeSlot: typeof TIME_SLOTS[0]) => {
    if (!weekSchedule?.timetable) return null;
    
    // Convert day to lowercase French as API returns lowercase day names
    const dayLabel = TimetableAPI.dayOfWeekToFrench(day).toLowerCase();
    const daySessions = weekSchedule.timetable[dayLabel];
    
    if (!daySessions) {
      console.log(`No sessions for ${dayLabel}`);
      return null;
    }
    
    const session = daySessions.find(session => 
      session.start_time === timeSlot.start && session.end_time === timeSlot.end
    );
    
    if (!session) {
      console.log(`No match for ${dayLabel} ${timeSlot.start}-${timeSlot.end}. Available sessions:`, 
        daySessions.map(s => `${s.start_time}-${s.end_time}`));
    }
    
    return session;
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
            Cliquez sur une case pour créer un cours récurrent pour le semestre
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
                  {resources.groupes.map((groupe) => (
                    <SelectItem key={groupe.id} value={groupe.id}>
                      {groupe.nom} - {groupe.niveau} ({groupe.specialite})
                    </SelectItem>
                  ))}
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

      {/* Timetable Grid - Like the photo */}
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
                                  {session.matiere.nom}
                                </div>
                                <div className="text-xs opacity-90 space-y-1">
                                  <div className="truncate">
                                    📍 {session.salle.code}
                                  </div>
                                  <div className="truncate">
                                    👨‍🏫 {session.enseignant.prenom} {session.enseignant.nom}
                                  </div>
                                  <div className="truncate">
                                    👥 {session.groupe.nom}
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
            <li>• Le cours sera créé pour toutes les semaines du semestre</li>
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
              <Label htmlFor="matiere">Matière *</Label>
              <Select
                value={sessionForm.matiere_id}
                onValueChange={(value) => setSessionForm(prev => ({ ...prev, matiere_id: value }))}
                disabled={!!editingSession}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {resources.matieres.map((matiere) => (
                    <SelectItem key={matiere.id} value={matiere.id}>
                      {matiere.nom} {matiere.code && `(${matiere.code})`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Enseignant */}
            <div>
              <Label htmlFor="enseignant">Enseignant *</Label>
              <Select
                value={sessionForm.enseignant_id}
                onValueChange={(value) => setSessionForm(prev => ({ ...prev, enseignant_id: value }))}
                disabled={!!editingSession}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {resources.enseignants.map((enseignant) => (
                    <SelectItem key={enseignant.id} value={enseignant.id}>
                      {enseignant.prenom} {enseignant.nom}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Salle */}
            <div>
              <Label htmlFor="salle">Salle *</Label>
              <Select
                value={sessionForm.salle_id}
                onValueChange={(value) => setSessionForm(prev => ({ ...prev, salle_id: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {resources.salles.map((salle) => (
                    <SelectItem key={salle.id} value={salle.id}>
                      {salle.code} ({salle.type}) - {salle.capacite} places
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Groupe (read-only display) */}
            <div>
              <Label>Groupe</Label>
              <Input 
                value={resources.groupes.find(g => g.id === selectedGroup)?.nom || ''} 
                disabled 
                className="bg-gray-50"
              />
            </div>

            {/* Recurrence - Only show for new sessions */}
            {!editingSession && (
              <div>
                <Label htmlFor="recurrence">Récurrence *</Label>
                <Select
                  value={sessionForm.recurrence_type}
                  onValueChange={(value) => setSessionForm(prev => ({ ...prev, recurrence_type: value as RecurrenceType }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={RecurrenceType.WEEKLY}>Chaque Semaine</SelectItem>
                    <SelectItem value={RecurrenceType.BIWEEKLY}>Toutes les 2 Semaines</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Semester Dates - Only show for new sessions */}
            {!editingSession && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="start">Début Semestre</Label>
                  <Input
                    id="start"
                    type="date"
                    value={sessionForm.semester_start}
                    onChange={(e) => setSessionForm(prev => ({ ...prev, semester_start: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="end">Fin Semestre</Label>
                  <Input
                    id="end"
                    type="date"
                    value={sessionForm.semester_end}
                    onChange={(e) => setSessionForm(prev => ({ ...prev, semester_end: e.target.value }))}
                  />
                </div>
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
