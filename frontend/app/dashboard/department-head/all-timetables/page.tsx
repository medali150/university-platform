'use client';

import { useState, useEffect } from 'react';
import { useRequireRole } from '@/hooks/useRequireRole';
import { Role } from '@/types/auth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Calendar, ChevronLeft, ChevronRight, List, Grid3x3, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

interface Schedule {
  id: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  salle?: {
    id: string;
    code: string;
  };
  matiere?: {
    id: string;
    nom: string;
  };
  groupe?: {
    id: string;
    nom: string;
  };
  enseignant?: {
    id: string;
    nom: string;
    prenom: string;
  };
  status: string;
}

interface Group {
  id: string;
  nom: string;
  niveau?: {
    nom: string;
    specialite?: {
      nom: string;
    };
  };
}

export default function AllTimetablesPage() {
  const { user, isLoading: authLoading } = useRequireRole('DEPARTMENT_HEAD' as Role);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [loadingGroups, setLoadingGroups] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'week' | 'list'>('week');
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(getWeekStart(new Date()));

  function getWeekStart(date: Date): Date {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  }

  useEffect(() => {
    if (user && !authLoading) {
      loadGroups();
    }
  }, [user, authLoading]);

  useEffect(() => {
    if (selectedGroup) {
      loadSchedules();
    }
  }, [selectedGroup, currentWeekStart]);

  const loadGroups = async () => {
    try {
      setLoadingGroups(true);
      const response = await api.get('/department-head/timetable/groups');
      console.log('✅ Groups loaded:', response);
      
      if (Array.isArray(response)) {
        setGroups(response);
        // Auto-select first group if available
        if (response.length > 0) {
          setSelectedGroup(response[0].id);
        }
      }
    } catch (error: any) {
      console.error('❌ Error loading groups:', error);
    } finally {
      setLoadingGroups(false);
    }
  };

  const loadSchedules = async () => {
    if (!selectedGroup) {
      setSchedules([]);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const weekEnd = new Date(currentWeekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);

      const startDateStr = currentWeekStart.toISOString().split('T')[0];
      const endDateStr = weekEnd.toISOString().split('T')[0];

      console.log('📅 Loading schedules for group', selectedGroup, 'from', startDateStr, 'to', endDateStr);

      // Use department-head specific endpoint with group filter
      const response = await api.get(
        `/department-head/timetable/schedules?group_id=${selectedGroup}&date_from=${startDateStr}&date_to=${endDateStr}`
      );

      console.log('✅ Schedules loaded:', response);
      console.log('📊 Schedule count:', Array.isArray(response) ? response.length : 0);
      
      if (Array.isArray(response) && response.length > 0) {
        console.log('🔍 First schedule sample:', response[0]);
        console.log('📅 First schedule date:', response[0].date);
        console.log('⏰ First schedule times:', response[0].heure_debut, '-', response[0].heure_fin);
      }

      if (Array.isArray(response)) {
        setSchedules(response);
      } else {
        setSchedules([]);
      }
    } catch (error: any) {
      console.error('❌ Error loading schedules:', error);
      const errorMessage = error.message || error.toString() || 'Erreur lors du chargement des emplois du temps';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timeStr: string | Date): string => {
    if (!timeStr) return '';
    const date = new Date(timeStr);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (dateStr: string | Date): string => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const getDayOfWeek = (dateStr: string | Date): number => {
    const date = typeof dateStr === 'string' ? new Date(dateStr) : new Date(dateStr);
    const day = date.getDay();
    return day === 0 ? 6 : day - 1; // Convert to 0=Monday, 6=Sunday
  };

  const getWeekDays = (): Date[] => {
    const days: Date[] = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(currentWeekStart);
      day.setDate(day.getDate() + i);
      days.push(day);
    }
    return days;
  };

  const getSchedulesForDay = (dayIndex: number): Schedule[] => {
    const filtered = schedules.filter(s => {
      const scheduleDayIndex = getDayOfWeek(s.date);
      return scheduleDayIndex === dayIndex;
    });
    
    // Debug log for first day
    if (dayIndex === 0 && filtered.length > 0) {
      console.log('📅 Monday schedules:', filtered.length, filtered);
    }
    
    return filtered;
  };

  const previousWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(newStart.getDate() - 7);
    setCurrentWeekStart(newStart);
  };

  const nextWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(newStart.getDate() + 7);
    setCurrentWeekStart(newStart);
  };

  const thisWeek = () => {
    setCurrentWeekStart(getWeekStart(new Date()));
  };

  if (authLoading || !user) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm text-muted-foreground">Chargement...</p>
        </div>
      </div>
    );
  }

  const weekDays = getWeekDays();
  const dayNames = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link href="/dashboard/department-head">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour au tableau de bord
          </Button>
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">Tous les Emplois du Temps</h1>
        <p className="text-muted-foreground">
          Visualisez tous les horaires de votre département
        </p>
      </div>

      {/* Filters and Controls */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Group Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">Sélectionner une classe</label>
              {loadingGroups ? (
                <div className="flex items-center gap-2 px-4 py-2 border rounded-lg">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">Chargement...</span>
                </div>
              ) : (
                <select
                  value={selectedGroup}
                  onChange={(e) => setSelectedGroup(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Choisir une classe --</option>
                  {groups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.nom}
                      {group.niveau?.specialite?.nom && ` - ${group.niveau.specialite.nom}`}
                      {group.niveau?.nom && ` (${group.niveau.nom})`}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* View Mode */}
            <div>
              <label className="block text-sm font-medium mb-2">Mode d'affichage</label>
              <div className="flex space-x-2">
                <Button
                  variant={viewMode === 'week' ? 'default' : 'outline'}
                  onClick={() => setViewMode('week')}
                  className="flex-1"
                  disabled={!selectedGroup}
                >
                  <Grid3x3 className="mr-2 h-4 w-4" />
                  Vue Semaine
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  onClick={() => setViewMode('list')}
                  className="flex-1"
                  disabled={!selectedGroup}
                >
                  <List className="mr-2 h-4 w-4" />
                  Vue Liste
                </Button>
              </div>
            </div>

            {/* Week Navigation */}
            <div>
              <label className="block text-sm font-medium mb-2">Navigation par semaine</label>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  onClick={previousWeek} 
                  size="icon"
                  disabled={!selectedGroup}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  onClick={thisWeek} 
                  className="flex-1"
                  disabled={!selectedGroup}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  Cette semaine
                </Button>
                <Button 
                  variant="outline" 
                  onClick={nextWeek} 
                  size="icon"
                  disabled={!selectedGroup}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {selectedGroup && (
            <div className="mt-4 text-center">
              <p className="text-sm text-muted-foreground">
                Semaine du {formatDate(currentWeekStart)} au {formatDate(weekDays[6])}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* No Group Selected Message */}
      {!selectedGroup && !loadingGroups && (
        <Card>
          <CardContent className="py-12 text-center">
            <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-lg font-medium text-muted-foreground">
              Veuillez sélectionner une classe pour voir son emploi du temps
            </p>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {selectedGroup && loading && (
        <div className="flex justify-center py-16">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin" />
            <p className="text-sm text-muted-foreground">Chargement des emplois du temps...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {selectedGroup && error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
            <Button onClick={loadSchedules} className="mt-4" variant="outline">
              Réessayer
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Week View */}
      {selectedGroup && !loading && !error && viewMode === 'week' && (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1200px] border-collapse">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="px-4 py-3 text-left text-sm font-semibold border border-gray-300 bg-gray-50">
                      Horaires
                    </th>
                    {weekDays.map((day, idx) => (
                      <th key={idx} className="px-4 py-3 text-center text-sm font-semibold border border-gray-300 bg-gray-50">
                        <div className="font-bold text-gray-900">{dayNames[idx]}</div>
                        <div className="text-xs text-gray-600 font-normal">
                          {day.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: 10 }, (_, i) => {
                    // Generate time slots: 08:30-10:00, 10:10-11:40, 11:50-13:20, 14:30-16:00, 16:10-17:40
                    const timeSlots = [
                      { start: '08:30', end: '10:00', startHour: 8, startMin: 30 },
                      { start: '10:10', end: '11:40', startHour: 10, startMin: 10 },
                      { start: '11:50', end: '13:20', startHour: 11, startMin: 50 },
                      { start: '14:30', end: '16:00', startHour: 14, startMin: 30 },
                      { start: '16:10', end: '17:40', startHour: 16, startMin: 10 },
                    ];
                    
                    if (i >= timeSlots.length) return null;
                    
                    const slot = timeSlots[i];
                    
                    return (
                      <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-4 py-8 text-sm font-medium border border-gray-300 text-center align-middle">
                          <div className="font-semibold text-gray-700">{slot.start}</div>
                          <div className="text-xs text-gray-500">à</div>
                          <div className="font-semibold text-gray-700">{slot.end}</div>
                        </td>
                        {weekDays.map((day, dayIdx) => {
                          const daySchedules = getSchedulesForDay(dayIdx);
                          const matchingSchedule = daySchedules.find(s => {
                            const scheduleStart = new Date(s.heure_debut);
                            const scheduleHour = scheduleStart.getHours();
                            const scheduleMin = scheduleStart.getMinutes();
                            
                            // Debug: log first match attempt on first render
                            if (i === 0 && dayIdx === 0 && daySchedules.length > 0) {
                              console.log('🔍 Matching slot', slot.start, 'with schedule time', scheduleHour + ':' + scheduleMin);
                            }
                            
                            return scheduleHour === slot.startHour && scheduleMin === slot.startMin;
                          });

                          return (
                            <td key={dayIdx} className="px-3 py-8 border border-gray-300 align-top relative">
                              {matchingSchedule ? (
                                <div className="bg-blue-50 border-l-4 border-blue-500 rounded-md p-3 hover:bg-blue-100 transition-colors cursor-pointer shadow-sm h-full">
                                  <div className="font-bold text-blue-900 text-sm mb-2">
                                    {matchingSchedule.matiere?.nom || 'N/A'}
                                  </div>
                                  <div className="space-y-1 text-xs text-gray-700">
                                    <div className="flex items-center gap-1">
                                      <span className="text-gray-500">👨‍🏫</span>
                                      <span className="truncate">
                                        {matchingSchedule.enseignant?.prenom} {matchingSchedule.enseignant?.nom}
                                      </span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <span className="text-gray-500">📍</span>
                                      <span className="font-medium">{matchingSchedule.salle?.code || 'N/A'}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <span className="text-gray-500">👥</span>
                                      <span className="truncate">{matchingSchedule.groupe?.nom || 'N/A'}</span>
                                    </div>
                                  </div>
                                  <div className="mt-2 pt-2 border-t border-blue-200 text-xs text-blue-700 font-medium">
                                    {formatTime(matchingSchedule.heure_debut)} - {formatTime(matchingSchedule.heure_fin)}
                                  </div>
                                </div>
                              ) : (
                                <div className="h-full flex flex-col items-center justify-center text-center py-6">
                                  <div className="text-gray-300 text-3xl mb-2">+</div>
                                  <div className="text-xs text-gray-400">Cliquer pour ajouter</div>
                                </div>
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  }).filter(Boolean)}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* List View */}
      {selectedGroup && !loading && !error && viewMode === 'list' && (
        <div className="space-y-4">
          {schedules.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Aucun emploi du temps trouvé pour cette semaine</p>
              </CardContent>
            </Card>
          ) : (
            schedules.map((schedule) => (
              <Card key={schedule.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Date & Heure</div>
                      <div className="font-semibold">{formatDate(schedule.date)}</div>
                      <div className="text-sm">
                        {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Matière</div>
                      <div className="font-semibold">{schedule.matiere?.nom || 'N/A'}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Enseignant</div>
                      <div className="font-semibold">
                        {schedule.enseignant?.prenom} {schedule.enseignant?.nom}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Salle & Groupe</div>
                      <div className="font-semibold">📍 {schedule.salle?.code || 'N/A'}</div>
                      <div className="text-sm">👥 {schedule.groupe?.nom || 'N/A'}</div>
                    </div>
                  </div>
                  {schedule.status !== 'PLANNED' && (
                    <div className="mt-4 pt-4 border-t">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        schedule.status === 'CANCELED' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {schedule.status}
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Statistics */}
      {selectedGroup && !loading && !error && schedules.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{schedules.length}</div>
              <p className="text-xs text-muted-foreground">cette semaine</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Planifiées</CardTitle>
              <Calendar className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {schedules.filter(s => s.status === 'PLANNED').length}
              </div>
              <p className="text-xs text-muted-foreground">sessions actives</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
              <Calendar className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {new Set(schedules.map(s => s.enseignant?.id).filter(Boolean)).size}
              </div>
              <p className="text-xs text-muted-foreground">impliqués</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Groupes</CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {new Set(schedules.map(s => s.groupe?.id).filter(Boolean)).size}
              </div>
              <p className="text-xs text-muted-foreground">concernés</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
