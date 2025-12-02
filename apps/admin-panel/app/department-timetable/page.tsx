'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminScheduleApi } from '@/lib/admin-api';

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

interface Department {
  id: string;
  nom: string;
}

export default function DepartmentTimetable() {
  const { admin, loading: authLoading } = useAdminAuth();
  const router = useRouter();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'week' | 'list'>('week');
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(getWeekStart(new Date()));

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  useEffect(() => {
    if (admin) {
      loadDepartments();
    }
  }, [admin]);

  useEffect(() => {
    if (selectedDepartment) {
      loadSchedules();
    }
  }, [selectedDepartment, currentWeekStart]);

  function getWeekStart(date: Date): Date {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  }

  const loadDepartments = async () => {
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_URL || 'http://127.0.0.1:8000';
      const token = localStorage.getItem('admin_auth_token');
      
      const response = await fetch(`${API_BASE_URL}/departments/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDepartments(data);
        if (data.length > 0) {
          setSelectedDepartment(data[0].id);
        }
      }
    } catch (error: any) {
      console.error('Error loading departments:', error);
    }
  };

  const loadSchedules = async () => {
    if (!selectedDepartment) return;

    try {
      setLoading(true);
      setError('');

      const API_BASE_URL = process.env.NEXT_PUBLIC_ADMIN_API_URL || 'http://127.0.0.1:8000';
      const token = localStorage.getItem('admin_auth_token');
      
      // Calculate date range for current week
      const weekEnd = new Date(currentWeekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);

      const response = await fetch(
        `${API_BASE_URL}/admin/timetable/list?department_id=${selectedDepartment}&start_date=${currentWeekStart.toISOString().split('T')[0]}&end_date=${weekEnd.toISOString().split('T')[0]}&limit=1000`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSchedules(data.sessions || []);
      } else {
        setError('Failed to load schedules');
      }
    } catch (error: any) {
      setError(error.message || 'Error loading schedules');
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

  const getDayOfWeek = (dateStr: string): number => {
    const date = new Date(dateStr);
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
    return schedules.filter(s => getDayOfWeek(s.date) === dayIndex);
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

  if (authLoading || !admin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-purple-400 mx-auto mb-4"></div>
          <p className="text-white text-lg font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  const weekDays = getWeekDays();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-900/80 to-indigo-900/80 backdrop-blur-xl border-b border-white/10 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-purple-200 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Department Timetables</h1>
                <p className="text-purple-200 text-sm">View all schedules by department</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl p-6 mb-8 border border-white/20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Department Selection */}
            <div>
              <label className="block text-purple-200 text-sm font-medium mb-2">
                Department
              </label>
              <select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Select Department</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id} className="bg-slate-800">
                    {dept.nom}
                  </option>
                ))}
              </select>
            </div>

            {/* View Mode */}
            <div>
              <label className="block text-purple-200 text-sm font-medium mb-2">
                View Mode
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={() => setViewMode('week')}
                  className={`flex-1 px-4 py-2 rounded-xl font-medium transition-all ${
                    viewMode === 'week'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg'
                      : 'bg-white/10 text-purple-200 hover:bg-white/20'
                  }`}
                >
                  Week View
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`flex-1 px-4 py-2 rounded-xl font-medium transition-all ${
                    viewMode === 'list'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg'
                      : 'bg-white/10 text-purple-200 hover:bg-white/20'
                  }`}
                >
                  List View
                </button>
              </div>
            </div>

            {/* Week Navigation */}
            <div>
              <label className="block text-purple-200 text-sm font-medium mb-2">
                Week Navigation
              </label>
              <div className="flex space-x-2">
                <button
                  onClick={previousWeek}
                  className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button
                  onClick={thisWeek}
                  className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors text-sm font-medium"
                >
                  This Week
                </button>
                <button
                  onClick={nextWeek}
                  className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div className="mt-4 text-center">
            <p className="text-purple-200 text-sm">
              Week of {formatDate(currentWeekStart)} - {formatDate(weekDays[6])}
            </p>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-400 mx-auto mb-4"></div>
            <p className="text-purple-200 text-lg font-medium">Loading Schedules...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 text-red-200 px-6 py-4 rounded-2xl mb-8">
            <div className="flex items-center">
              <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Week View */}
        {!loading && viewMode === 'week' && (
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1200px]">
                <thead>
                  <tr className="bg-gradient-to-r from-purple-900/50 to-indigo-900/50">
                    <th className="px-4 py-3 text-left text-purple-200 text-sm font-semibold w-24">
                      Time
                    </th>
                    {weekDays.map((day, idx) => (
                      <th key={idx} className="px-4 py-3 text-center text-purple-200 text-sm font-semibold border-l border-white/10">
                        <div className="font-bold">{day.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                        <div className="text-xs text-purple-300">{formatDate(day)}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: 14 }, (_, i) => {
                    const hour = 8 + Math.floor(i / 2);
                    const minute = (i % 2) * 30;
                    const timeSlot = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                    
                    return (
                      <tr key={i} className="border-t border-white/10 hover:bg-white/5">
                        <td className="px-4 py-2 text-purple-200 text-sm font-medium">
                          {timeSlot}
                        </td>
                        {weekDays.map((day, dayIdx) => {
                          const daySchedules = getSchedulesForDay(dayIdx);
                          const matchingSchedule = daySchedules.find(s => {
                            const startTime = formatTime(s.heure_debut);
                            return startTime === timeSlot;
                          });

                          return (
                            <td key={dayIdx} className="px-2 py-2 border-l border-white/10">
                              {matchingSchedule && (
                                <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-400/30 rounded-lg p-2 text-xs">
                                  <div className="font-bold text-blue-200 mb-1">
                                    {matchingSchedule.matiere?.nom || 'N/A'}
                                  </div>
                                  <div className="text-purple-200">
                                    👨‍🏫 {matchingSchedule.enseignant?.prenom} {matchingSchedule.enseignant?.nom}
                                  </div>
                                  <div className="text-purple-300 mt-1">
                                    📍 {matchingSchedule.salle?.code || 'N/A'}
                                  </div>
                                  <div className="text-purple-300">
                                    👥 {matchingSchedule.groupe?.nom || 'N/A'}
                                  </div>
                                  <div className="text-purple-400 text-xs mt-1">
                                    {formatTime(matchingSchedule.heure_debut)} - {formatTime(matchingSchedule.heure_fin)}
                                  </div>
                                </div>
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* List View */}
        {!loading && viewMode === 'list' && (
          <div className="space-y-4">
            {schedules.length === 0 ? (
              <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl p-12 text-center border border-white/20">
                <svg className="w-16 h-16 text-purple-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-purple-200 text-lg font-medium">No schedules found for this week</p>
              </div>
            ) : (
              schedules.map((schedule) => (
                <div
                  key={schedule.id}
                  className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20 hover:bg-white/15 transition-all"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                      <div className="text-purple-300 text-sm mb-1">Date & Time</div>
                      <div className="text-white font-semibold">{formatDate(schedule.date)}</div>
                      <div className="text-purple-200 text-sm">
                        {formatTime(schedule.heure_debut)} - {formatTime(schedule.heure_fin)}
                      </div>
                    </div>
                    <div>
                      <div className="text-purple-300 text-sm mb-1">Subject</div>
                      <div className="text-white font-semibold">{schedule.matiere?.nom || 'N/A'}</div>
                    </div>
                    <div>
                      <div className="text-purple-300 text-sm mb-1">Teacher</div>
                      <div className="text-white font-semibold">
                        {schedule.enseignant?.prenom} {schedule.enseignant?.nom}
                      </div>
                    </div>
                    <div>
                      <div className="text-purple-300 text-sm mb-1">Room & Group</div>
                      <div className="text-white font-semibold">📍 {schedule.salle?.code || 'N/A'}</div>
                      <div className="text-purple-200 text-sm">👥 {schedule.groupe?.nom || 'N/A'}</div>
                    </div>
                  </div>
                  {schedule.status !== 'PLANNED' && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        schedule.status === 'CANCELED' ? 'bg-red-500/20 text-red-200' : 'bg-yellow-500/20 text-yellow-200'
                      }`}>
                        {schedule.status}
                      </span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Statistics */}
        {!loading && schedules.length > 0 && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-blue-400/30">
              <div className="text-blue-300 text-sm mb-1">Total Sessions</div>
              <div className="text-4xl font-bold text-blue-200">{schedules.length}</div>
            </div>
            <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-green-400/30">
              <div className="text-green-300 text-sm mb-1">Planned</div>
              <div className="text-4xl font-bold text-green-200">
                {schedules.filter(s => s.status === 'PLANNED').length}
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-purple-400/30">
              <div className="text-purple-300 text-sm mb-1">Unique Teachers</div>
              <div className="text-4xl font-bold text-purple-200">
                {new Set(schedules.map(s => s.enseignant?.id).filter(Boolean)).size}
              </div>
            </div>
            <div className="bg-gradient-to-br from-pink-500/20 to-pink-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-pink-400/30">
              <div className="text-pink-300 text-sm mb-1">Unique Groups</div>
              <div className="text-4xl font-bold text-pink-200">
                {new Set(schedules.map(s => s.groupe?.id).filter(Boolean)).size}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
