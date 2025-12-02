'use client';

import { useState, useEffect } from 'react';
import { useRequireRole } from '@/hooks/useRequireRole';
import { Role } from '@/types/auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Calendar, ChevronLeft, ChevronRight, List, Grid3x3, Loader2, RefreshCw } from 'lucide-react';
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
    niveau?: {
      nom: string;
      specialite?: {
        nom: string;
      };
    };
  };
  enseignant?: {
    id: string;
    nom: string;
    prenom: string;
  };
  status: string;
}

export default function DepartmentSchedulePage() {
  const { user, isLoading: authLoading } = useRequireRole('DEPARTMENT_HEAD' as Role);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'week' | 'list'>('list');
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(getWeekStart(new Date()));
  const [selectedGroup, setSelectedGroup] = useState<string>('all');

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
    if (groups.length > 0) {
      loadSchedules();
    }
  }, [groups, currentWeekStart]);

  // Auto-refresh when page becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && groups.length > 0) {
        console.log('🔄 Page visible - refreshing schedules...');
        loadSchedules();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [groups.length]);

  // Auto-refresh every 10 seconds when page is active
  useEffect(() => {
    if (groups.length === 0) return;

    const intervalId = setInterval(() => {
      if (!document.hidden) {
        console.log('🔄 Auto-refresh (10s interval)...');
        loadSchedules();
      }
    }, 10000); // 10 seconds for faster updates

    return () => clearInterval(intervalId);
  }, [groups.length]);

  const loadGroups = async () => {
    try {
      console.log('📚 Loading groups...');
      const response = await api.get('/department-head/timetable/groups');
      console.log('✅ Groups loaded:', response);
      
      if (Array.isArray(response)) {
        setGroups(response);
      }
    } catch (error: any) {
      console.error('❌ Error loading groups:', error);
    }
  };

  const loadSchedules = async () => {
    if (groups.length === 0) {
      console.log('⚠️ No groups available, skipping schedule load');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const weekEnd = new Date(currentWeekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);

      const startDateStr = currentWeekStart.toISOString().split('T')[0];
      const endDateStr = weekEnd.toISOString().split('T')[0];

      console.log('📅 Loading all department schedules from', startDateStr, 'to', endDateStr);
      console.log('📚 Loading for', groups.length, 'groups');

      // Load schedules for all groups
      const allSchedulesPromises = groups.map(group =>
        api.get(
          `/department-head/timetable/schedules?group_id=${group.id}&date_from=${startDateStr}&date_to=${endDateStr}`
        ).catch(err => {
          console.warn(`⚠️ Failed to load schedules for group ${group.nom}:`, err);
          return [];
        })
      );

      const allSchedulesArrays = await Promise.all(allSchedulesPromises);
      const allSchedules = allSchedulesArrays.flat();

      console.log('✅ Schedules loaded:', allSchedules);
      console.log('📊 Number of schedules:', allSchedules.length);
      
      if (allSchedules.length > 0) {
        console.log('🔍 First 3 schedules:', allSchedules.slice(0, 3));
        setSchedules(allSchedules);
      } else {
        console.log('⚠️ No schedules found');
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
    return day === 0 ? 6 : day - 1;
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

    console.log(`📅 Day ${dayIndex}: Found ${filtered.length} schedules before group filter`);
    
    // Filter by selected group if not 'all'
    if (selectedGroup !== 'all') {
      const groupFiltered = filtered.filter(s => s.groupe?.id === selectedGroup);
      console.log(`🔍 After group filter (${selectedGroup}): ${groupFiltered.length} schedules`);
      return groupFiltered;
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
  
  // Use loaded groups for filtering
  const uniqueGroups = groups.sort((a, b) => (a.nom || '').localeCompare(b.nom || ''));

  // Get filtered schedules based on selected group
  const filteredSchedules = selectedGroup === 'all' 
    ? schedules 
    : schedules.filter(s => s.groupe?.id === selectedGroup);

  // Group schedules by day for list view
  const schedulesByDay = weekDays.map((day, idx) => ({
    day,
    dayName: day.toLocaleDateString('fr-FR', { weekday: 'long' }),
    schedules: getSchedulesForDay(idx)
  }));
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
        <h1 className="text-3xl font-bold tracking-tight">Emplois du Temps du Département</h1>
        <p className="text-muted-foreground">
          Vue complète de tous les horaires de votre département
        </p>
      </div>

      {/* Filters and Controls */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Group Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Filtrer par classe</label>
              <select
                value={selectedGroup}
                onChange={(e) => setSelectedGroup(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">📚 Toutes les classes</option>
                {uniqueGroups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.nom}
                    {group.niveau?.specialite?.nom && ` - ${group.niveau.specialite.nom}`}
                    {group.niveau?.nom && ` (${group.niveau.nom})`}
                  </option>
                ))}
              </select>
            </div>

            {/* View Mode */}
            {/* View Mode */}
            <div>
              <label className="block text-sm font-medium mb-2">Mode d'affichage</label>
              <div className="flex space-x-2">
                <Button
                  variant={viewMode === 'week' ? 'default' : 'outline'}
                  onClick={() => setViewMode('week')}
                  className="flex-1"
                >
                  <Grid3x3 className="mr-2 h-4 w-4" />
                  Vue Semaine
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  onClick={() => setViewMode('list')}
                  className="flex-1"
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
                <Button variant="outline" onClick={previousWeek} size="icon">
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="outline" onClick={thisWeek} className="flex-1">
                  <Calendar className="mr-2 h-4 w-4" />
                  Cette semaine
                </Button>
                <Button variant="outline" onClick={nextWeek} size="icon">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Refresh Button */}
            <div>
              <label className="block text-sm font-medium mb-2">Actualiser</label>
              <Button 
                variant="outline" 
                onClick={() => loadSchedules()}
                disabled={loading}
                className="w-full"
              >
                <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                {loading ? 'Chargement...' : 'Rafraîchir'}
              </Button>
            </div>
          </div>

          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              Semaine du {formatDate(currentWeekStart)} au {formatDate(weekDays[6])}
            </p>
            {selectedGroup !== 'all' && (
              <p className="text-sm text-blue-600 mt-1">
                Filtré pour: {uniqueGroups.find(g => g.id === selectedGroup)?.nom}
              </p>
            )}
            {!loading && (
              <p className="text-xs text-gray-500 mt-2">
                📊 {schedules.length} session(s) chargée(s) | 
                {selectedGroup === 'all' ? ' Toutes les classes' : ` ${filteredSchedules.length} session(s) filtrée(s)`}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center py-16">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin" />
            <p className="text-sm text-muted-foreground">Chargement des emplois du temps...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
            <Button onClick={loadSchedules} className="mt-4" variant="outline">
              Réessayer
            </Button>
          </CardContent>
        </Card>
      )}

      {/* No Data Warning */}
      {!loading && !error && schedules.length === 0 && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="text-yellow-600 text-4xl">⚠️</div>
              <div>
                <h3 className="text-yellow-800 font-bold text-lg mb-2">Aucune session trouvée</h3>
                <p className="text-yellow-700 mb-4">
                  Aucun emploi du temps n'a été trouvé pour la semaine du {formatDate(currentWeekStart)} au {formatDate(weekDays[6])}.
                </p>
                <div className="space-y-2 text-sm text-yellow-600">
                  <p>• Vérifiez que des emplois du temps ont été créés pour votre département</p>
                  <p>• Essayez de naviguer vers une autre semaine</p>
                  <p>• Contactez l'administrateur si le problème persiste</p>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button onClick={thisWeek} variant="outline" size="sm">
                    Revenir à cette semaine
                  </Button>
                  <Button onClick={loadSchedules} variant="outline" size="sm">
                    Recharger
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Week View */}
      {!loading && !error && viewMode === 'week' && schedules.length > 0 && (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1400px] border-collapse">
                <thead>
                  <tr className="bg-gray-100">
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
                  <tr>
                    {weekDays.map((day, dayIdx) => {
                      const daySchedules = getSchedulesForDay(dayIdx)
                        .sort((a, b) => new Date(a.heure_debut).getTime() - new Date(b.heure_debut).getTime());

                      return (
                        <td key={dayIdx} className="px-3 py-3 border border-gray-300 align-top bg-gray-50">
                          <div className="space-y-2 min-h-[400px]">
                            {daySchedules.length > 0 ? (
                              daySchedules.map((schedule) => (
                                <div
                                  key={schedule.id}
                                  className="bg-gradient-to-br from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-3 hover:shadow-lg transition-all cursor-pointer"
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="text-xs font-bold text-blue-700 bg-blue-100 px-2 py-1 rounded">
                                      {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                                    </div>
                                  </div>
                                  <div className="font-bold text-blue-900 text-sm mb-2 truncate">
                                    {schedule.matiere?.nom || 'N/A'}
                                  </div>
                                  <div className="space-y-1 text-xs text-gray-700">
                                    <div className="flex items-center gap-1">
                                      <span>👥</span>
                                      <span className="font-medium text-indigo-700 truncate">
                                        {schedule.groupe?.nom}
                                      </span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <span>👨‍🏫</span>
                                      <span className="truncate">
                                        {schedule.enseignant?.prenom} {schedule.enseignant?.nom}
                                      </span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <span>📍</span>
                                      <span className="font-medium">{schedule.salle?.code || 'N/A'}</span>
                                    </div>
                                  </div>
                                </div>
                              ))
                            ) : (
                              <div className="h-full flex flex-col items-center justify-center text-gray-400 py-12">
                                <Calendar className="h-12 w-12 mb-2 opacity-30" />
                                <p className="text-xs">Aucune session</p>
                              </div>
                            )}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* List View - Grouped by Day */}
      {!loading && !error && viewMode === 'list' && schedules.length > 0 && (
        <div className="space-y-6">
          {filteredSchedules.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Aucun emploi du temps trouvé pour cette semaine</p>
              </CardContent>
            </Card>
          ) : (
            schedulesByDay.map(({ day, dayName, schedules: daySchedules }) => (
              daySchedules.length > 0 && (
                <div key={day.toISOString()}>
                  <h3 className="text-lg font-bold mb-3 capitalize flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-blue-600" />
                    {dayName} - {formatDate(day)}
                    <span className="text-sm font-normal text-muted-foreground ml-2">
                      ({daySchedules.length} session{daySchedules.length > 1 ? 's' : ''})
                    </span>
                  </h3>
                  <div className="space-y-3">
                    {daySchedules
                      .sort((a, b) => new Date(a.heure_debut).getTime() - new Date(b.heure_debut).getTime())
                      .map((schedule) => (
                        <Card key={schedule.id} className="hover:shadow-md transition-shadow">
                          <CardContent className="pt-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">Horaire</div>
                                <div className="font-semibold text-sm">
                                  {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                                </div>
                              </div>
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">Matière</div>
                                <div className="font-semibold text-sm">{schedule.matiere?.nom || 'N/A'}</div>
                              </div>
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">Groupe</div>
                                <div className="font-semibold text-sm text-blue-700">
                                  {schedule.groupe?.nom || 'N/A'}
                                </div>
                                {schedule.groupe?.niveau?.specialite?.nom && (
                                  <div className="text-xs text-muted-foreground">
                                    {schedule.groupe.niveau.specialite.nom}
                                  </div>
                                )}
                              </div>
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">Enseignant</div>
                                <div className="font-semibold text-sm">
                                  {schedule.enseignant?.prenom} {schedule.enseignant?.nom}
                                </div>
                              </div>
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">Salle</div>
                                <div className="font-semibold text-sm">📍 {schedule.salle?.code || 'N/A'}</div>
                              </div>
                            </div>
                            {schedule.status !== 'PLANNED' && (
                              <div className="mt-3 pt-3 border-t">
                                <span
                                  className={`px-2 py-1 rounded-full text-xs font-semibold ${
                                    schedule.status === 'CANCELED'
                                      ? 'bg-red-100 text-red-800'
                                      : 'bg-yellow-100 text-yellow-800'
                                  }`}
                                >
                                  {schedule.status}
                                </span>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                  </div>
                </div>
              )
            ))
          )}
        </div>
      )}

      {/* Statistics */}
      {!loading && !error && filteredSchedules.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredSchedules.length}</div>
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
                {filteredSchedules.filter((s) => s.status === 'PLANNED').length}
              </div>
              <p className="text-xs text-muted-foreground">sessions actives</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Groupes</CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {new Set(filteredSchedules.map((s) => s.groupe?.id).filter(Boolean)).size}
              </div>
              <p className="text-xs text-muted-foreground">différents</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Enseignants</CardTitle>
              <Calendar className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {new Set(filteredSchedules.map((s) => s.enseignant?.id).filter(Boolean)).size}
              </div>
              <p className="text-xs text-muted-foreground">impliqués</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Salles</CardTitle>
              <Calendar className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {new Set(filteredSchedules.map((s) => s.salle?.id).filter(Boolean)).size}
              </div>
              <p className="text-xs text-muted-foreground">utilisées</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
