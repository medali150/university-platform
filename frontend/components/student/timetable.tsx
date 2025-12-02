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
import { StudentAPI } from '@/lib/student-api';

const DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];

// Time slots matching the standard university schedule
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
      <Card className="border-0 shadow-lg bg-gradient-to-br from-slate-50 to-indigo-50">
        <CardContent className="p-8 text-center">
          <div className="flex flex-col items-center gap-4">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <Calendar className="h-8 w-8 text-indigo-600" />
            </div>
            <p className="text-gray-700 font-medium">Aucun cours programmé pour cette semaine</p>
            {note && <p className="text-sm text-gray-500">{note}</p>}
          </div>
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
      return sessionStart >= timeSlot.start && sessionStart < timeSlot.end;
    });
  };

  // Count total courses
  let totalCourses = 0;
  Object.values(timetable).forEach((sessions: any) => {
    totalCourses += sessions.length;
  });

  // Subject color mapping
  const getSubjectColor = (subject: string) => {
    const colors: Record<string, { gradient: string; light: string }> = {
      'ALGO': { gradient: 'from-blue-500 to-blue-600', light: 'bg-blue-50' },
      'MATH': { gradient: 'from-green-500 to-green-600', light: 'bg-green-50' },
      'ARCH': { gradient: 'from-purple-500 to-purple-600', light: 'bg-purple-50' },
      'ENG': { gradient: 'from-orange-500 to-orange-600', light: 'bg-orange-50' },
      'default': { gradient: 'from-indigo-500 to-indigo-600', light: 'bg-indigo-50' }
    };
    const code = subject.split(' ')[0];
    return colors[code] || colors['default'];
  };

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600 font-medium">Cours cette semaine</p>
                <p className="text-2xl font-bold text-gray-900">{totalCourses}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Calendar className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600 font-medium">Jours de cours</p>
                <p className="text-2xl font-bold text-gray-900">{Object.keys(timetable).length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600 font-medium">Heures totales</p>
                <p className="text-2xl font-bold text-gray-900">{total_hours}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Grid Timetable */}
      <Card className="border-0 shadow-lg overflow-hidden">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse min-w-[800px]">
              <thead>
                <tr className="bg-gradient-to-r from-indigo-50 to-purple-50 border-b-2 border-indigo-200">
                  <th className="p-4 text-center font-bold text-gray-900 border-r border-indigo-200">
                    Horaire
                  </th>
                  {DAYS_OF_WEEK.map((day) => (
                    <th key={day} className="p-4 text-center font-bold text-gray-900 border-r border-indigo-200">
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {TIME_SLOTS.map((slot, index) => (
                  <tr key={index} className={`border-b border-gray-200 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'}`}>
                    <td className="p-4 text-center align-top font-medium text-sm text-gray-900 border-r border-gray-200 bg-gradient-to-r from-indigo-50 to-transparent">
                      <div className="flex flex-col">
                        <span className="font-bold">{slot.start}</span>
                        <span className="text-xs text-gray-500">à</span>
                        <span className="font-bold">{slot.end}</span>
                      </div>
                    </td>
                    {DAYS_OF_WEEK.map((day) => {
                      const session = findSessionForSlot(day, slot);
                      const colors = session ? getSubjectColor(session.subject) : null;
                      
                      return (
                        <td 
                          key={`${day}-${index}`} 
                          className="p-2 align-top border-r border-gray-200 min-h-[100px] hover:bg-indigo-50/50 transition-all"
                        >
                          {session ? (
                            <div className={`h-full bg-gradient-to-br ${colors?.gradient} rounded-lg p-3 text-white shadow-md hover:shadow-lg transition-all cursor-pointer group hover:scale-105 transform`}>
                              <div className="font-semibold text-sm leading-tight line-clamp-2 mb-1 flex items-start gap-1">
                                <BookOpen className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                                <span>{session.subject}</span>
                              </div>
                              
                              <div className="text-xs text-white/90 space-y-0.5">
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  <span>{session.start_time} - {session.end_time}</span>
                                </div>
                                
                                <div className="flex items-center gap-1">
                                  <User className="h-3 w-3" />
                                  <span className="truncate">{session.teacher}</span>
                                </div>
                                
                                <div className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3" />
                                  <span className="truncate">Salle {session.room}</span>
                                </div>
                              </div>

                              {session.status === 'PLANNED' && (
                                <Badge className="text-xs mt-2 bg-white/20 text-white border-0 hover:bg-white/30">
                                  ✓ Programmé
                                </Badge>
                              )}
                              {session.status === 'CANCELED' && (
                                <Badge className="text-xs mt-2 bg-red-500/40 text-white border-0">
                                  ✕ Annulé
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

      {note && (
        <Alert className="border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50">
          <AlertCircle className="h-4 w-4 text-indigo-600" />
          <AlertDescription className="text-indigo-900 font-medium">
            {note}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default function StudentTimetablePage() {
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

      const data = await StudentAPI.getUniversityTimetable(0);
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
      {/* Modern Gradient Header */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-8 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-2">
            📚 Mon Emploi du Temps
          </h1>
          <p className="text-indigo-100 text-lg">
            Semaine du {formatWeekRange()}
          </p>
        </div>
      </div>

      {/* Week Navigation */}
      <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4 p-4 bg-gradient-to-r from-slate-50 to-indigo-50 rounded-lg border border-indigo-100">
        <div className="text-sm text-gray-600">
          <p className="font-semibold text-gray-900">Navigation de la semaine</p>
          <p className="text-xs text-gray-500 mt-1">Utilisez les boutons pour naviguer</p>
        </div>
        
        <div className="flex items-center gap-2">
          <button 
            onClick={() => navigateWeek('prev')}
            disabled={loading}
            className="p-2 hover:bg-indigo-100 rounded-lg transition-all text-gray-600 hover:text-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Semaine précédente"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          
          <button 
            onClick={goToCurrentWeek}
            disabled={loading}
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            title="Semaine actuelle"
          >
            <Calendar className="h-4 w-4" />
            Aujourd'hui
          </button>
          
          <button 
            onClick={() => navigateWeek('next')}
            disabled={loading}
            className="p-2 hover:bg-indigo-100 rounded-lg transition-all text-gray-600 hover:text-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Semaine suivante"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <Alert variant="destructive" className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-900 font-medium">{error}</AlertDescription>
        </Alert>
      )}

      {/* Loading overlay */}
      {loading && scheduleData && (
        <div className="text-center p-4 bg-indigo-50 rounded-lg border border-indigo-200">
          <Loader2 className="h-4 w-4 animate-spin inline-block mr-2 text-indigo-600" />
          <span className="text-sm text-indigo-900 font-medium">Chargement...</span>
        </div>
      )}

      {/* Schedule content */}
      {scheduleData && <WeekView scheduleData={scheduleData} />}
    </div>
  );
}