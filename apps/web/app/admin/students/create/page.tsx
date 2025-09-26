'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, studentApi, universityApi } from '@/lib/api-utils';
import Link from 'next/link';

export default function CreateStudentPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    login: '',
    password: '',
    role: 'STUDENT' as const
  });
  const [options, setOptions] = useState({
    specialty_id: '',
    level_id: '',
    group_id: ''
  });
  const [departments, setDepartments] = useState<any[]>([]);
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [levels, setLevels] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
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

      // Load university structure
      await loadUniversityStructure();

    } catch (error) {
      console.error('Error checking auth and loading data:', error);
      setError('Failed to load data');
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

  const loadLevels = async (specialtyId: string) => {
    if (!specialtyId) {
      setLevels([]);
      setGroups([]);
      return;
    }

    try {
      const result = await universityApi.getLevelsBySpecialty(specialtyId);
      if (result.success && result.data) {
        setLevels(result.data);
      }
    } catch (error) {
      console.error('Error loading levels:', error);
    }
  };

  const loadGroups = async (levelId: string) => {
    if (!levelId) {
      setGroups([]);
      return;
    }

    try {
      const result = await universityApi.getGroupsByLevel(levelId);
      if (result.success && result.data) {
        setGroups(result.data);
      }
    } catch (error) {
      console.error('Error loading groups:', error);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleOptionChange = (field: string, value: string) => {
    setOptions(prev => ({ ...prev, [field]: value }));
    
    // Load dependent data
    if (field === 'specialty_id') {
      loadLevels(value);
      setOptions(prev => ({ ...prev, level_id: '', group_id: '' }));
    } else if (field === 'level_id') {
      loadGroups(value);
      setOptions(prev => ({ ...prev, group_id: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Filter out empty options
      const cleanOptions = Object.fromEntries(
        Object.entries(options).filter(([_, value]) => value !== '')
      );

      const result = await studentApi.create(formData, cleanOptions);
      
      if (result.success) {
        alert('Student created successfully!');
        router.push('/admin/students');
      } else {
        setError(result.error || 'Failed to create student');
      }
    } catch (error) {
      console.error('Error creating student:', error);
      setError('Failed to create student');
    } finally {
      setLoading(false);
    }
  };

  if (error && error.includes('Access denied')) {
    return (
      <div className="container">
        <div className="welcome">
          <h1>❌ Access Denied</h1>
          <p style={{ color: '#dc3545' }}>{error}</p>
          <Link href="/admin/login" className="button">Go to Login</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="welcome">
        <h1 className="title">➕ Create New Student</h1>
        
        {/* Navigation */}
        <div style={{ marginBottom: '20px' }}>
          <Link href="/admin/students" style={{ color: '#007bff', textDecoration: 'none' }}>
            ← Back to Students
          </Link>
        </div>

        <form onSubmit={handleSubmit} className="form" style={{ maxWidth: '600px', margin: '0 auto' }}>
          {/* Basic Information */}
          <h3>👤 Basic Information</h3>
          
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              First Name *
            </label>
            <input
              type="text"
              value={formData.firstName}
              onChange={(e) => handleInputChange('firstName', e.target.value)}
              required
              className="input"
              placeholder="Student's first name"
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Last Name *
            </label>
            <input
              type="text"
              value={formData.lastName}
              onChange={(e) => handleInputChange('lastName', e.target.value)}
              required
              className="input"
              placeholder="Student's last name"
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Email *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              required
              className="input"
              placeholder="student@university.edu"
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Login Username *
            </label>
            <input
              type="text"
              value={formData.login}
              onChange={(e) => handleInputChange('login', e.target.value)}
              required
              className="input"
              placeholder="student_username"
            />
          </div>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Password *
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              required
              className="input"
              placeholder="Secure password"
            />
          </div>

          {/* Academic Information */}
          <h3 style={{ marginTop: '30px' }}>🎓 Academic Assignment (Optional)</h3>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Specialty
            </label>
            <select
              value={options.specialty_id}
              onChange={(e) => handleOptionChange('specialty_id', e.target.value)}
              className="input"
            >
              <option value="">Select Specialty</option>
              {specialties.map(spec => (
                <option key={spec.id} value={spec.id}>
                  {spec.name}
                </option>
              ))}
            </select>
          </div>

          {levels.length > 0 && (
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Level
              </label>
              <select
                value={options.level_id}
                onChange={(e) => handleOptionChange('level_id', e.target.value)}
                className="input"
              >
                <option value="">Select Level</option>
                {levels.map(level => (
                  <option key={level.id} value={level.id}>
                    {level.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {groups.length > 0 && (
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Group
              </label>
              <select
                value={options.group_id}
                onChange={(e) => handleOptionChange('group_id', e.target.value)}
                className="input"
              >
                <option value="">Select Group</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {error && (
            <div style={{ 
              color: '#dc3545', 
              background: '#f8d7da', 
              padding: '10px', 
              borderRadius: '4px', 
              marginBottom: '15px',
              fontSize: '14px'
            }}>
              {error}
            </div>
          )}

          <div style={{ 
            display: 'flex', 
            gap: '10px', 
            justifyContent: 'center',
            marginTop: '30px'
          }}>
            <button 
              type="submit" 
              disabled={loading}
              className="button"
              style={{ backgroundColor: '#28a745' }}
            >
              {loading ? 'Creating...' : '✅ Create Student'}
            </button>
            
            <Link
              href="/admin/students"
              className="button"
              style={{ 
                backgroundColor: '#6c757d',
                textDecoration: 'none',
                color: 'white'
              }}
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}