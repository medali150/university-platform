'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { 
  Loader2, 
  Users, 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  Save,
  User
} from 'lucide-react';
import { TeacherAPI } from '@/lib/teacher-api';

interface StudentAbsenceInfo {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  is_absent: boolean;
  absence_id: string | null;
}

interface GroupDetails {
  id: string;
  nom: string;
  niveau: {
    id: string;
    nom: string;
    specialite: {
      id: string;
      nom: string;
    };
  };
  students: StudentAbsenceInfo[];
}

export default function GroupStudentsPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const groupId = params.groupId as string;
  const scheduleId = searchParams.get('schedule');

  const [groupDetails, setGroupDetails] = useState<GroupDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [absenceChanges, setAbsenceChanges] = useState<Map<string, {
    is_absent: boolean;
    motif?: string;
  }>>(new Map());

  useEffect(() => {
    loadGroupDetails();
  }, [groupId, scheduleId]);

  const loadGroupDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await TeacherAPI.getGroupStudents(groupId, scheduleId || undefined);
      setGroupDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load group details');
    } finally {
      setLoading(false);
    }
  };

  const handleAbsenceToggle = (studentId: string, isAbsent: boolean) => {
    setAbsenceChanges(prev => {
      const newChanges = new Map(prev);
      const currentChange = newChanges.get(studentId) || { is_absent: false };
      newChanges.set(studentId, {
        ...currentChange,
        is_absent: isAbsent
      });
      return newChanges;
    });
  };

  const handleMotifChange = (studentId: string, motif: string) => {
    setAbsenceChanges(prev => {
      const newChanges = new Map(prev);
      const currentChange = newChanges.get(studentId) || { is_absent: false };
      newChanges.set(studentId, {
        ...currentChange,
        motif: motif
      });
      return newChanges;
    });
  };

  const getStudentAbsenceStatus = (student: StudentAbsenceInfo) => {
    const change = absenceChanges.get(student.id);
    return change ? change.is_absent : student.is_absent;
  };

  const getStudentMotif = (student: StudentAbsenceInfo) => {
    const change = absenceChanges.get(student.id);
    return change?.motif || '';
  };

  const hasChanges = () => {
    return absenceChanges.size > 0;
  };

  const saveChanges = async () => {
    if (!scheduleId) {
      setError('ID de planning requis pour enregistrer les absences');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const promises = Array.from(absenceChanges.entries()).map(([studentId, change]) => {
        return TeacherAPI.markAbsence({
          student_id: studentId,
          schedule_id: scheduleId,
          is_absent: change.is_absent,
          motif: change.motif
        });
      });

      await Promise.all(promises);
      
      setSuccess('Absences enregistrées avec succès');
      setAbsenceChanges(new Map());
      
      // Reload data to reflect changes
      await loadGroupDetails();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'enregistrement');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Chargement des étudiants...</span>
      </div>
    );
  }

  if (error && !groupDetails) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!groupDetails) {
    return (
      <Alert>
        <AlertDescription>Groupe non trouvé</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          onClick={() => window.history.back()}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Retour
        </Button>
        
        <div>
          <h1 className="text-3xl font-bold">{groupDetails.nom}</h1>
          <p className="text-muted-foreground">
            {groupDetails.niveau.nom} - {groupDetails.niveau.specialite.nom}
          </p>
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Save Changes Button */}
      {hasChanges() && (
        <div className="flex justify-end">
          <Button 
            onClick={saveChanges} 
            disabled={saving || !scheduleId}
            className="flex items-center gap-2"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Enregistrer les Modifications
          </Button>
        </div>
      )}

      {/* Students List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Étudiants ({groupDetails.students.length})
          </CardTitle>
          <CardDescription>
            {scheduleId 
              ? 'Marquez les absences pour ce cours'
              : 'Liste des étudiants du groupe'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {groupDetails.students.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Aucun étudiant dans ce groupe
            </p>
          ) : (
            <div className="space-y-4">
              {groupDetails.students.map((student) => {
                const isAbsent = getStudentAbsenceStatus(student);
                const motif = getStudentMotif(student);
                const hasChanged = absenceChanges.has(student.id);

                return (
                  <Card 
                    key={student.id} 
                    className={`transition-all ${hasChanged ? 'ring-2 ring-primary/20 bg-primary/5' : ''}`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-4">
                          <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
                            <User className="h-5 w-5" />
                          </div>
                          
                          <div className="flex-1">
                            <h3 className="font-semibold">
                              {student.prenom} {student.nom}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              {student.email}
                            </p>
                            
                            {scheduleId && (
                              <div className="mt-2 space-y-2">
                                <div className="flex items-center space-x-2">
                                  <Checkbox
                                    id={`absent-${student.id}`}
                                    checked={isAbsent}
                                    onCheckedChange={(checked: boolean) => 
                                      handleAbsenceToggle(student.id, checked)
                                    }
                                  />
                                  <label 
                                    htmlFor={`absent-${student.id}`}
                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                                  >
                                    Absent
                                  </label>
                                </div>
                                
                                {isAbsent && (
                                  <Textarea
                                    placeholder="Motif de l'absence (optionnel)"
                                    value={motif}
                                    onChange={(e) => handleMotifChange(student.id, e.target.value)}
                                    className="text-sm"
                                    rows={2}
                                  />
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex flex-col items-end gap-2">
                          {isAbsent ? (
                            <Badge variant="destructive" className="flex items-center gap-1">
                              <XCircle className="h-3 w-3" />
                              Absent
                            </Badge>
                          ) : (
                            <Badge variant="default" className="flex items-center gap-1 bg-green-100 text-green-800">
                              <CheckCircle className="h-3 w-3" />
                              Présent
                            </Badge>
                          )}
                          
                          {hasChanged && (
                            <Badge variant="outline" className="text-xs">
                              Modifié
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Save Changes Button (Bottom) */}
      {hasChanges() && (
        <div className="flex justify-center">
          <Button 
            onClick={saveChanges} 
            disabled={saving || !scheduleId}
            size="lg"
            className="flex items-center gap-2"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Enregistrer les Modifications
          </Button>
        </div>
      )}
    </div>
  );
}