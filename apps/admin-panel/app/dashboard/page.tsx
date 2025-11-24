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
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-red-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold">🔐 Admin Panel</h1>
              <span className="ml-4 px-3 py-1 bg-red-700 rounded-full text-sm">
                Secure Access
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-red-100">Welcome back,</p>
                <p className="font-semibold">{admin.firstName} {admin.lastName}</p>
              </div>
              <button
                onClick={handleLogout}
                className="bg-red-700 hover:bg-red-600 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
              >
                🚪 Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Admin Info Card */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border-l-4 border-red-600">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Administrator Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Name:</span>
                  <p className="font-semibold">{admin.firstName} {admin.lastName}</p>
                </div>
                <div>
                  <span className="text-gray-600">Email:</span>
                  <p className="font-semibold">{admin.email}</p>
                </div>
                <div>
                  <span className="text-gray-600">Login:</span>
                  <p className="font-semibold">{admin.login}</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="bg-red-100 text-red-800 px-4 py-2 rounded-full font-semibold">
                🛡️ ADMIN
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Stats */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-red-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard statistics...</p>
          </div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">Error: {error}</span>
            </div>
            <button 
              onClick={loadDashboardStats}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        ) : stats ? (
          <div className="space-y-8">
            {/* Overview Stats */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 Platform Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
                  <div className="text-2xl font-bold text-blue-600">{stats.overview?.totalUsers || 0}</div>
                  <div className="text-gray-600">Total Users</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
                  <div className="text-2xl font-bold text-green-600">{stats.overview?.totalStudents || 0}</div>
                  <div className="text-gray-600">Students</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
                  <div className="text-2xl font-bold text-purple-600">{stats.overview?.totalTeachers || 0}</div>
                  <div className="text-gray-600">Teachers</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
                  <div className="text-2xl font-bold text-orange-600">{stats.overview?.totalDepartmentHeads || 0}</div>
                  <div className="text-gray-600">Dept. Heads</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
                  <div className="text-2xl font-bold text-red-600">{stats.overview?.recentRegistrations || 0}</div>
                  <div className="text-gray-600">Recent Registrations</div>
                </div>
              </div>
            </div>

            {/* University Structure */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">🏛️ University Structure</h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <div className="text-2xl font-bold text-indigo-600">{stats.universityStructure?.faculties || 0}</div>
                  <div className="text-gray-600">Faculties</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <div className="text-2xl font-bold text-indigo-600">{stats.universityStructure?.departments || 0}</div>
                  <div className="text-gray-600">Departments</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <div className="text-2xl font-bold text-indigo-600">{stats.universityStructure?.specialties || 0}</div>
                  <div className="text-gray-600">Specialties</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <div className="text-2xl font-bold text-indigo-600">{stats.universityStructure?.levels || 0}</div>
                  <div className="text-gray-600">Levels</div>
                </div>
                <div className="bg-white rounded-lg shadow p-6 text-center">
                  <div className="text-2xl font-bold text-indigo-600">{stats.universityStructure?.groups || 0}</div>
                  <div className="text-gray-600">Groups</div>
                </div>
              </div>
            </div>

            {/* NEW: Global Resources Section */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">🌐 Global Resources (New API)</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg shadow p-6 text-center border-l-4 border-pink-500">
                  <div className="text-2xl font-bold text-pink-700">{stats.overview?.globalDepartments || 0}</div>
                  <div className="text-gray-700 font-medium">Global Departments</div>
                </div>
                <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-lg shadow p-6 text-center border-l-4 border-cyan-500">
                  <div className="text-2xl font-bold text-cyan-700">{stats.overview?.globalRooms || 0}</div>
                  <div className="text-gray-700 font-medium">Classrooms</div>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow p-6 text-center border-l-4 border-purple-500">
                  <div className="text-2xl font-bold text-purple-700">{stats.overview?.globalTeachers || 0}</div>
                  <div className="text-gray-700 font-medium">Teachers (Global)</div>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow p-6 text-center border-l-4 border-green-500">
                  <div className="text-2xl font-bold text-green-700">{stats.overview?.globalStudents || 0}</div>
                  <div className="text-gray-700 font-medium">Students (Global)</div>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {/* Management Actions */}
        <div className="mt-12">
          <h3 className="text-lg font-semibold text-gray-800 mb-6">🛠️ Administrative Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Global Management */}
            <a href="/global-management" className="block bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border-l-4 border-pink-500">
              <div className="text-center">
                <div className="text-3xl mb-3">🌐</div>
                <h4 className="font-semibold text-gray-800">Global Management</h4>
                <p className="text-sm text-gray-600 mt-2">Manage departments, specialties, levels, groups, rooms & subjects</p>
              </div>
            </a>
            
            {/* Timetable Admin */}
            <a href="/timetable-admin" className="block bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border-l-4 border-cyan-500">
              <div className="text-center">
                <div className="text-3xl mb-3">📅</div>
                <h4 className="font-semibold text-gray-800">Timetable (View Only)</h4>
                <p className="text-sm text-gray-600 mt-2">View all timetables across departments</p>
              </div>
            </a>

            <a href="/students" className="block bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border-l-4 border-green-500">
              <div className="text-center">
                <div className="text-3xl mb-3">👨‍🎓</div>
                <h4 className="font-semibold text-gray-800">Manage Students</h4>
                <p className="text-sm text-gray-600 mt-2">Create, edit, and manage student accounts</p>
              </div>
            </a>
            
            <a href="/teachers" className="block bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border-l-4 border-purple-500">
              <div className="text-center">
                <div className="text-3xl mb-3">👨‍🏫</div>
                <h4 className="font-semibold text-gray-800">Manage Teachers</h4>
                <p className="text-sm text-gray-600 mt-2">Create, edit, and manage teacher accounts</p>
              </div>
            </a>
            
            <a href="/department-heads" className="block bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border-l-4 border-orange-500">
              <div className="text-center">
                <div className="text-3xl mb-3">👨‍💼</div>
                <h4 className="font-semibold text-gray-800">Department Heads</h4>
                <p className="text-sm text-gray-600 mt-2">Manage department head assignments</p>
              </div>
            </a>
            
            <a href="/bulk-import" className="block bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border-l-4 border-indigo-500">
              <div className="text-center">
                <div className="text-3xl mb-3">📊</div>
                <h4 className="font-semibold text-gray-800">Bulk Import</h4>
                <p className="text-sm text-gray-600 mt-2">Import students & teachers from Excel</p>
              </div>
            </a>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-12 bg-red-50 border-l-4 border-red-600 p-6 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-9-2a9 9 0 1118 0 9 9 0 01-18 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-red-800 font-semibold">🛡️ Security Notice</h4>
              <p className="text-red-700 text-sm mt-1">
                This admin panel runs on a separate secure port (3001) with enhanced security measures.
                All administrative actions are logged and monitored for security purposes.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}