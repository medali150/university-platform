'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminScheduleApi, adminUniversityApi } from '@/lib/admin-api';

// Types
interface Department {
  id: string;
  name: string;
}

interface Specialty {
  id: string;
  name: string;
  departmentId: string;
}

interface Level {
  id: string;
  name: string;
  specialtyId: string;
}

interface Group {
  id: string;
  name: string;
  levelId: string;
}

interface Subject {
  id: string;
  name: string;
  levelId: string;
  teacher: {
    user: {
      firstName: string;
      lastName: string;
    };
  };
}

interface Room {
  id: string;
  code: string;
  type: string;
  capacity: number;
}

interface Schedule {
  id: string;
  date: string;
  startTime: string;
  endTime: string;
  room: Room;
  subject: Subject;
  group: Group;
  status: string;
}

interface TimeSlot {
  id: string;
  start: string;
  end: string;
  label: string;
}

const timeSlots: TimeSlot[] = [
  { id: '1', start: '08:00', end: '09:30', label: '08:00 - 09:30' },
  { id: '2', start: '09:30', end: '11:00', label: '09:30 - 11:00' },
  { id: '3', start: '11:15', end: '12:45', label: '11:15 - 12:45' },
  { id: '4', start: '12:45', end: '14:15', label: '12:45 - 14:15' },
  { id: '5', start: '14:15', end: '15:45', label: '14:15 - 15:45' },
  { id: '6', start: '15:45', end: '17:15', label: '15:45 - 17:15' },
];

const weekDays = [
  { id: 'monday', name: 'Monday', abbr: 'Mon' },
  { id: 'tuesday', name: 'Tuesday', abbr: 'Tue' },
  { id: 'wednesday', name: 'Wednesday', abbr: 'Wed' },
  { id: 'thursday', name: 'Thursday', abbr: 'Thu' },
  { id: 'friday', name: 'Friday', abbr: 'Fri' },
  { id: 'saturday', name: 'Saturday', abbr: 'Sat' },
];

export default function ScheduleManagement() {
  const { admin, loading: authLoading } = useAdminAuth();
  const router = useRouter();
  
  // State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Data state
  const [departments, setDepartments] = useState<Department[]>([]);
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [levels, setLevels] = useState<Level[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  
  // Selection state
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [selectedWeek, setSelectedWeek] = useState('');
  
  // Schedule creation state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedCell, setSelectedCell] = useState<{day: string, timeSlot: string} | null>(null);
  const [formData, setFormData] = useState({
    subjectId: '',
    roomId: '',
    date: '',
    startTime: '',
    endTime: '',
  });

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  useEffect(() => {
    if (admin) {
      loadInitialData();
    }
  }, [admin]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadDepartments(),
        loadRooms(),
      ]);
    } catch (error) {
      setError('Failed to load initial data');
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    try {
      const result = await adminUniversityApi.getDepartments();
      if (result.success && result.data) {
        setDepartments(result.data);
      } else {
        setError('Failed to load departments');
      }
    } catch (error) {
      setError('Error loading departments');
    }
  };

  const loadRooms = async () => {
    try {
      const result = await adminScheduleApi.getRooms();
      if (result.success && result.data) {
        setRooms(result.data);
      } else {
        setError('Failed to load rooms');
      }
    } catch (error) {
      setError('Error loading rooms');
    }
  };

  const handleDepartmentChange = async (departmentId: string) => {
    setSelectedDepartment(departmentId);
    setSelectedSpecialty('');
    setSelectedLevel('');
    setSelectedGroup('');
    
    if (departmentId) {
      try {
        const result = await adminUniversityApi.getSpecialties();
        if (result.success && result.data) {
          // Filter specialties by department
          const deptSpecialties = result.data.filter(s => s.departmentId === departmentId);
          setSpecialties(deptSpecialties);
        }
      } catch (error) {
        setError('Failed to load specialties');
      }
    } else {
      setSpecialties([]);
    }
  };

  const handleSpecialtyChange = async (specialtyId: string) => {
    setSelectedSpecialty(specialtyId);
    setSelectedLevel('');
    setSelectedGroup('');
    
    if (specialtyId) {
      try {
        const result = await adminUniversityApi.getLevelsBySpecialty(specialtyId);
        if (result.success && result.data) {
          setLevels(result.data);
        }
      } catch (error) {
        setError('Failed to load levels');
      }
    } else {
      setLevels([]);
    }
  };

  const handleLevelChange = async (levelId: string) => {
    setSelectedLevel(levelId);
    setSelectedGroup('');
    
    if (levelId) {
      try {
        const [groupsResult, subjectsResult] = await Promise.all([
          adminUniversityApi.getGroupsByLevel(levelId),
          adminScheduleApi.getSubjectsByLevel(levelId)
        ]);
        
        if (groupsResult.success && groupsResult.data) {
          setGroups(groupsResult.data);
        }
        
        if (subjectsResult.success && subjectsResult.data) {
          setSubjects(subjectsResult.data);
        }
      } catch (error) {
        setError('Failed to load groups and subjects');
      }
    } else {
      setGroups([]);
      setSubjects([]);
    }
  };

  const handleGroupChange = (groupId: string) => {
    setSelectedGroup(groupId);
    if (groupId && selectedWeek) {
      loadSchedules(groupId, selectedWeek);
    }
  };

  const handleWeekChange = (week: string) => {
    setSelectedWeek(week);
    if (selectedGroup && week) {
      loadSchedules(selectedGroup, week);
    }
  };

  const loadSchedules = async (groupId: string, week: string) => {
    try {
      setLoading(true);
      // Calculate start and end dates from week
      const [year, weekNum] = week.split('-W');
      const startDate = getDateOfWeek(parseInt(year), parseInt(weekNum));
      const endDate = new Date(startDate);
      endDate.setDate(startDate.getDate() + 6);
      
      const result = await adminScheduleApi.getSchedulesByGroup(
        groupId, 
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );
      
      if (result.success && result.data) {
        setSchedules(result.data);
      } else {
        setError('Failed to load schedules');
        setSchedules([]);
      }
    } catch (error) {
      setError('Failed to load schedules');
      setSchedules([]);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get date of week
  const getDateOfWeek = (year: number, week: number): Date => {
    const simple = new Date(year, 0, 1 + (week - 1) * 7);
    const dow = simple.getDay();
    const ISOweekStart = simple;
    if (dow <= 4) {
      ISOweekStart.setDate(simple.getDate() - simple.getDay() + 1);
    } else {
      ISOweekStart.setDate(simple.getDate() + 8 - simple.getDay());
    }
    return ISOweekStart;
  };

  const handleCellClick = (day: string, timeSlot: TimeSlot) => {
    if (!selectedGroup || !selectedWeek) {
      setError('Please select a group and week first');
      return;
    }
    
    setSelectedCell({ day, timeSlot: timeSlot.id });
    setFormData({
      subjectId: '',
      roomId: '',
      date: '',
      startTime: timeSlot.start,
      endTime: timeSlot.end,
    });
    setShowCreateForm(true);
  };

  const handleCreateSchedule = async () => {
    if (!formData.subjectId || !formData.roomId || !formData.date) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      
      // First check for conflicts
      const conflictCheck = await adminScheduleApi.checkConflicts({
        date: formData.date,
        startTime: formData.startTime,
        endTime: formData.endTime,
        roomId: formData.roomId,
        subjectId: formData.subjectId,
        groupId: selectedGroup!
      });

      if (!conflictCheck.success || (conflictCheck.data && conflictCheck.data.length > 0)) {
        setError('Schedule conflicts detected. Please choose a different time or room.');
        return;
      }

      // Create the schedule
      const result = await adminScheduleApi.createSchedule({
        date: formData.date,
        startTime: formData.startTime,
        endTime: formData.endTime,
        roomId: formData.roomId,
        subjectId: formData.subjectId,
        groupId: selectedGroup!
      });

      if (result.success) {
        setSuccess('Schedule created successfully!');
        setShowCreateForm(false);
        setSelectedCell(null);
        setFormData({
          subjectId: '',
          roomId: '',
          date: '',
          startTime: '',
          endTime: '',
        });
        // Reload schedules
        if (selectedGroup && selectedWeek) {
          await loadSchedules(selectedGroup, selectedWeek);
        }
      } else {
        setError(result.error || 'Failed to create schedule');
      }
    } catch (error) {
      setError('Failed to create schedule');
    } finally {
      setLoading(false);
    }
  };

  const getScheduleForCell = (day: string, timeSlotId: string): Schedule | null => {
    return schedules.find(schedule => {
      const scheduleDay = new Date(schedule.date).toLocaleDateString('en', { weekday: 'long' }).toLowerCase();
      const scheduleTimeSlot = timeSlots.find(slot => 
        schedule.startTime === slot.start && schedule.endTime === slot.end
      );
      return scheduleDay === day && scheduleTimeSlot?.id === timeSlotId;
    }) || null;
  };

  if (authLoading || !admin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading schedule management...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="mr-4 p-2 hover:bg-blue-700 rounded-lg transition-colors"
              >
                ← Back
              </button>
              <h1 className="text-2xl font-bold">📅 Schedule Management</h1>
            </div>
            <div className="text-sm">
              <p>Department Head Panel</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Filters Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-6">🎯 Filter Options</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
              <select
                value={selectedDepartment}
                onChange={(e) => handleDepartmentChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Department</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>{dept.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Specialty</label>
              <select
                value={selectedSpecialty}
                onChange={(e) => handleSpecialtyChange(e.target.value)}
                disabled={!selectedDepartment}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              >
                <option value="">Select Specialty</option>
                {specialties.map(specialty => (
                  <option key={specialty.id} value={specialty.id}>{specialty.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Level</label>
              <select
                value={selectedLevel}
                onChange={(e) => handleLevelChange(e.target.value)}
                disabled={!selectedSpecialty}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              >
                <option value="">Select Level</option>
                {levels.map(level => (
                  <option key={level.id} value={level.id}>{level.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Group</label>
              <select
                value={selectedGroup}
                onChange={(e) => handleGroupChange(e.target.value)}
                disabled={!selectedLevel}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              >
                <option value="">Select Group</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>{group.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Week</label>
              <input
                type="week"
                value={selectedWeek}
                onChange={(e) => handleWeekChange(e.target.value)}
                disabled={!selectedGroup}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={() => {
                  setSelectedDepartment('');
                  setSelectedSpecialty('');
                  setSelectedLevel('');
                  setSelectedGroup('');
                  setSelectedWeek('');
                  setSchedules([]);
                }}
                className="w-full px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
            <button 
              onClick={() => setError('')}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              {success}
            </div>
            <button 
              onClick={() => setSuccess('')}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Schedule Timetable */}
        {selectedGroup && selectedWeek && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">
                🗓️ Timetable - {groups.find(g => g.id === selectedGroup)?.name}
              </h2>
              <div className="text-sm text-gray-600">
                Week: {selectedWeek}
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="border border-gray-300 p-3 bg-gray-100 text-left font-semibold text-gray-700">
                      Time
                    </th>
                    {weekDays.map(day => (
                      <th key={day.id} className="border border-gray-300 p-3 bg-gray-100 text-center font-semibold text-gray-700 min-w-40">
                        {day.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {timeSlots.map(timeSlot => (
                    <tr key={timeSlot.id}>
                      <td className="border border-gray-300 p-3 bg-gray-50 font-medium text-sm text-gray-700">
                        {timeSlot.label}
                      </td>
                      {weekDays.map(day => {
                        const schedule = getScheduleForCell(day.id, timeSlot.id);
                        return (
                          <td
                            key={`${day.id}-${timeSlot.id}`}
                            className="border border-gray-300 p-2 h-20 cursor-pointer hover:bg-blue-50 transition-colors relative"
                            onClick={() => !schedule && handleCellClick(day.id, timeSlot)}
                          >
                            {schedule ? (
                              <div className="bg-blue-100 rounded-lg p-2 h-full">
                                <div className="font-semibold text-xs text-blue-800 truncate">
                                  {schedule.subject.name}
                                </div>
                                <div className="text-xs text-blue-600 truncate">
                                  {schedule.room.code}
                                </div>
                                <div className="text-xs text-blue-500 truncate">
                                  {schedule.subject.teacher.user.firstName} {schedule.subject.teacher.user.lastName}
                                </div>
                              </div>
                            ) : (
                              <div className="h-full flex items-center justify-center text-gray-400 hover:text-blue-500">
                                <span className="text-2xl">+</span>
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Instructions */}
        {(!selectedGroup || !selectedWeek) && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-blue-800 font-semibold">📋 How to Create Schedules</h4>
                <div className="text-blue-700 text-sm mt-2 space-y-1">
                  <p>1. Select Department, Specialty, Level, and Group from the filters above</p>
                  <p>2. Choose the week you want to create schedules for</p>
                  <p>3. Click on any empty time slot in the timetable to add a new schedule</p>
                  <p>4. Fill in the subject, room, and date information</p>
                  <p>5. Save the schedule and it will appear in the timetable</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Create Schedule Modal */}
      {showCreateForm && selectedCell && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-800">➕ Create New Schedule</h3>
              <button
                onClick={() => {
                  setShowCreateForm(false);
                  setSelectedCell(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Subject *</label>
                <select
                  value={formData.subjectId}
                  onChange={(e) => setFormData({ ...formData, subjectId: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Subject</option>
                  {subjects.map(subject => (
                    <option key={subject.id} value={subject.id}>
                      {subject.name} - {subject.teacher.user.firstName} {subject.teacher.user.lastName}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Room *</label>
                <select
                  value={formData.roomId}
                  onChange={(e) => setFormData({ ...formData, roomId: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Room</option>
                  {rooms.map(room => (
                    <option key={room.id} value={room.id}>
                      {room.code} ({room.type}) - Capacity: {room.capacity}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date *</label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Time</label>
                  <input
                    type="time"
                    value={formData.startTime}
                    onChange={(e) => setFormData({ ...formData, startTime: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Time</label>
                  <input
                    type="time"
                    value={formData.endTime}
                    onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-2">Selected Time Slot:</h4>
                <p className="text-sm text-gray-600">
                  Day: {weekDays.find(d => d.id === selectedCell.day)?.name}<br/>
                  Time: {timeSlots.find(t => t.id === selectedCell.timeSlot)?.label}
                </p>
              </div>
            </div>

            <div className="flex justify-end space-x-4 mt-6">
              <button
                onClick={() => {
                  setShowCreateForm(false);
                  setSelectedCell(null);
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateSchedule}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Schedule'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}