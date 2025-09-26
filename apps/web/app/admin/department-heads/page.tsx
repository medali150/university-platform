'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, departmentHeadApi, universityApi } from '@/lib/api-utils';
import Link from 'next/link';

export default function AdminDepartmentHeadsPage() {
  const [departmentHeads, setDepartmentHeads] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    department_id: ''
  });
  const router = useRouter();

  useEffect(() => {
    checkAuthAndLoadData();
  }, []);

  const checkAuthAndLoadData = async () => {
    try {
      // Check authentication
      if (!authApi.isAuthenticated()) {
        router.push('/admin/login');
        return;
      }

      const userResult = await authApi.me();
      if (!userResult.success || userResult.data?.role !== 'ADMIN') {
        setError('Access denied. Admin privileges required.');
        return;
      }

      // Load data
      await Promise.all([
        loadDepartmentHeads(),
        loadDepartments()
      ]);

    } catch (error) {
      console.error('Error checking auth and loading data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadDepartmentHeads = async () => {
    try {
      const result = await departmentHeadApi.getAll(filters);
      if (result.success && result.data) {
        setDepartmentHeads(result.data);
      } else {
        console.error('Failed to load department heads:', result.error);
      }
    } catch (error) {
      console.error('Error loading department heads:', error);
    }
  };

  const loadDepartments = async () => {
    try {
      const result = await universityApi.getDepartments();
      if (result.success && result.data) {
        setDepartments(result.data);
      }
    } catch (error) {
      console.error('Error loading departments:', error);
    }
  };

  const handleDeleteDepartmentHead = async (deptHeadId: string) => {
    if (!confirm('Are you sure you want to delete this department head?')) {
      return;
    }

    try {
      const result = await departmentHeadApi.delete(deptHeadId);
      if (result.success) {
        setDepartmentHeads(departmentHeads.filter(dh => dh.id !== deptHeadId));
        alert('Department head deleted successfully!');
      } else {
        alert(`Failed to delete department head: ${result.error}`);
      }
    } catch (error) {
      console.error('Error deleting department head:', error);
      alert('Error deleting department head');
    }
  };

  const handleDemoteToTeacher = async (deptHeadId: string) => {
    if (!confirm('Are you sure you want to demote this department head to teacher?')) {
      return;
    }

    try {
      const result = await departmentHeadApi.demoteToTeacher(deptHeadId);
      if (result.success) {
        setDepartmentHeads(departmentHeads.filter(dh => dh.id !== deptHeadId));
        alert('Department head demoted to teacher successfully!');
      } else {
        alert(`Failed to demote department head: ${result.error}`);
      }
    } catch (error) {
      console.error('Error demoting department head:', error);
      alert('Error demoting department head');
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    loadDepartmentHeads();
  };

  if (loading) {
    return (
      <div className="container">
        <div className="welcome">
          <h1>Loading Department Heads...</h1>
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
          <Link href="/admin/dashboard" className="button">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="welcome">
        <h1 className="title">🏢 Department Heads Management</h1>
        
        {/* Navigation */}
        <div style={{ marginBottom: '20px' }}>
          <Link href="/admin/dashboard" style={{ color: '#007bff', textDecoration: 'none' }}>
            ← Back to Dashboard
          </Link>
        </div>

        {/* Filters */}
        <div style={{ 
          background: '#f8f9fa', 
          padding: '20px', 
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <h3>🔍 Filters</h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px',
            marginBottom: '15px'
          }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Department:
              </label>
              <select
                value={filters.department_id}
                onChange={(e) => handleFilterChange('department_id', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ddd'
                }}
              >
                <option value="">All Departments</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button 
            onClick={applyFilters}
            className="button"
            style={{ backgroundColor: '#007bff' }}
          >
            Apply Filters
          </button>
        </div>

        {/* Actions */}
        <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <Link
            href="/admin/department-heads/create"
            className="button"
            style={{ 
              textDecoration: 'none',
              backgroundColor: '#28a745',
              color: 'white',
              padding: '10px 20px',
              borderRadius: '4px'
            }}
          >
            ➕ Create New Department Head
          </Link>
          
          <Link
            href="/admin/department-heads/assign"
            className="button"
            style={{ 
              textDecoration: 'none',
              backgroundColor: '#ffc107',
              color: '#000',
              padding: '10px 20px',
              borderRadius: '4px'
            }}
          >
            🔄 Assign Teacher as Head
          </Link>
        </div>

        {/* Department Heads List */}
        <div style={{ marginBottom: '20px' }}>
          <h3>📊 Department Heads ({departmentHeads.length})</h3>
          
          {departmentHeads.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px', 
              background: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #dee2e6'
            }}>
              <p>No department heads found.</p>
              <Link href="/admin/department-heads/create" className="button">
                Create First Department Head
              </Link>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ 
                width: '100%', 
                borderCollapse: 'collapse',
                background: 'white',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                <thead style={{ backgroundColor: '#ffc107', color: '#000' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Email</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Login</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Department</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Appointed</th>
                    <th style={{ padding: '12px', textAlign: 'center' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {departmentHeads.map((head, index) => (
                    <tr 
                      key={head.id}
                      style={{ 
                        backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white',
                        borderBottom: '1px solid #dee2e6'
                      }}
                    >
                      <td style={{ padding: '12px' }}>
                        {head.user?.firstName} {head.user?.lastName}
                      </td>
                      <td style={{ padding: '12px' }}>{head.user?.email}</td>
                      <td style={{ padding: '12px' }}>{head.user?.login}</td>
                      <td style={{ padding: '12px' }}>
                        {head.department?.name || 'N/A'}
                      </td>
                      <td style={{ padding: '12px' }}>
                        {head.appointmentDate ? 
                          new Date(head.appointmentDate).toLocaleDateString() : 
                          'N/A'
                        }
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <Link
                          href={`/admin/department-heads/${head.id}/edit`}
                          style={{
                            backgroundColor: '#007bff',
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            textDecoration: 'none',
                            fontSize: '12px',
                            marginRight: '5px'
                          }}
                        >
                          ✏️ Edit
                        </Link>
                        <button
                          onClick={() => handleDemoteToTeacher(head.id)}
                          style={{
                            backgroundColor: '#6f42c1',
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            border: 'none',
                            fontSize: '12px',
                            cursor: 'pointer',
                            marginRight: '5px'
                          }}
                          title="Demote to Teacher"
                        >
                          👨‍🏫 Demote
                        </button>
                        <button
                          onClick={() => handleDeleteDepartmentHead(head.id)}
                          style={{
                            backgroundColor: '#dc3545',
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            border: 'none',
                            fontSize: '12px',
                            cursor: 'pointer'
                          }}
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}