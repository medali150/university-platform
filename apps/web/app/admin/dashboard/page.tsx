'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, adminApi, DashboardStats } from '@/lib/api-utils';
import Link from 'next/link';

export default function AdminDashboard() {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Check if user is authenticated
      if (!authApi.isAuthenticated()) {
        router.push('/admin/login');
        return;
      }

      // Verify user is admin
      const userResult = await authApi.me();
      if (!userResult.success) {
        router.push('/admin/login');
        return;
      }

      if (userResult.data?.role !== 'ADMIN') {
        setError('Access denied. Admin privileges required.');
        return;
      }

      // Load dashboard data in parallel
      const [statsResult, healthResult, activityResult] = await Promise.all([
        adminApi.getDashboardStats(),
        adminApi.getSystemHealth(),
        adminApi.getRecentActivity(10)
      ]);

      if (statsResult.success && statsResult.data) {
        setDashboardStats(statsResult.data);
      } else {
        console.error('Failed to load dashboard stats:', statsResult.error);
      }

      if (healthResult.success && healthResult.data) {
        setSystemHealth(healthResult.data);
      }

      if (activityResult.success && activityResult.data) {
        setRecentActivity(activityResult.data);
      }

    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authApi.logout();
    router.push('/admin/login');
  };

  const currentUser = authApi.getCurrentUser();

  if (loading) {
    return (
      <div className="container">
        <div className="welcome">
          <h1>Loading Admin Dashboard...</h1>
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <div style={{ 
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #3498db',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              animation: 'spin 2s linear infinite',
              margin: '0 auto'
            }}></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="welcome">
          <h1>❌ Error</h1>
          <p style={{ color: '#dc3545' }}>{error}</p>
          <button onClick={() => router.push('/admin/login')} className="button">
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="welcome">
        <h1 className="title">🔐 Admin Dashboard</h1>
        
        {/* Current Admin Info */}
        <div style={{ 
          background: '#d4edda', 
          padding: '15px', 
          borderRadius: '8px', 
          border: '1px solid #c3e6cb',
          marginBottom: '30px'
        }}>
          <h3 style={{ color: '#155724', margin: '0 0 10px 0' }}>
            👤 Current Administrator
          </h3>
          <div style={{ color: '#155724' }}>
            {currentUser && (
              <>
                <p><strong>Name:</strong> {currentUser.firstName} {currentUser.lastName}</p>
                <p><strong>Email:</strong> {currentUser.email}</p>
                <p><strong>Login:</strong> {currentUser.login}</p>
                <p><strong>Role:</strong> {currentUser.role}</p>
              </>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ marginBottom: '30px' }}>
          <h3>⚙️ Admin Actions</h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px'
          }}>
            <Link 
              href="/admin/students"
              className="button"
              style={{ 
                textDecoration: 'none', 
                textAlign: 'center',
                backgroundColor: '#007bff',
                color: 'white',
                padding: '15px',
                borderRadius: '8px'
              }}
            >
              👥 Manage Students
            </Link>
            
            <Link 
              href="/admin/teachers"
              className="button"
              style={{ 
                textDecoration: 'none', 
                textAlign: 'center',
                backgroundColor: '#28a745',
                color: 'white',
                padding: '15px',
                borderRadius: '8px'
              }}
            >
              �‍🏫 Manage Teachers
            </Link>

            <Link 
              href="/admin/department-heads"
              className="button"
              style={{ 
                textDecoration: 'none', 
                textAlign: 'center',
                backgroundColor: '#ffc107',
                color: '#000',
                padding: '15px',
                borderRadius: '8px'
              }}
            >
              🏢 Manage Dept. Heads
            </Link>

            <button 
              onClick={loadDashboardData}
              className="button"
              style={{ 
                backgroundColor: '#6f42c1',
                color: 'white',
                padding: '15px',
                borderRadius: '8px'
              }}
            >
              🔄 Refresh Data
            </button>
          </div>
        </div>

        {/* Dashboard Statistics */}
        {dashboardStats && (
          <div style={{ marginBottom: '30px' }}>
            <h3>📊 System Overview</h3>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '15px',
              marginBottom: '20px'
            }}>
              <div style={{ 
                background: '#e3f2fd', 
                padding: '20px', 
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <h4 style={{ color: '#1976d2', margin: '0 0 10px 0' }}>👥 Total Users</h4>
                <p style={{ fontSize: '28px', margin: '0', color: '#1976d2', fontWeight: 'bold' }}>
                  {dashboardStats.overview.totalUsers}
                </p>
              </div>
              
              <div style={{ 
                background: '#f3e5f5', 
                padding: '20px', 
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <h4 style={{ color: '#7b1fa2', margin: '0 0 10px 0' }}>🎓 Students</h4>
                <p style={{ fontSize: '28px', margin: '0', color: '#7b1fa2', fontWeight: 'bold' }}>
                  {dashboardStats.overview.totalStudents}
                </p>
              </div>
              
              <div style={{ 
                background: '#e8f5e8', 
                padding: '20px', 
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <h4 style={{ color: '#2e7d32', margin: '0 0 10px 0' }}>👨‍🏫 Teachers</h4>
                <p style={{ fontSize: '28px', margin: '0', color: '#2e7d32', fontWeight: 'bold' }}>
                  {dashboardStats.overview.totalTeachers}
                </p>
              </div>
              
              <div style={{ 
                background: '#fff3e0', 
                padding: '20px', 
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <h4 style={{ color: '#f57c00', margin: '0 0 10px 0' }}>🏢 Dept. Heads</h4>
                <p style={{ fontSize: '28px', margin: '0', color: '#f57c00', fontWeight: 'bold' }}>
                  {dashboardStats.overview.totalDepartmentHeads}
                </p>
              </div>
            </div>

            {/* University Structure */}
            <h4>🏫 University Structure</h4>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
              gap: '10px',
              marginBottom: '20px'
            }}>
              <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '4px', textAlign: 'center' }}>
                <strong>Departments</strong><br />
                {dashboardStats.universityStructure.departments}
              </div>
              <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '4px', textAlign: 'center' }}>
                <strong>Specialties</strong><br />
                {dashboardStats.universityStructure.specialties}
              </div>
              <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '4px', textAlign: 'center' }}>
                <strong>Levels</strong><br />
                {dashboardStats.universityStructure.levels}
              </div>
              <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '4px', textAlign: 'center' }}>
                <strong>Groups</strong><br />
                {dashboardStats.universityStructure.groups}
              </div>
            </div>
          </div>
        )}

        {/* System Health */}
        {systemHealth && (
          <div style={{ marginBottom: '30px' }}>
            <h3>🔧 System Health</h3>
            <div style={{ 
              background: systemHealth.database ? '#d4edda' : '#f8d7da',
              padding: '15px', 
              borderRadius: '8px',
              border: systemHealth.database ? '1px solid #c3e6cb' : '1px solid #f5c6cb'
            }}>
              <p style={{ 
                color: systemHealth.database ? '#155724' : '#721c24',
                margin: '0'
              }}>
                <strong>Database:</strong> {systemHealth.database ? '✅ Connected' : '❌ Disconnected'}
              </p>
              {systemHealth.uptime && (
                <p style={{ color: '#155724', margin: '5px 0 0 0' }}>
                  <strong>Uptime:</strong> {systemHealth.uptime}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Recent Activity */}
        {recentActivity.length > 0 && (
          <div style={{ marginBottom: '30px' }}>
            <h3>📝 Recent Activity</h3>
            <div style={{ 
              background: '#f8f9fa', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #dee2e6'
            }}>
              {recentActivity.map((activity, index) => (
                <div key={index} style={{ 
                  padding: '8px 0', 
                  borderBottom: index < recentActivity.length - 1 ? '1px solid #dee2e6' : 'none' 
                }}>
                  <small>{JSON.stringify(activity)}</small>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Logout Button */}
        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <button 
            onClick={handleLogout}
            className="button"
            style={{ backgroundColor: '#dc3545', color: 'white', padding: '12px 24px' }}
          >
            🚪 Logout
          </button>
        </div>

        {/* Navigation */}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <Link 
            href="/" 
            style={{ color: '#007bff', textDecoration: 'none', fontSize: '14px' }}
          >
            ← Return to Home
          </Link>
        </div>
      </div>
    </div>
  );
}