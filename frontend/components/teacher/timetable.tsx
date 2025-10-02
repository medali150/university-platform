'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  Calendar, 
  Clock, 
  MapPin, 
  Users, 
  BookOpen,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  XCircle,
  GraduationCap
} from 'lucide-react';
import { TeacherAPI, TeacherSchedule, TeacherScheduleResponse } from '@/lib/teacher-api';

const DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];

interface WeekViewProps {
  scheduleData: TeacherScheduleResponse;
}

const WeekView: React.FC<WeekViewProps> = ({ scheduleData }) => {
  const { schedules, teacher_info } = scheduleData;
  
  // Group schedules by day
  const schedulesByDay: { [key: string]: TeacherSchedule[] } = {};
  
  schedules.forEach(schedule => {
    const date = new Date(schedule.date);
    const dayKey = date.toISOString().split('T')[0]; // YYYY-MM-DD
    
    if (!schedulesByDay[dayKey]) {
      schedulesByDay[dayKey] = [];
    }
    schedulesByDay[dayKey].push(schedule);
  });

  // Sort schedules within each day by start time
  Object.keys(schedulesByDay).forEach(day => {
    schedulesByDay[day].sort((a, b) => 
      new Date(a.heure_debut).getTime() - new Date(b.heure_debut).getTime()
    );
  });

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long'
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
      case 'COMPLETED':
        return <Badge className="bg-green-600">Terminé</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  // Get sorted days for the week
  const sortedDays = Object.keys(schedulesByDay).sort();

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">
          Emploi du temps - Prof. {teacher_info.prenom} {teacher_info.nom}
        </h2>
        <p className="text-muted-foreground">
          {teacher_info.email}
        </p>
      </div>

      {sortedDays.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Aucun cours programmé pour cette période</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {sortedDays.map(day => (
            <Card key={day}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  {formatDate(day)}
                </CardTitle>
                <CardDescription>
                  {schedulesByDay[day].length} cours programmés
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {schedulesByDay[day].map(schedule => (
                    <Card key={schedule.id} className="border-l-4 border-l-primary">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <BookOpen className="h-4 w-4 text-primary" />
                              <h3 className="font-semibold text-lg">
                                {schedule.matiere.nom}
                              </h3>
                              {getStatusBadge(schedule.status)}
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                <span>
                                  {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                                </span>
                              </div>
                              
                              <div className="flex items-center gap-1">
                                <Users className="h-3 w-3" />
                                <span>
                                  Groupe {schedule.groupe.nom} - {schedule.groupe.niveau}
                                </span>
                              </div>
                              
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                <span>
                                  Salle {schedule.salle.code}
                                </span>
                              </div>
                            </div>

                            <div className="mt-2 text-xs text-muted-foreground">
                              Spécialité: {schedule.groupe.specialite}
                            </div>
                          </div>
                          
                          <div className="flex flex-col items-end gap-1">
                            {schedule.status === 'COMPLETED' ? (
                              <CheckCircle className="h-5 w-5 text-green-500" />
                            ) : schedule.status === 'CANCELED' ? (
                              <XCircle className="h-5 w-5 text-red-500" />
                            ) : (
                              <Clock className="h-5 w-5 text-blue-500" />
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default function TeacherTimetablePage() {
  const [scheduleData, setScheduleData] = useState<TeacherScheduleResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(() => {
    const today = new Date();
    const monday = new Date(today);
    monday.setDate(today.getDate() - today.getDay() + 1); // Get Monday of current week
    return monday;
  });

  const loadSchedule = async (startDate: Date) => {
    try {
      setLoading(true);
      setError(null);

      const endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + 6); // Get Sunday of the week

      const data = await TeacherAPI.getSchedule(
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );

      setScheduleData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedule(currentWeekStart);
  }, [currentWeekStart]);

  const navigateWeek = (direction: 'prev' | 'next') => {
    const newWeekStart = new Date(currentWeekStart);
    newWeekStart.setDate(currentWeekStart.getDate() + (direction === 'next' ? 7 : -7));
    setCurrentWeekStart(newWeekStart);
  };

  const goToCurrentWeek = () => {
    const today = new Date();
    const monday = new Date(today);
    monday.setDate(today.getDate() - today.getDay() + 1);
    setCurrentWeekStart(monday);
  };

  const formatWeekRange = (startDate: Date) => {
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 6);
    
    return `${startDate.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })} - ${endDate.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}`;
  };

  if (loading && !scheduleData) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Chargement de l'emploi du temps...</span>
      </div>
    );
  }

  if (error && !scheduleData) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header with navigation */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <GraduationCap className="h-8 w-8" />
            Mon Emploi du Temps
          </h1>
          <p className="text-muted-foreground">
            Semaine du {formatWeekRange(currentWeekStart)}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => navigateWeek('prev')}
            disabled={loading}
          >
            <ChevronLeft className="h-4 w-4" />
            Précédent
          </Button>
          
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
            onClick={() => navigateWeek('next')}
            disabled={loading}
          >
            Suivant
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Loading overlay */}
      {loading && scheduleData && (
        <div className="text-center">
          <Loader2 className="h-4 w-4 animate-spin inline-block mr-2" />
          <span className="text-sm text-muted-foreground">Chargement...</span>
        </div>
      )}

      {/* Schedule content */}
      {scheduleData && <WeekView scheduleData={scheduleData} />}
    </div>
  );
}