'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, teacherApi, universityApi, User } from '@/lib/api-utils';
import Link from 'next/link';

export default function AdminTeachersPage() {
  const [teachers, setTeachers] = useState<User[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    department_id: '',
    specialty_id: '',
    academic_title: ''
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
        loadTeachers(),
        loadUniversityStructure()
      ]);

    } catch (error) {
      console.error('Error checking auth and loading data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadTeachers = async () => {
    try {
      const result = await teacherApi.getAll(filters);
      if (result.success && result.data) {
        setTeachers(result.data);
      } else {
        console.error('Failed to load teachers:', result.error);
      }
    } catch (error) {
      console.error('Error loading teachers:', error);
    }
  };

  const loadUniversityStructure = async () => {
    try {
      const [deptsResult, specsResult] = await Promise.all([
        universityApi.getDepartments(),
        universityApi.getSpecialties()
      ]);

      if (deptsResult.success && deptsResult.data) {
        setDepartments(deptsResult.data);
      }

      if (specsResult.success && specsResult.data) {
        setSpecialties(specsResult.data);
      }
    } catch (error) {
      console.error('Error loading university structure:', error);
    }
  };

  const handleDeleteTeacher = async (teacherId: string) => {
    if (!confirm('Are you sure you want to delete this teacher?')) {
      return;
    }

    try {
      const result = await teacherApi.delete(teacherId);
      if (result.success) {
        setTeachers(teachers.filter(t => t.id !== teacherId));
        alert('Teacher deleted successfully!');
      } else {
        alert(`Failed to delete teacher: ${result.error}`);
      }
    } catch (error) {
      console.error('Error deleting teacher:', error);
      alert('Error deleting teacher');
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    loadTeachers();
  };

  if (loading) {
    return (
      <div className="container">
        <div className="welcome">
          <h1>Loading Teachers...</h1>
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
        <h1 className="title">👨‍🏫 Teachers Management</h1>
        
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

            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Specialty:
              </label>
              <select
                value={filters.specialty_id}
                onChange={(e) => handleFilterChange('specialty_id', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ddd'
                }}
              >
                <option value="">All Specialties</option>
                {specialties.map(spec => (
                  <option key={spec.id} value={spec.id}>
                    {spec.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Academic Title:
              </label>
              <select
                value={filters.academic_title}
                onChange={(e) => handleFilterChange('academic_title', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ddd'
                }}
              >
                <option value="">All Titles</option>
                <option value="Professor">Professor</option>
                <option value="Associate Professor">Associate Professor</option>
                <option value="Assistant Professor">Assistant Professor</option>
                <option value="Lecturer">Lecturer</option>
                <option value="Teaching Assistant">Teaching Assistant</option>
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
        <div style={{ marginBottom: '20px' }}>
          <Link
            href="/admin/teachers/create"
            className="button"
            style={{ 
              textDecoration: 'none',
              backgroundColor: '#28a745',
              color: 'white',
              padding: '10px 20px',
              borderRadius: '4px'
            }}
          >
            ➕ Create New Teacher
          </Link>
        </div>

        {/* Teachers List */}
        <div style={{ marginBottom: '20px' }}>
          <h3>📊 Teachers ({teachers.length})</h3>
          
          {teachers.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px', 
              background: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #dee2e6'
            }}>
              <p>No teachers found.</p>
              <Link href="/admin/teachers/create" className="button">
                Create First Teacher
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
                <thead style={{ backgroundColor: '#28a745', color: 'white' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Email</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Login</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Created</th>
                    <th style={{ padding: '12px', textAlign: 'center' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {teachers.map((teacher, index) => (
                    <tr 
                      key={teacher.id}
                      style={{ 
                        backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white',
                        borderBottom: '1px solid #dee2e6'
                      }}
                    >
                      <td style={{ padding: '12px' }}>
                        {teacher.firstName} {teacher.lastName}
                      </td>
                      <td style={{ padding: '12px' }}>{teacher.email}</td>
                      <td style={{ padding: '12px' }}>{teacher.login}</td>
                      <td style={{ padding: '12px' }}>
                        {new Date(teacher.createdAt).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <Link
                          href={`/admin/teachers/${teacher.id}/edit`}
                          style={{
                            backgroundColor: '#ffc107',
                            color: '#000',
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
                          onClick={() => handleDeleteTeacher(teacher.id)}
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