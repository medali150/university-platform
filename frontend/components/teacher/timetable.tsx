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
import { TeacherAPI } from '@/lib/teacher-api';

const DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];

// Time slots matching the image structure
const TIME_SLOTS = [
  { start: '08:30', end: '10:00' },
  { start: '10:10', end: '11:40' },
  { start: '11:50', end: '13:20' },
  { start: '14:30', end: '16:00' },
  { start: '16:10', end: '17:40' },
];

interface WeekViewProps {
  scheduleData: any;
}

const WeekView: React.FC<WeekViewProps> = ({ scheduleData }) => {
  const { timetable, week_start, week_end, total_hours, note } = scheduleData;
  
  if (!timetable || Object.keys(timetable).length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">Aucun cours programmé pour cette semaine</p>
          {note && <p className="text-sm text-blue-600 mt-2">{note}</p>}
        </CardContent>
      </Card>
    );
  }

  // Helper function to check if a session fits in a time slot
  const findSessionForSlot = (day: string, timeSlot: { start: string; end: string }) => {
    const daySessions = timetable[day.toLowerCase()] || timetable[day];
    if (!daySessions) return null;

    return daySessions.find((session: any) => {
      const sessionStart = session.start_time;
      const sessionEnd = session.end_time;
      // Match if session starts within this time slot
      return sessionStart >= timeSlot.start && sessionStart < timeSlot.end;
    });
  };

  // Count total courses
  let totalCourses = 0;
  Object.values(timetable).forEach((sessions: any) => {
    totalCourses += sessions.length;
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
          <Alert className="mt-4 border-blue-200 bg-blue-50">
            <AlertDescription className="text-blue-700">
              <strong>Note:</strong> {note}
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Grid Timetable */}
      <Card>
        <CardContent className="p-4">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse min-w-[800px]">
              <thead>
                <tr>
                  <th className="border border-gray-300 bg-gray-100 p-3 text-center font-semibold">
                    Horaire
                  </th>
                  {DAYS_OF_WEEK.map((day) => (
                    <th key={day} className="border border-gray-300 bg-gray-100 p-3 text-center font-semibold">
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map((slot, index) => (
                  <tr key={index}>
                    <td className="border border-gray-300 bg-gray-50 p-3 text-center align-middle font-medium text-sm whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="font-bold">{slot.start}</span>
                        <span className="text-xs text-muted-foreground">à</span>
                        <span className="font-bold">{slot.end}</span>
                      </div>
                    </td>
                    {DAYS_OF_WEEK.map((day) => {
                      const session = findSessionForSlot(day, slot);
                      
                      return (
                        <td 
                          key={`${day}-${index}`} 
                          className={`border border-gray-300 p-2 align-top ${
                            session ? 'bg-blue-50' : 'bg-white'
                          }`}
                        >
                          {session ? (
                            <div className="space-y-1">
                              <div className="font-semibold text-sm text-blue-900 flex items-start gap-1">
                                <BookOpen className="h-3 w-3 mt-0.5 flex-shrink-0" />
                                <span className="line-clamp-2">{session.matiere.nom}</span>
                              </div>
                              
                              <div className="text-xs text-gray-700 space-y-0.5">
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  <span>{session.start_time} - {session.end_time}</span>
                                </div>
                                
                                <div className="flex items-center gap-1">
                                  <Users className="h-3 w-3" />
                                  <span className="truncate">Groupe {session.groupe.nom}</span>
                                </div>
                                
                                <div className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3" />
                                  <span>Salle {session.salle.code}</span>
                                </div>
                              </div>

                              <div className="text-xs italic text-gray-600 truncate">
                                {session.groupe.specialite}
                              </div>

                              {session.status === 'PLANNED' && (
                                <Badge variant="default" className="text-xs">
                                  Programmé
                                </Badge>
                              )}
                              {session.status === 'CANCELED' && (
                                <Badge variant="destructive" className="text-xs">
                                  Annulé
                                </Badge>
                              )}
                            </div>
                          ) : null}
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

      {/* Statistics */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{totalCourses}</div>
              <div className="text-sm text-muted-foreground">Cours cette semaine</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{Object.keys(timetable).length}</div>
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

export default function TeacherTimetablePage() {
  const [scheduleData, setScheduleData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentWeekStart, setCurrentWeekStart] = useState<string>(() => {
    const today = new Date();
    const day = today.getDay();
    const diff = today.getDate() - day + (day === 0 ? -6 : 1);
    const monday = new Date(today.setDate(diff));
    return monday.toISOString().split('T')[0];
  });

  const loadSchedule = async (weekStart: string) => {
    try {
      setLoading(true);
      setError(null);

      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);
      
      const data = await TeacherAPI.getSchedule(weekStart, weekEnd.toISOString().split('T')[0]);
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
      const day = nextDate.getDay();
      const diff = nextDate.getDate() - day + (day === 0 ? -6 : 1);
      const monday = new Date(nextDate.setDate(diff));
      setCurrentWeekStart(monday.toISOString().split('T')[0]);
    } else {
      const prevDate = new Date(currentWeekStart);
      prevDate.setDate(prevDate.getDate() - 7);
      const day = prevDate.getDay();
      const diff = prevDate.getDate() - day + (day === 0 ? -6 : 1);
      const monday = new Date(prevDate.setDate(diff));
      setCurrentWeekStart(monday.toISOString().split('T')[0]);
    }
  };

  const goToCurrentWeek = () => {
    const today = new Date();
    const day = today.getDay();
    const diff = today.getDate() - day + (day === 0 ? -6 : 1);
    const monday = new Date(today.setDate(diff));
    setCurrentWeekStart(monday.toISOString().split('T')[0]);
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
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <GraduationCap className="h-8 w-8" />
            Mon Emploi du Temps
          </h1>
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