'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, studentApi, universityApi, User } from '@/lib/api-utils';
import Link from 'next/link';

export default function AdminStudentsPage() {
  const [students, setStudents] = useState<User[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    department_id: '',
    specialty_id: '',
    academic_year: ''
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
        loadStudents(),
        loadUniversityStructure()
      ]);

    } catch (error) {
      console.error('Error checking auth and loading data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    try {
      const result = await studentApi.getAll(filters);
      if (result.success && result.data) {
        setStudents(result.data);
      } else {
        console.error('Failed to load students:', result.error);
      }
    } catch (error) {
      console.error('Error loading students:', error);
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

  const handleDeleteStudent = async (studentId: string) => {
    if (!confirm('Are you sure you want to delete this student?')) {
      return;
    }

    try {
      const result = await studentApi.delete(studentId);
      if (result.success) {
        setStudents(students.filter(s => s.id !== studentId));
        alert('Student deleted successfully!');
      } else {
        alert(`Failed to delete student: ${result.error}`);
      }
    } catch (error) {
      console.error('Error deleting student:', error);
      alert('Error deleting student');
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    loadStudents();
  };

  if (loading) {
    return (
      <div className="container">
        <div className="welcome">
          <h1>Loading Students...</h1>
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
        <h1 className="title">👥 Students Management</h1>
        
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
                Academic Year:
              </label>
              <input
                type="text"
                value={filters.academic_year}
                onChange={(e) => handleFilterChange('academic_year', e.target.value)}
                placeholder="e.g., 2024"
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ddd'
                }}
              />
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
            href="/admin/students/create"
            className="button"
            style={{ 
              textDecoration: 'none',
              backgroundColor: '#28a745',
              color: 'white',
              padding: '10px 20px',
              borderRadius: '4px'
            }}
          >
            ➕ Create New Student
          </Link>
        </div>

        {/* Students List */}
        <div style={{ marginBottom: '20px' }}>
          <h3>📊 Students ({students.length})</h3>
          
          {students.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px', 
              background: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #dee2e6'
            }}>
              <p>No students found.</p>
              <Link href="/admin/students/create" className="button">
                Create First Student
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
                <thead style={{ backgroundColor: '#007bff', color: 'white' }}>
                  <tr>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Email</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Login</th>
                    <th style={{ padding: '12px', textAlign: 'left' }}>Created</th>
                    <th style={{ padding: '12px', textAlign: 'center' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student, index) => (
                    <tr 
                      key={student.id}
                      style={{ 
                        backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white',
                        borderBottom: '1px solid #dee2e6'
                      }}
                    >
                      <td style={{ padding: '12px' }}>
                        {student.firstName} {student.lastName}
                      </td>
                      <td style={{ padding: '12px' }}>{student.email}</td>
                      <td style={{ padding: '12px' }}>{student.login}</td>
                      <td style={{ padding: '12px' }}>
                        {new Date(student.createdAt).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <Link
                          href={`/admin/students/${student.id}/edit`}
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
                          onClick={() => handleDeleteStudent(student.id)}
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