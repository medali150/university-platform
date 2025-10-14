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
  User, 
  BookOpen,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import TimetableAPI, { TimetableResponse, SessionStatus } from '@/lib/timetable-api';

const DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];

interface WeekViewProps {
  scheduleData: TimetableResponse;
}

const WeekView: React.FC<WeekViewProps> = ({ scheduleData }) => {
  const { timetable, week_start, week_end, total_hours, note } = scheduleData;
  
  if (!timetable || Object.keys(timetable).length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">Aucun cours programmé pour cette semaine</p>
          {note && <p className="text-sm text-muted-foreground mt-2">{note}</p>}
        </CardContent>
      </Card>
    );
  }

  const formatTime = (timeString: string) => {
    return timeString; // Already formatted as "08:30"
  };

  const getStatusBadge = (status: SessionStatus) => {
    return (
      <Badge variant={TimetableAPI.getStatusVariant(status)}>
        {TimetableAPI.getStatusLabel(status)}
      </Badge>
    );
  };

  // Count total courses
  let totalCourses = 0;
  Object.values(timetable).forEach((sessions) => {
    totalCourses += sessions.length;
  });

  // Get unique days from timetable
  const daysWithCourses = Object.keys(timetable).sort((a, b) => {
    const dayOrder = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
    return dayOrder.indexOf(a) - dayOrder.indexOf(b);
  });

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">Mon Emploi du Temps</h2>
        <p className="text-muted-foreground">
          Semaine du {week_start} au {week_end}
        </p>
        {total_hours && (
          <p className="text-sm text-muted-foreground">
            Total: {total_hours}
          </p>
        )}
        {note && (
          <p className="text-sm text-blue-600 mt-2">{note}</p>
        )}
      </div>

      <div className="space-y-4">
        {daysWithCourses.map((day) => {
          const sessions = timetable[day];
          return (
            <Card key={day}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  {day}
                </CardTitle>
                <CardDescription>
                  {sessions.length} cours programmé{sessions.length > 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {sessions.map((session) => (
                    <Card key={session.id} className="border-l-4 border-l-primary">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <BookOpen className="h-4 w-4 text-primary" />
                              <h3 className="font-semibold text-lg">
                                {session.matiere.nom}
                              </h3>
                              {getStatusBadge(session.status)}
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                <span>
                                  {formatTime(session.start_time)} - {formatTime(session.end_time)}
                                </span>
                              </div>
                              
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                <span>
                                  Salle {session.salle.code}
                                </span>
                              </div>
                              
                              <div className="flex items-center gap-1">
                                <User className="h-3 w-3" />
                                <span>
                                  {session.enseignant.prenom} {session.enseignant.nom}
                                </span>
                              </div>
                            </div>

                            <div className="mt-2 text-xs text-muted-foreground">
                              Groupe: {session.groupe.nom} - {session.groupe.niveau}
                            </div>
                          </div>
                          
                          <div className="flex flex-col items-end gap-1">
                            {session.status === SessionStatus.COMPLETED ? (
                              <CheckCircle className="h-5 w-5 text-green-500" />
                            ) : session.status === SessionStatus.CANCELED ? (
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
          );
        })}
      </div>

      {/* Statistics */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{totalCourses}</div>
              <div className="text-sm text-muted-foreground">Cours cette semaine</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{daysWithCourses.length}</div>
              <div className="text-sm text-muted-foreground">Jours de cours</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">{total_hours}</div>
              <div className="text-sm text-muted-foreground">Heures totales</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default function StudentTimetablePage() {
  const [scheduleData, setScheduleData] = useState<TimetableResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentWeekStart, setCurrentWeekStart] = useState<string>(() => {
    return TimetableAPI.getWeekStart(new Date());
  });

  const loadSchedule = async (weekStart: string) => {
    try {
      setLoading(true);
      setError(null);

      const data = await TimetableAPI.getStudentWeeklySchedule(weekStart);
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
    if (!scheduleData) return '';
    return `${scheduleData.week_start} au ${scheduleData.week_end}`;
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
          <h1 className="text-3xl font-bold">Mon Emploi du Temps</h1>
          <p className="text-muted-foreground">
            Semaine du {formatWeekRange()}
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