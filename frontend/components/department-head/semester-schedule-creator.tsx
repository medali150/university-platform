'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  Calendar, 
  Plus,
  Save,
  AlertCircle,
  CheckCircle,
  BookOpen,
  Users,
  MapPin,
  Clock
} from 'lucide-react';
import TimetableAPI, { 
  SemesterScheduleCreate, 
  DayOfWeek, 
  RecurrenceType,
  AvailableResources 
} from '@/lib/timetable-api';

export default function SemesterScheduleCreator() {
  const [loading, setLoading] = useState(false);
  const [resources, setResources] = useState<AvailableResources | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<SemesterScheduleCreate>({
    matiere_id: '',
    groupe_id: '',
    enseignant_id: '',
    salle_id: '',
    day_of_week: DayOfWeek.MONDAY,
    start_time: '08:30',
    end_time: '10:00',
    recurrence_type: RecurrenceType.WEEKLY,
    semester_start: '2025-09-01',
    semester_end: '2025-12-31'
  });

  // Load available resources
  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = async () => {
    try {
      setLoading(true);
      const data = await TimetableAPI.getAvailableResources();
      setResources(data);
      
      // Pre-select first items
      if (data.matieres.length > 0) {
        setFormData(prev => ({ ...prev, matiere_id: data.matieres[0].id }));
      }
      if (data.groupes.length > 0) {
        setFormData(prev => ({ ...prev, groupe_id: data.groupes[0].id }));
      }
      if (data.enseignants.length > 0) {
        setFormData(prev => ({ ...prev, enseignant_id: data.enseignants[0].id }));
      }
      if (data.salles.length > 0) {
        setFormData(prev => ({ ...prev, salle_id: data.salles[0].id }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      setLoading(true);
      const result = await TimetableAPI.createSemesterSchedule(formData);
      
      if (result.success) {
        setSuccess(
          `✅ Succès! ${result.created_count} sessions créées pour le semestre. ` +
          (result.conflicts_count > 0 
            ? `⚠️ ${result.conflicts_count} conflit(s) détecté(s).`
            : '✨ Aucun conflit.')
        );
      } else {
        setError('Échec de la création du planning');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof SemesterScheduleCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
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
            Créer un Emploi du Temps Semestriel
          </CardTitle>
          <CardDescription>
            Créez un planning récurrent pour tout le semestre en une seule fois.
            Une session sera créée automatiquement pour chaque semaine.
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

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Course Details */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Détails du Cours
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Matière */}
            <div>
              <Label htmlFor="matiere">Matière *</Label>
              <Select
                value={formData.matiere_id}
                onValueChange={(value) => handleChange('matiere_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner une matière" />
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

            {/* Groupe */}
            <div>
              <Label htmlFor="groupe">Groupe *</Label>
              <Select
                value={formData.groupe_id}
                onValueChange={(value) => handleChange('groupe_id', value)}
              >
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

            {/* Enseignant */}
            <div>
              <Label htmlFor="enseignant">Enseignant *</Label>
              <Select
                value={formData.enseignant_id}
                onValueChange={(value) => handleChange('enseignant_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un enseignant" />
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
                value={formData.salle_id}
                onValueChange={(value) => handleChange('salle_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner une salle" />
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
          </CardContent>
        </Card>

        {/* Schedule Details */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Horaires
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Day of Week */}
            <div>
              <Label htmlFor="day">Jour de la Semaine *</Label>
              <Select
                value={formData.day_of_week}
                onValueChange={(value) => handleChange('day_of_week', value as DayOfWeek)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={DayOfWeek.MONDAY}>Lundi</SelectItem>
                  <SelectItem value={DayOfWeek.TUESDAY}>Mardi</SelectItem>
                  <SelectItem value={DayOfWeek.WEDNESDAY}>Mercredi</SelectItem>
                  <SelectItem value={DayOfWeek.THURSDAY}>Jeudi</SelectItem>
                  <SelectItem value={DayOfWeek.FRIDAY}>Vendredi</SelectItem>
                  <SelectItem value={DayOfWeek.SATURDAY}>Samedi</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Recurrence Type */}
            <div>
              <Label htmlFor="recurrence">Récurrence *</Label>
              <Select
                value={formData.recurrence_type}
                onValueChange={(value) => handleChange('recurrence_type', value as RecurrenceType)}
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

            {/* Start Time */}
            <div>
              <Label htmlFor="start_time">Heure de Début *</Label>
              <Input
                id="start_time"
                type="time"
                value={formData.start_time}
                onChange={(e) => handleChange('start_time', e.target.value)}
                required
              />
            </div>

            {/* End Time */}
            <div>
              <Label htmlFor="end_time">Heure de Fin *</Label>
              <Input
                id="end_time"
                type="time"
                value={formData.end_time}
                onChange={(e) => handleChange('end_time', e.target.value)}
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Semester Dates */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Dates du Semestre
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Semester Start */}
            <div>
              <Label htmlFor="semester_start">Début du Semestre *</Label>
              <Input
                id="semester_start"
                type="date"
                value={formData.semester_start}
                onChange={(e) => handleChange('semester_start', e.target.value)}
                required
              />
            </div>

            {/* Semester End */}
            <div>
              <Label htmlFor="semester_end">Fin du Semestre *</Label>
              <Input
                id="semester_end"
                type="date"
                value={formData.semester_end}
                onChange={(e) => handleChange('semester_end', e.target.value)}
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-muted-foreground">
                  Créer toutes les sessions pour le semestre automatiquement
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Le planning des enseignants sera généré automatiquement
                </p>
              </div>
              <Button type="submit" disabled={loading} size="lg">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Création...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Créer le Planning
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>

      {/* Info Card */}
      <Alert className="border-blue-200 bg-blue-50">
        <AlertCircle className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>Comment ça marche?</strong>
          <ul className="mt-2 space-y-1 text-sm">
            <li>• Une session sera créée pour chaque occurrence (chaque semaine ou toutes les 2 semaines)</li>
            <li>• Le système vérifie automatiquement les conflits (salle, enseignant, groupe)</li>
            <li>• Le planning de l'enseignant est généré automatiquement</li>
            <li>• Les étudiants verront le planning immédiatement</li>
          </ul>
        </AlertDescription>
      </Alert>
    </div>
  );
}
