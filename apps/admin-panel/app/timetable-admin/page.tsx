'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { timetableApi, globalCrudApi } from '@/lib/admin-global-api';

type ViewMode = 'groups' | 'teachers';

// Time slots matching the standard university schedule
const TIME_SLOTS = [
  { start: '08:30', end: '10:00' },
  { start: '10:10', end: '11:40' },
  { start: '11:50', end: '13:20' },
  { start: '14:30', end: '16:00' },
  { start: '16:10', end: '17:40' },
];

const DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];

export default function TimetableAdminPage() {
  const { admin, loading: authLoading } = useAdminAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('groups');
  const [selectedEntity, setSelectedEntity] = useState('');

  // Reference data
  const [departments, setDepartments] = useState<any[]>([]);
  const [teachers, setTeachers] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  useEffect(() => {
    if (admin) {
      loadReferenceData();
      loadSessions();
    }
  }, [admin]);

  const loadReferenceData = async () => {
    try {
      console.log('Loading reference data...');
      const [deptsRes, teachersRes, roomsRes, subjectsRes, groupsRes] = await Promise.all([
        globalCrudApi.departments.list({ limit: 100 }),
        globalCrudApi.teachers.list({ limit: 100 }),
        globalCrudApi.rooms.list({ limit: 100 }),
        globalCrudApi.subjects.list({ limit: 100 }),
        globalCrudApi.groups.list({ limit: 100 }),
      ]);

      console.log('Groups loaded:', groupsRes);
      console.log('Subjects loaded:', subjectsRes);
      console.log('Teachers loaded:', teachersRes);
      console.log('Rooms loaded:', roomsRes);
      
      setDepartments(deptsRes.data || []);
      setTeachers(teachersRes.data || []);
      setRooms(roomsRes.data || []);
      setSubjects(subjectsRes.data || []);
      setGroups(groupsRes.data || []);
    } catch (error) {
      console.error('Failed to load reference data:', error);
      alert('Failed to load data: ' + (error as any).message);
    }
  };

  const loadSessions = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 500 };
      
      if (viewMode === 'groups' && selectedEntity) {
        params.group_id = selectedEntity;
      } else if (viewMode === 'teachers' && selectedEntity) {
        params.teacher_id = selectedEntity;
      }

      console.log('Loading sessions with params:', params);
      const response = await timetableApi.sessions.list(params);
      console.log('Sessions loaded:', response);
      setSessions(response.data || []);
    } catch (error: any) {
      console.error('Failed to load sessions:', error);
      alert('Failed to load sessions: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (admin && selectedEntity) {
      loadSessions();
    } else if (admin && !selectedEntity) {
      setSessions([]);
      setLoading(false);
    }
  }, [selectedEntity, viewMode]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📅 Timetable Administration (View Only)</h1>
              <p className="mt-1 text-sm text-gray-500">
                View weekly schedules for classes and teachers - Read-only access
              </p>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* View Mode Selector */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center gap-6">
            <div className="flex gap-2">
              <button
                onClick={() => { setViewMode('groups'); setSelectedEntity(''); }}
                className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                  viewMode === 'groups'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                👥 View by Groups
              </button>
              <button
                onClick={() => { setViewMode('teachers'); setSelectedEntity(''); }}
                className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                  viewMode === 'teachers'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                👨‍🏫 View by Teachers
              </button>
            </div>

            <div className="flex-1">
              <select
                value={selectedEntity}
                onChange={(e) => setSelectedEntity(e.target.value)}
                className="w-full max-w-md px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">
                  {viewMode === 'groups' ? 'Select a Group...' : 'Select a Teacher...'}
                </option>
                {viewMode === 'groups'
                  ? groups.map((g) => (
                      <option key={g.id} value={g.id}>
                        {g.nom} - {g.niveau?.nom || 'N/A'}
                      </option>
                    ))
                  : teachers.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.prenom} {t.nom} - {t.departement?.nom || 'N/A'}
                      </option>
                    ))}
              </select>
            </div>
          </div>
        </div>

        {/* Weekly Timetable Grid */}
        {selectedEntity ? (
          <WeeklyTimetableGrid
            sessions={sessions}
            loading={loading}
            viewMode={viewMode}
            entity={
              viewMode === 'groups'
                ? groups.find((g) => g.id === selectedEntity)
                : teachers.find((t) => t.id === selectedEntity)
            }
            onRefresh={loadSessions}
          />
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">📅</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              {viewMode === 'groups' ? 'Select a Group' : 'Select a Teacher'}
            </h3>
            <p className="text-gray-500">
              Choose a {viewMode === 'groups' ? 'group' : 'teacher'} from the dropdown above to view their weekly schedule
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

// Weekly Timetable Grid Component
function WeeklyTimetableGrid({ sessions, loading, viewMode, entity, onRefresh }: any) {
  const TIME_SLOTS = [
    { start: '08:30', end: '10:00' },
    { start: '10:10', end: '11:40' },
    { start: '11:50', end: '13:20' },
    { start: '14:30', end: '16:00' },
    { start: '16:10', end: '17:40' },
  ];

  const DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];

  const findSessionForSlot = (dayIndex: number, slotIndex: number) => {
    return sessions.find((session: any) => {
      if (session.day_of_week !== dayIndex) return false;
      const slot = TIME_SLOTS[slotIndex];
      return session.start_time === slot.start;
    });
  };

  // Calculate statistics
  const totalCourses = sessions.length;
  const daysWithSessions = new Set(sessions.map((s: any) => s.day_of_week)).size;
  const totalHours = sessions.reduce((acc: number, session: any) => {
    const [startHour, startMin] = session.start_time.split(':').map(Number);
    const [endHour, endMin] = session.end_time.split(':').map(Number);
    const duration = (endHour * 60 + endMin - (startHour * 60 + startMin)) / 60;
    return acc + duration;
  }, 0);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p>Loading schedule...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
        <h2 className="text-2xl font-bold mb-2">
          {viewMode === 'groups' ? '👥' : '👨‍🏫'} {entity?.nom || entity?.prenom + ' ' + entity?.nom}
        </h2>
        <p className="text-sm opacity-90">
          {viewMode === 'groups' 
            ? `Niveau: ${entity?.niveau?.nom || 'N/A'}` 
            : `Department: ${entity?.departement?.nom || 'N/A'}`}
        </p>
      </div>

      {/* Timetable Grid */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse min-w-[800px]">
          <thead>
            <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
              <th className="border border-gray-300 p-4 text-left font-bold text-gray-700 w-32">
                ⏰ Horaire
              </th>
              {DAYS_OF_WEEK.map((day) => (
                <th key={day} className="border border-gray-300 p-4 text-center font-bold text-gray-700">
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {TIME_SLOTS.map((slot, slotIndex) => (
              <tr key={slotIndex} className="hover:bg-gray-50 transition-colors">
                <td className="border border-gray-300 p-3 text-center bg-gradient-to-r from-blue-50 to-purple-50 font-semibold text-gray-700">
                  <div className="text-sm">{slot.start}</div>
                  <div className="text-xs text-gray-500">à</div>
                  <div className="text-sm">{slot.end}</div>
                </td>
                {DAYS_OF_WEEK.map((day, dayIndex) => {
                  const session = findSessionForSlot(dayIndex, slotIndex);
                  return (
                    <td
                      key={dayIndex}
                      className="border border-gray-300 p-2 align-top min-h-[120px]"
                    >
                      {session ? (
                        <div className="p-3 rounded-lg bg-gradient-to-br from-blue-50 to-purple-50 border-l-4 border-blue-500 hover:shadow-md transition-shadow">
                          <div className="font-semibold text-blue-900 text-sm mb-2 flex items-center gap-1">
                            <span>📚</span>
                            <span className="truncate">{session.subject?.name || 'N/A'}</span>
                          </div>
                          <div className="text-xs text-gray-600 space-y-1">
                            <div className="flex items-center gap-1">
                              <span>🕐</span>
                              <span>{session.start_time} - {session.end_time}</span>
                            </div>
                            {viewMode === 'groups' ? (
                              <div className="flex items-center gap-1">
                                <span>👨‍🏫</span>
                                <span className="truncate">{session.teacher?.name || 'N/A'}</span>
                              </div>
                            ) : (
                              <div className="flex items-center gap-1">
                                <span>👥</span>
                                <span className="truncate">{session.group?.name || 'N/A'}</span>
                              </div>
                            )}
                            <div className="flex items-center gap-1">
                              <span>📍</span>
                              <span className="truncate">{session.room?.code || 'TBA'}</span>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center text-gray-300 text-sm py-8">-</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Statistics Footer */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{totalCourses}</div>
            <div className="text-sm text-gray-600 mt-1">Total Courses</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{daysWithSessions}</div>
            <div className="text-sm text-gray-600 mt-1">Active Days</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{totalHours.toFixed(1)}h</div>
            <div className="text-sm text-gray-600 mt-1">Total Hours</div>
          </div>
        </div>
      </div>

      {sessions.length === 0 && (
        <div className="p-12 text-center text-gray-500">
          <div className="text-6xl mb-4">📅</div>
          <p className="text-xl">No sessions scheduled for this {viewMode === 'groups' ? 'group' : 'teacher'}</p>
        </div>
      )}
    </div>
  );
}
