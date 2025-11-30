'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminManagementApi, DashboardStats } from '@/lib/admin-api';
import { globalCrudApi } from '@/lib/admin-global-api';

export default function AdminDashboard() {
  const { admin, loading: authLoading, logout } = useAdminAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  useEffect(() => {
    if (admin) {
      loadDashboardStats();
    }
  }, [admin]);

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      
      // Load from both old API and new Global API
      const [oldStatsResult, departments, rooms, teachers, students] = await Promise.all([
        adminManagementApi.getDashboardStats(),
        globalCrudApi.departments.list({ limit: 1 }),
        globalCrudApi.rooms.list({ limit: 1 }),
        globalCrudApi.teachers.list({ limit: 1 }),
        globalCrudApi.students.list({ limit: 1 }),
      ]);
      
      // Merge old stats with new global data
      let mergedStats: DashboardStats = oldStatsResult.data || {
        overview: {
          totalUsers: 0,
          totalStudents: 0,
          totalTeachers: 0,
          totalDepartmentHeads: 0,
          recentRegistrations: 0
        },
        universityStructure: {
          faculties: 0,
          departments: 0,
          specialties: 0,
          levels: 0,
          groups: 0
        },
        roleDistribution: {},
        departmentStats: {
          studentsByDepartment: {},
          teachersByDepartment: {}
        }
      };
      
      // Add global CRUD counts to university structure
      mergedStats.universityStructure.departments = departments.total || 0;
      mergedStats.universityStructure.rooms = rooms.total || 0;
      
      // Add to overview if available
      mergedStats.overview.globalDepartments = departments.total || 0;
      mergedStats.overview.globalRooms = rooms.total || 0;
      mergedStats.overview.globalTeachers = teachers.total || 0;
      mergedStats.overview.globalStudents = students.total || 0;
      
      setStats(mergedStats);
      
    } catch (error: any) {
      setError(error.message || 'Error loading dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  if (authLoading || !admin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-purple-400 mx-auto mb-4"></div>
            <div className="absolute inset-0 rounded-full h-20 w-20 border-4 border-purple-200/20 mx-auto animate-pulse"></div>
          </div>
          <p className="text-white text-lg font-medium">Loading Admin Panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="relative bg-gradient-to-r from-purple-900/80 to-indigo-900/80 backdrop-blur-xl border-b border-white/10 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Admin Control Center</h1>
                <p className="text-purple-200 text-sm">University Platform Management</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              {/* Clock */}
              <div className="text-right hidden lg:block">
                <p className="text-purple-200 text-xs font-medium">Current Time</p>
                <p className="text-white font-mono text-sm">
                  {currentTime.toLocaleTimeString('en-US', { hour12: false })}
                </p>
              </div>

              {/* User Info */}
              <div className="text-right">
                <p className="text-purple-200 text-xs font-medium">Logged in as</p>
                <p className="text-white font-semibold">{admin.firstName} {admin.lastName}</p>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 px-5 py-2.5 rounded-xl text-white text-sm font-semibold transition-all duration-300 shadow-lg shadow-red-500/50 hover:shadow-xl hover:scale-105 flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Admin Info Card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl p-6 mb-8 border border-white/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Administrator Profile</h2>
                <div className="flex items-center space-x-6 text-sm">
                  <div className="flex items-center space-x-2">
                    <svg className="w-4 h-4 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span className="text-purple-200">{admin.firstName} {admin.lastName}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <svg className="w-4 h-4 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span className="text-purple-200">{admin.email}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <svg className="w-4 h-4 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                    <span className="text-purple-200">{admin.login}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end space-y-2">
              <div className="bg-gradient-to-r from-purple-500 to-pink-600 px-4 py-2 rounded-full shadow-lg">
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span className="text-white font-bold text-sm">ADMIN</span>
                </div>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1 bg-green-500/20 rounded-full border border-green-400/30">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-green-200 text-xs font-medium">Active Session</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Stats */}
        {loading ? (
          <div className="text-center py-16">
            <div className="relative inline-block">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-400 mb-4"></div>
              <div className="absolute inset-0 rounded-full h-16 w-16 border-4 border-purple-200/20 animate-pulse"></div>
            </div>
            <p className="text-purple-200 text-lg font-medium">Loading Analytics...</p>
          </div>
        ) : error ? (
          <div className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 text-red-200 px-6 py-4 rounded-2xl mb-8">
            <div className="flex items-center">
              <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <span className="font-semibold">Error Loading Data: </span>
                <span>{error}</span>
              </div>
              <button 
                onClick={loadDashboardStats}
                className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-lg text-white text-sm font-semibold transition-colors ml-4"
              >
                Retry
              </button>
            </div>
          </div>
        ) : stats ? (
          <div className="space-y-8">
            {/* Overview Stats */}
            <div>
              <div className="flex items-center mb-6">
                <div className="w-1 h-8 bg-gradient-to-b from-purple-500 to-pink-600 rounded-full mr-3"></div>
                <h3 className="text-2xl font-bold text-white">Platform Overview</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-blue-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-blue-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-blue-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-blue-300 mb-1">{stats.overview?.totalUsers || 0}</div>
                  <div className="text-blue-200 font-medium">Total Users</div>
                </div>

                <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-green-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-green-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M12 14l9-5-9-5-9 5 9 5z" />
                        <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
                      </svg>
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-green-300 mb-1">{stats.overview?.totalStudents || 0}</div>
                  <div className="text-green-200 font-medium">Students</div>
                </div>

                <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-purple-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-purple-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-purple-300 mb-1">{stats.overview?.totalTeachers || 0}</div>
                  <div className="text-purple-200 font-medium">Teachers</div>
                </div>

                <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-orange-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-orange-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-orange-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-orange-300 mb-1">{stats.overview?.totalDepartmentHeads || 0}</div>
                  <div className="text-orange-200 font-medium">Dept. Heads</div>
                </div>

                <div className="bg-gradient-to-br from-pink-500/20 to-pink-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-pink-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 bg-pink-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-pink-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-pink-300 mb-1">{stats.overview?.recentRegistrations || 0}</div>
                  <div className="text-pink-200 font-medium">New Registrations</div>
                </div>
              </div>
            </div>

            {/* University Structure */}
            <div>
              <div className="flex items-center mb-6">
                <div className="w-1 h-8 bg-gradient-to-b from-indigo-500 to-cyan-600 rounded-full mr-3"></div>
                <h3 className="text-2xl font-bold text-white">University Structure</h3>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {[
                  { label: 'Faculties', value: stats.universityStructure?.faculties || 0, color: 'indigo' },
                  { label: 'Departments', value: stats.universityStructure?.departments || 0, color: 'blue' },
                  { label: 'Specialties', value: stats.universityStructure?.specialties || 0, color: 'cyan' },
                  { label: 'Levels', value: stats.universityStructure?.levels || 0, color: 'teal' },
                  { label: 'Groups', value: stats.universityStructure?.groups || 0, color: 'emerald' },
                ].map((item, idx) => (
                  <div key={idx} className={`bg-${item.color}-500/10 backdrop-blur-sm rounded-xl shadow-lg p-4 border border-${item.color}-400/20 text-center hover:bg-${item.color}-500/20 transition-all duration-300`}>
                    <div className={`text-3xl font-bold text-${item.color}-300 mb-1`}>{item.value}</div>
                    <div className={`text-${item.color}-200 text-sm font-medium`}>{item.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Global Resources */}
            <div>
              <div className="flex items-center mb-6">
                <div className="w-1 h-8 bg-gradient-to-b from-cyan-500 to-blue-600 rounded-full mr-3"></div>
                <h3 className="text-2xl font-bold text-white">Global Resources</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-gradient-to-br from-pink-500/20 to-rose-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-pink-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-pink-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-7 h-7 text-pink-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-pink-300">{stats.overview?.globalDepartments || 0}</div>
                      <div className="text-pink-200 text-sm font-medium">Departments</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-cyan-500/20 to-blue-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-cyan-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-cyan-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-7 h-7 text-cyan-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-cyan-300">{stats.overview?.globalRooms || 0}</div>
                      <div className="text-cyan-200 text-sm font-medium">Classrooms</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-purple-500/20 to-violet-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-purple-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-purple-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-7 h-7 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-purple-300">{stats.overview?.globalTeachers || 0}</div>
                      <div className="text-purple-200 text-sm font-medium">Teachers</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-green-500/20 to-emerald-600/20 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-green-400/30 hover:scale-105 transition-transform duration-300">
                  <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-green-500/30 rounded-xl flex items-center justify-center">
                      <svg className="w-7 h-7 text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path d="M12 14l9-5-9-5-9 5 9 5z" />
                        <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-green-300">{stats.overview?.globalStudents || 0}</div>
                      <div className="text-green-200 text-sm font-medium">Students</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {/* Management Actions */}
        <div className="mt-12">
          <div className="flex items-center mb-6">
            <div className="w-1 h-8 bg-gradient-to-b from-amber-500 to-orange-600 rounded-full mr-3"></div>
            <h3 className="text-2xl font-bold text-white">Quick Actions</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { href: '/global-management', icon: '🌐', title: 'Global Management', desc: 'Manage departments, specialties, levels, groups, rooms & subjects', gradient: 'from-pink-500 to-rose-600' },
              { href: '/timetable-admin', icon: '📅', title: 'Timetable Viewer', desc: 'View all timetables across departments', gradient: 'from-cyan-500 to-blue-600' },
              { href: '/students', icon: '👨‍🎓', title: 'Student Management', desc: 'Create, edit, and manage student accounts', gradient: 'from-green-500 to-emerald-600' },
              { href: '/teachers', icon: '👨‍🏫', title: 'Teacher Management', desc: 'Create, edit, and manage teacher accounts', gradient: 'from-purple-500 to-violet-600' },
              { href: '/department-heads', icon: '👨‍💼', title: 'Department Heads', desc: 'Manage department head assignments', gradient: 'from-orange-500 to-amber-600' },
              { href: '/bulk-import', icon: '📊', title: 'Bulk Import', desc: 'Import students & teachers from Excel', gradient: 'from-indigo-500 to-purple-600' },
            ].map((action, idx) => (
              <a 
                key={idx}
                href={action.href} 
                className="group bg-white/10 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20 hover:bg-white/15 hover:scale-105 transition-all duration-300"
              >
                <div className={`w-16 h-16 bg-gradient-to-br ${action.gradient} rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <span className="text-3xl">{action.icon}</span>
                </div>
                <h4 className="font-bold text-white text-lg mb-2">{action.title}</h4>
                <p className="text-purple-200 text-sm leading-relaxed">{action.desc}</p>
                <div className="mt-4 flex items-center text-purple-300 text-sm font-medium group-hover:text-purple-200">
                  <span>Access</span>
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </a>
            ))}
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-12 bg-gradient-to-r from-amber-500/20 to-orange-500/20 backdrop-blur-xl border border-amber-400/30 p-6 rounded-2xl">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-amber-500/30 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-amber-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-amber-200 font-bold text-lg mb-2">Security & Compliance</h4>
              <p className="text-amber-100 text-sm leading-relaxed">
                This admin panel operates on a dedicated secure port (3001) with enhanced security protocols. 
                All administrative actions are logged and monitored. Unauthorized access attempts are tracked and reported.
              </p>
              <div className="mt-3 flex items-center space-x-4 text-xs text-amber-200">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>SSL Encrypted</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>Audit Logging Active</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>Session Secured</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}