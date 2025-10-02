'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Users, Calendar, CheckCircle, XCircle, Clock } from 'lucide-react';
import { TeacherAPI } from '@/lib/teacher-api';

interface TeacherGroup {
  id: string;
  nom: string;
  niveau: {
    id: string;
    nom: string;
  };
  specialite: {
    id: string;
    nom: string;
    departement: string;
  };
  student_count: number;
}

interface TodaySchedule {
  id: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  matiere: {
    id: string;
    nom: string;
  };
  groupe: {
    id: string;
    nom: string;
    niveau: string;
    specialite: string;
  };
  salle: {
    id: string;
    code: string;
    type: string;
  };
  status: string;
}

export default function TeacherAbsencePage() {
  const [groups, setGroups] = useState<TeacherGroup[]>([]);
  const [todaySchedule, setTodaySchedule] = useState<TodaySchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSchedule, setSelectedSchedule] = useState<TodaySchedule | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [groupsData, scheduleData] = await Promise.all([
        TeacherAPI.getGroups(),
        TeacherAPI.getTodaySchedule()
      ]);

      setGroups(groupsData);
      setTodaySchedule(scheduleData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleSelect = (schedule: TodaySchedule) => {
    setSelectedSchedule(schedule);
  };

  const handleGroupSelect = (group: TeacherGroup, scheduleId?: string) => {
    // Navigate to group students page
    const url = scheduleId 
      ? `/teacher/absence/group/${group.id}?schedule=${scheduleId}`
      : `/teacher/absence/group/${group.id}`;
    
    window.location.href = url;
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PLANNED':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700">Programmé</Badge>;
      case 'CANCELED':
        return <Badge variant="destructive">Annulé</Badge>;
      case 'MAKEUP':
        return <Badge variant="secondary">Rattrapage</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Chargement des données...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gestion des Absences</h1>
          <p className="text-muted-foreground">
            Gérez les absences de vos étudiants
          </p>
        </div>
      </div>

      {/* Today's Schedule */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Planning d&apos;Aujourd&apos;hui
          </CardTitle>
          <CardDescription>
            Vos cours programmés pour aujourd&apos;hui
          </CardDescription>
        </CardHeader>
        <CardContent>
          {todaySchedule.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Aucun cours programmé pour aujourd&apos;hui
            </p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {todaySchedule.map((schedule) => (
                <Card 
                  key={schedule.id}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    selectedSchedule?.id === schedule.id ? 'ring-2 ring-primary' : ''
                  }`}
                  onClick={() => handleScheduleSelect(schedule)}
                >
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-start">
                        <h3 className="font-semibold">{schedule.matiere.nom}</h3>
                        {getStatusBadge(schedule.status)}
                      </div>
                      
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                        </div>
                        
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {schedule.groupe.nom} ({schedule.groupe.niveau})
                        </div>
                        
                        <div>
                          📍 Salle {schedule.salle.code}
                        </div>
                      </div>
                      
                      <Button 
                        size="sm" 
                        className="w-full mt-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          const group = groups.find(g => g.nom === schedule.groupe.nom);
                          if (group) {
                            handleGroupSelect(group, schedule.id);
                          }
                        }}
                      >
                        Gérer les Absences
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* All Groups */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Tous mes Groupes
          </CardTitle>
          <CardDescription>
            Tous les groupes que vous enseignez
          </CardDescription>
        </CardHeader>
        <CardContent>
          {groups.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              Aucun groupe trouvé
            </p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {groups.map((group) => (
                <Card key={group.id} className="cursor-pointer transition-all hover:shadow-md">
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div>
                        <h3 className="font-semibold text-lg">{group.nom}</h3>
                        <p className="text-sm text-muted-foreground">
                          {group.niveau.nom} - {group.specialite.nom}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {group.specialite.departement}
                        </p>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary" className="flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {group.student_count} étudiants
                        </Badge>
                      </div>
                      
                      <Button 
                        className="w-full"
                        onClick={() => handleGroupSelect(group)}
                      >
                        Voir les Étudiants
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}