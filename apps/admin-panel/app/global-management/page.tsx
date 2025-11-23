'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { globalCrudApi } from '@/lib/admin-global-api';

export default function GlobalManagementPage() {
  const { admin, loading: authLoading } = useAdminAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('departments');

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-red-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading Admin Panel...</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'departments', name: 'Departments', icon: '🏢', color: 'blue' },
    { id: 'specialties', name: 'Specialties', icon: '🎯', color: 'purple' },
    { id: 'levels', name: 'Levels', icon: '📊', color: 'indigo' },
    { id: 'teachers', name: 'Teachers', icon: '👨‍🏫', color: 'orange' },
    { id: 'students', name: 'Students', icon: '🎓', color: 'green' },
    { id: 'rooms', name: 'Classrooms', icon: '🚪', color: 'cyan' },
    { id: 'subjects', name: 'Subjects', icon: '📚', color: 'red' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Modern Header */}
      <div className="bg-white shadow-lg border-b-4 border-red-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center text-2xl shadow-lg">
                🌐
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
                  Global Management
                </h1>
                <p className="mt-1 text-sm text-gray-600">
                  Manage all university resources and entities
                </p>
              </div>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-6 py-3 bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 rounded-xl hover:from-gray-200 hover:to-gray-300 transition-all font-semibold shadow-md hover:shadow-lg flex items-center gap-2"
            >
              <span>←</span> Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Enhanced Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex flex-wrap px-4" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    ${activeTab === tab.id
                      ? 'border-red-500 text-red-600 bg-red-50'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }
                    flex-1 min-w-[140px] py-4 px-3 border-b-3 font-semibold text-sm transition-all flex items-center justify-center gap-2
                  `}
                >
                  <span className="text-xl">{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="p-6 bg-gradient-to-br from-white to-gray-50 min-h-[600px]">
            {activeTab === 'departments' && <DepartmentsManager />}
            {activeTab === 'specialties' && <SpecialtiesManager />}
            {activeTab === 'levels' && <LevelsManager />}
            {activeTab === 'teachers' && <TeachersManager />}
            {activeTab === 'students' && <StudentsManager />}
            {activeTab === 'rooms' && <RoomsManager />}
            {activeTab === 'subjects' && <SubjectsManager />}
          </div>
        </div>
      </div>
    </div>
  );
}

// Enhanced Departments Manager
function DepartmentsManager() {
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ nom: '' });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    try {
      setLoading(true);
      const response = await globalCrudApi.departments.list({ limit: 100 });
      setDepartments(response.data || []);
    } catch (error: any) {
      console.error('Failed to load departments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.nom.trim()) return;

    try {
      if (editingId) {
        await globalCrudApi.departments.update(editingId, formData);
      } else {
        await globalCrudApi.departments.create(formData);
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({ nom: '' });
      loadDepartments();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Operation failed'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this department?')) return;
    
    try {
      await globalCrudApi.departments.delete(id, false);
      loadDepartments();
    } catch (error: any) {
      if (error.message.includes('force') || error.message.includes('specialties') || error.message.includes('teachers')) {
        if (confirm('This department has related data. Force delete?')) {
          await globalCrudApi.departments.delete(id, true);
          loadDepartments();
        }
      } else {
        alert('Error: ' + (error.message || 'Delete failed'));
      }
    }
  };

  const filteredDepartments = departments.filter(dept =>
    dept.nom.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with Search */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span>🏢</span> Departments Management
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            {filteredDepartments.length} department{filteredDepartments.length !== 1 ? 's' : ''} total
          </p>
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <input
            type="text"
            placeholder="🔍 Search departments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 md:w-64 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-xl hover:from-red-700 hover:to-orange-700 font-semibold shadow-md hover:shadow-lg transition-all whitespace-nowrap"
          >
            {showForm ? '✕ Cancel' : '+ Add Department'}
          </button>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 border-2 border-blue-300 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-blue-900 flex items-center gap-2">
            <span>{editingId ? '✏️' : '➕'}</span>
            {editingId ? 'Edit Department' : 'Create New Department'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Department Name *
              </label>
              <input
                type="text"
                value={formData.nom}
                onChange={(e) => setFormData({ nom: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Computer Science, Mathematics..."
                required
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 font-semibold shadow-md"
              >
                {editingId ? '💾 Update' : '➕ Create'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingId(null);
                  setFormData({ nom: '' });
                }}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 font-semibold"
              >
                ✕ Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredDepartments.map((dept) => (
          <div
            key={dept.id}
            className="bg-white border-2 border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-blue-300 transition-all group"
          >
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-bold text-lg text-gray-900 group-hover:text-blue-600 transition-colors">
                {dept.nom}
              </h3>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setEditingId(dept.id);
                    setFormData({ nom: dept.nom });
                    setShowForm(true);
                  }}
                  className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                  title="Edit"
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleDelete(dept.id)}
                  className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <span className="font-semibold">🎯 Specialties:</span>
                <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-semibold">
                  {dept.specialites?.length || 0}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">👨‍🏫 Teachers:</span>
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-semibold">
                  {dept.enseignants?.length || 0}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredDepartments.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">🏢</div>
          <p className="text-gray-600 font-medium">No departments found</p>
          <p className="text-sm text-gray-500 mt-1">
            {searchTerm ? 'Try adjusting your search' : 'Create your first department to get started'}
          </p>
        </div>
      )}
    </div>
  );
}

// Enhanced Specialties Manager
function SpecialtiesManager() {
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({ nom: '', id_departement: '' });
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDept, setFilterDept] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [specialtiesRes, deptsRes] = await Promise.all([
        globalCrudApi.specialties.list({ limit: 100 }),
        globalCrudApi.departments.list({ limit: 100 }),
      ]);
      setSpecialties(specialtiesRes.data || []);
      setDepartments(deptsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.nom.trim() || !formData.id_departement) return;

    try {
      if (editingId) {
        await globalCrudApi.specialties.update(editingId, formData);
      } else {
        await globalCrudApi.specialties.create(formData);
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({ nom: '', id_departement: '' });
      loadData();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Operation failed'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this specialty?')) return;
    
    try {
      await globalCrudApi.specialties.delete(id, false);
      loadData();
    } catch (error: any) {
      if (error.message.includes('force') || error.message.includes('students') || error.message.includes('subjects')) {
        if (confirm('This specialty has related data. Force delete?')) {
          await globalCrudApi.specialties.delete(id, true);
          loadData();
        }
      } else {
        alert('Error: ' + (error.message || 'Delete failed'));
      }
    }
  };

  const filteredSpecialties = specialties.filter(spec => {
    const matchesSearch = spec.nom.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDept = !filterDept || spec.id_departement === filterDept;
    return matchesSearch && matchesDept;
  });

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-600 border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with Search and Filters */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span>🎯</span> Specialties Management
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {filteredSpecialties.length} specialt{filteredSpecialties.length !== 1 ? 'ies' : 'y'} total
            </p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 font-semibold shadow-md hover:shadow-lg transition-all"
          >
            {showForm ? '✕ Cancel' : '+ Add Specialty'}
          </button>
        </div>
        <div className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            placeholder="🔍 Search specialties..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <select
            value={filterDept}
            onChange={(e) => setFilterDept(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">All Departments</option>
            {departments.map(dept => (
              <option key={dept.id} value={dept.id}>{dept.nom}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-gradient-to-br from-purple-50 to-pink-100 border-2 border-purple-300 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-purple-900 flex items-center gap-2">
            <span>{editingId ? '✏️' : '➕'}</span>
            {editingId ? 'Edit Specialty' : 'Create New Specialty'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Specialty Name *
                </label>
                <input
                  type="text"
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="e.g., Software Engineering"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Department *
                </label>
                <select
                  value={formData.id_departement}
                  onChange={(e) => setFormData({ ...formData, id_departement: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  required
                >
                  <option value="">Select Department</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.nom}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 font-semibold shadow-md"
              >
                {editingId ? '💾 Update' : '➕ Create'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingId(null);
                  setFormData({ nom: '', id_departement: '' });
                }}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 font-semibold"
              >
                ✕ Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredSpecialties.map((spec) => (
          <div
            key={spec.id}
            className="bg-white border-2 border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-purple-300 transition-all group"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="font-bold text-lg text-gray-900 group-hover:text-purple-600 transition-colors">
                  {spec.nom}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  🏢 {spec.departement?.nom || 'N/A'}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setEditingId(spec.id);
                    setFormData({ nom: spec.nom, id_departement: spec.id_departement });
                    setShowForm(true);
                  }}
                  className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                  title="Edit"
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleDelete(spec.id)}
                  className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="font-semibold">📊 Levels:</span>
              <span className="bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full text-xs font-semibold">
                {spec.niveaux?.length || 0}
              </span>
            </div>
          </div>
        ))}
      </div>

      {filteredSpecialties.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">🎯</div>
          <p className="text-gray-600 font-medium">No specialties found</p>
          <p className="text-sm text-gray-500 mt-1">
            {searchTerm || filterDept ? 'Try adjusting your filters' : 'Create your first specialty to get started'}
          </p>
        </div>
      )}
    </div>
  );
}

// Levels Manager with full CRUD
function LevelsManager() {
  const [levels, setLevels] = useState<any[]>([]);
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDept, setFilterDept] = useState('');
  const [formData, setFormData] = useState({
    nom: '',
    id_specialite: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [levelsRes, specsRes, deptsRes] = await Promise.all([
        globalCrudApi.levels.list({ limit: 100 }),
        globalCrudApi.specialties.list({ limit: 100 }),
        globalCrudApi.departments.list({ limit: 100 })
      ]);
      setLevels(levelsRes.data || []);
      setSpecialties(specsRes.data || []);
      setDepartments(deptsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await globalCrudApi.levels.update(editingId, formData);
      } else {
        await globalCrudApi.levels.create(formData);
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({ nom: '', id_specialite: '' });
      loadData();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Operation failed'));
    }
  };

  const handleEdit = (level: any) => {
    setFormData({
      nom: level.nom,
      id_specialite: level.id_specialite || ''
    });
    setEditingId(level.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this level? This will also affect related groups and students.')) return;
    try {
      await globalCrudApi.levels.delete(id, false);
      loadData();
    } catch (error: any) {
      if (error.message.includes('force') || error.message.includes('groups') || error.message.includes('students')) {
        if (confirm('This level has related data (groups/students). Force delete?')) {
          await globalCrudApi.levels.delete(id, true);
          loadData();
        }
      } else {
        alert('Error: ' + (error.message || 'Delete failed'));
      }
    }
  };

  const filteredLevels = levels.filter(l => {
    const matchesSearch = l.nom.toLowerCase().includes(searchTerm.toLowerCase());
    const specialty = specialties.find(s => s.id === l.id_specialite);
    const matchesDept = !filterDept || specialty?.id_departement === filterDept;
    return matchesSearch && matchesDept;
  });

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-600 border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span>📊</span> Levels Management
            </h2>
            <p className="text-sm text-gray-600 mt-1">{filteredLevels.length} level{filteredLevels.length !== 1 ? 's' : ''}</p>
          </div>
          <button
            onClick={() => {
              setShowForm(!showForm);
              if (showForm) {
                setEditingId(null);
                setFormData({ nom: '', id_specialite: '' });
              }
            }}
            className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 font-semibold shadow-md"
          >
            {showForm ? '✕ Cancel' : '+ Add Level'}
          </button>
        </div>
        
        <div className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            placeholder="🔍 Search levels..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
          />
          <select
            value={filterDept}
            onChange={(e) => setFilterDept(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Departments</option>
            {departments.map(d => (
              <option key={d.id} value={d.id}>{d.nom}</option>
            ))}
          </select>
        </div>
      </div>

      {showForm && (
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6 border-2 border-indigo-200 shadow-lg">
          <h3 className="text-xl font-bold text-indigo-900 mb-4 flex items-center gap-2">
            {editingId ? '✏️ Edit Level' : '➕ Add New Level'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Level Name *</label>
                <input
                  type="text"
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g., 1ère année, 2ème année"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Specialty *</label>
                <select
                  value={formData.id_specialite}
                  onChange={(e) => setFormData({ ...formData, id_specialite: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
                  required
                >
                  <option value="">Select Specialty</option>
                  {specialties.map(s => {
                    const dept = departments.find(d => d.id === s.id_departement);
                    return (
                      <option key={s.id} value={s.id}>
                        {s.nom} ({dept?.nom || 'Unknown Dept'})
                      </option>
                    );
                  })}
                </select>
              </div>
            </div>
            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingId(null);
                  setFormData({ nom: '', id_specialite: '' });
                }}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 font-semibold shadow-md"
              >
                {editingId ? 'Update Level' : 'Create Level'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid gap-4">
        {filteredLevels.map((level) => {
          // Direct relationship: level has one specialty
          const specialty = specialties.find(s => s.id === level.id_specialite);
          const department = departments.find(d => d.id === specialty?.id_departement);
          
          return (
            <div key={level.id} className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all border-l-4 border-indigo-500 p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-md">
                      {level.nom.charAt(0)}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{level.nom}</h3>
                      <p className="text-sm text-gray-500">Level ID: {level.id}</p>
                    </div>
                  </div>
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-700">🎯 Specialty:</span>
                      <span className="text-gray-600">{specialty?.nom || 'Unknown'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-700">🏢 Department:</span>
                      <span className="text-gray-600">{department?.nom || 'Unknown'}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(level)}
                    className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 font-semibold shadow-md"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    onClick={() => handleDelete(level.id)}
                    className="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg hover:from-red-600 hover:to-pink-600 font-semibold shadow-md"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredLevels.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-gray-600 font-medium">No levels found</p>
          <p className="text-sm text-gray-500 mt-1">
            {searchTerm || filterDept ? 'Try adjusting your filters' : 'Create your first level to get started'}
          </p>
        </div>
      )}
    </div>
  );
}

// Teachers Manager with full CRUD
function TeachersManager() {
  const [teachers, setTeachers] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    id_departement: '',
    password: '',
    image_url: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [teachersRes, deptsRes] = await Promise.all([
        globalCrudApi.teachers.list({ limit: 100, department_id: filterDepartment || undefined }),
        globalCrudApi.departments.list({ limit: 100 }),
      ]);
      setTeachers(teachersRes.data || []);
      setDepartments(deptsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Reload when filter changes
  useEffect(() => {
    if (!loading) loadData();
  }, [filterDepartment]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.nom.trim() || !formData.email || !formData.id_departement) return;

    try {
      await globalCrudApi.teachers.create(formData);
      setShowForm(false);
      setFormData({ nom: '', prenom: '', email: '', id_departement: '', password: '', image_url: '' });
      loadData();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Operation failed'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this teacher?')) return;
    try {
      await globalCrudApi.teachers.delete(id, false);
      loadData();
    } catch (error: any) {
      if (confirm('This teacher has related data. Force delete?')) {
        await globalCrudApi.teachers.delete(id, true);
        loadData();
      }
    }
  };

  const filteredTeachers = teachers.filter(t =>
    `${t.nom} ${t.prenom} ${t.email}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-600 border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span>👨‍🏫</span> Teachers Management
          </h2>
          <p className="text-sm text-gray-600 mt-1">{filteredTeachers.length} teacher{filteredTeachers.length !== 1 ? 's' : ''}</p>
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <select
            value={filterDepartment}
            onChange={(e) => setFilterDepartment(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
          >
            <option value="">🏢 All Departments</option>
            {departments.map(dept => (
              <option key={dept.id} value={dept.id}>{dept.nom}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="🔍 Search teachers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 md:w-64 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
          />
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl hover:from-orange-700 hover:to-red-700 font-semibold shadow-md"
          >
            {showForm ? '✕ Cancel' : '+ Add Teacher'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-gradient-to-br from-orange-50 to-red-100 border-2 border-orange-300 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-orange-900">➕ Create New Teacher</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Last Name *"
                value={formData.nom}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
                required
              />
              <input
                type="text"
                placeholder="First Name *"
                value={formData.prenom}
                onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
                required
              />
              <input
                type="email"
                placeholder="Email *"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
                required
              />
              <input
                type="password"
                placeholder="Password *"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
                required
              />
              <select
                value={formData.id_departement}
                onChange={(e) => setFormData({ ...formData, id_departement: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
                required
              >
                <option value="">Select Department *</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>{dept.nom}</option>
                ))}
              </select>
              <input
                type="url"
                placeholder="Image URL (optional)"
                value={formData.image_url}
                onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500"
              />
            </div>
            <button type="submit" className="px-6 py-3 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl font-semibold shadow-md">
              ➕ Create Teacher
            </button>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTeachers.map((teacher) => (
          <div key={teacher.id} className="bg-white border-2 border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-orange-300 transition-all">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="font-bold text-lg text-gray-900">{teacher.prenom} {teacher.nom}</h3>
                <p className="text-sm text-gray-600">{teacher.email}</p>
                <p className="text-xs text-gray-500 mt-1">🏢 {teacher.departement?.nom || 'N/A'}</p>
              </div>
              <button
                onClick={() => handleDelete(teacher.id)}
                className="p-2 text-red-600 hover:bg-red-100 rounded-lg"
                title="Delete"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredTeachers.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">👨‍🏫</div>
          <p className="text-gray-600 font-medium">No teachers found</p>
        </div>
      )}
    </div>
  );
}

// Students Manager with full CRUD
function StudentsManager() {
  const [students, setStudents] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [levels, setLevels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  const [filterSpecialty, setFilterSpecialty] = useState('');
  const [filterLevel, setFilterLevel] = useState('');
  const [filterGroup, setFilterGroup] = useState('');
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    cne: '',
    id_groupe: '',
    id_specialite: '',
    password: ''
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [studentsRes, deptsRes, groupsRes, specsRes] = await Promise.all([
        globalCrudApi.students.list({ limit: 100 }),
        globalCrudApi.departments.list({ limit: 100 }),
        globalCrudApi.groups.list(),
        globalCrudApi.specialties.list({ limit: 100 }),
      ]);
      setStudents(studentsRes.data || []);
      setDepartments(deptsRes.data || []);
      setGroups(groupsRes.data || []);
      setSpecialties(specsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load students with filters
  const loadStudents = async () => {
    try {
      const params: any = { limit: 100 };
      if (filterDepartment) params.department_id = filterDepartment;
      if (filterSpecialty) params.specialty_id = filterSpecialty;
      if (filterLevel) params.level_id = filterLevel;
      if (filterGroup) params.group_id = filterGroup;
      
      const studentsRes = await globalCrudApi.students.list(params);
      setStudents(studentsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load students:', error);
    }
  };

  // Reload students when filters change
  useEffect(() => {
    if (!loading) loadStudents();
  }, [filterDepartment, filterSpecialty, filterLevel, filterGroup]);

  const loadData = loadInitialData; // Alias for compatibility

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await globalCrudApi.students.create(formData);
      setShowForm(false);
      setFormData({ nom: '', prenom: '', email: '', cne: '', id_groupe: '', id_specialite: '', password: '' });
      loadData();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Operation failed'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this student?')) return;
    try {
      await globalCrudApi.students.delete(id, false);
      loadData();
    } catch (error: any) {
      if (confirm('Force delete?')) {
        await globalCrudApi.students.delete(id, true);
        loadData();
      }
    }
  };

  const filteredStudents = students.filter(s =>
    `${s.nom} ${s.prenom} ${s.email} ${s.cne}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-4 border-green-600 border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span>🎓</span> Students Management
          </h2>
          <p className="text-sm text-gray-600 mt-1">{filteredStudents.length} student{filteredStudents.length !== 1 ? 's' : ''}</p>
        </div>
        <div className="flex gap-2 w-full md:w-auto flex-wrap">
          <select
            value={filterDepartment}
            onChange={(e) => {
              setFilterDepartment(e.target.value);
              setFilterSpecialty('');
              setFilterLevel('');
              setFilterGroup('');
            }}
            className="px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-sm"
          >
            <option value="">🏢 All Departments</option>
            {departments.map(dept => (
              <option key={dept.id} value={dept.id}>{dept.nom}</option>
            ))}
          </select>
          <select
            value={filterSpecialty}
            onChange={(e) => {
              setFilterSpecialty(e.target.value);
              setFilterLevel('');
              setFilterGroup('');
            }}
            className="px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-sm"
          >
            <option value="">📚 All Specialties</option>
            {specialties.filter(s => !filterDepartment || s.id_departement === filterDepartment).map(spec => (
              <option key={spec.id} value={spec.id}>{spec.nom}</option>
            ))}
          </select>
          <select
            value={filterGroup}
            onChange={(e) => setFilterGroup(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-sm"
          >
            <option value="">👥 All Groups</option>
            {groups.filter(g => !filterSpecialty || g.niveau?.id_specialite === filterSpecialty).map(group => (
              <option key={group.id} value={group.id}>{group.nom}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="🔍 Search students..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 md:w-48 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
          />
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-xl hover:from-green-700 hover:to-teal-700 font-semibold shadow-md"
          >
            {showForm ? '✕ Cancel' : '+ Add Student'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-gradient-to-br from-green-50 to-teal-100 border-2 border-green-300 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-green-900">➕ Create New Student</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Last Name *"
                value={formData.nom}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
                required
              />
              <input
                type="text"
                placeholder="First Name *"
                value={formData.prenom}
                onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
                required
              />
              <input
                type="email"
                placeholder="Email *"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
                required
              />
              <input
                type="text"
                placeholder="CNE *"
                value={formData.cne}
                onChange={(e) => setFormData({ ...formData, cne: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
                required
              />
              <input
                type="password"
                placeholder="Password *"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
                required
              />
              <select
                value={formData.id_specialite}
                onChange={(e) => setFormData({ ...formData, id_specialite: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
                required
              >
                <option value="">Select Specialty *</option>
                {specialties.map(spec => (
                  <option key={spec.id} value={spec.id}>{spec.nom}</option>
                ))}
              </select>
              <select
                value={formData.id_groupe}
                onChange={(e) => setFormData({ ...formData, id_groupe: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500"
                required
              >
                <option value="">Select Group *</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>{group.nom}</option>
                ))}
              </select>
            </div>
            <button type="submit" className="px-6 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-xl font-semibold shadow-md">
              ➕ Create Student
            </button>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredStudents.map((student) => (
          <div key={student.id} className="bg-white border-2 border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-green-300 transition-all">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="font-bold text-lg text-gray-900">{student.prenom} {student.nom}</h3>
                <p className="text-sm text-gray-600">{student.email}</p>
                <p className="text-xs text-gray-500 mt-1">CNE: {student.cne}</p>
                <p className="text-xs text-gray-500">🎯 {student.specialite?.nom || 'N/A'}</p>
              </div>
              <button
                onClick={() => handleDelete(student.id)}
                className="p-2 text-red-600 hover:bg-red-100 rounded-lg"
                title="Delete"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredStudents.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">🎓</div>
          <p className="text-gray-600 font-medium">No students found</p>
        </div>
      )}
    </div>
  );
}

// Rooms Manager (already implemented - enhanced version)
function RoomsManager() {
  const [rooms, setRooms] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    code: '',
    type: 'AMPHITHEATRE' as 'AMPHITHEATRE' | 'TD' | 'TP' | 'AUTRE',
    capacite: 0,
  });

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      setLoading(true);
      const response = await globalCrudApi.rooms.list({ limit: 100 });
      setRooms(response.data || []);
    } catch (error: any) {
      console.error('Failed to load rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await globalCrudApi.rooms.create(formData);
      setShowForm(false);
      setFormData({ code: '', type: 'AMPHITHEATRE', capacite: 0 });
      loadRooms();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Creation failed'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this room?')) return;
    try {
      await globalCrudApi.rooms.delete(id);
      loadRooms();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Delete failed'));
    }
  };

  const filteredRooms = rooms.filter(r =>
    r.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-4 border-cyan-600 border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span>🚪</span> Classrooms Management
          </h2>
          <p className="text-sm text-gray-600 mt-1">{filteredRooms.length} room{filteredRooms.length !== 1 ? 's' : ''}</p>
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <input
            type="text"
            placeholder="🔍 Search rooms..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 md:w-64 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500"
          />
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl hover:from-cyan-700 hover:to-blue-700 font-semibold shadow-md"
          >
            {showForm ? '✕ Cancel' : '+ Add Room'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-gradient-to-br from-cyan-50 to-blue-100 border-2 border-cyan-300 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-cyan-900">➕ Create New Room</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                type="text"
                placeholder="Room Code *"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500"
                required
              />
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500"
              >
                <option value="AMPHITHEATRE">Amphitheatre</option>
                <option value="TD">TD Room</option>
                <option value="TP">TP Room</option>
                <option value="AUTRE">Other</option>
              </select>
              <input
                type="number"
                placeholder="Capacity *"
                value={formData.capacite || ''}
                onChange={(e) => setFormData({ ...formData, capacite: parseInt(e.target.value) || 0 })}
                className="px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-cyan-500"
                min="1"
                required
              />
            </div>
            <button type="submit" className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl font-semibold shadow-md">
              ➕ Create Room
            </button>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filteredRooms.map((room) => (
          <div key={room.id} className="bg-white border-2 border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-cyan-300 transition-all">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-bold text-xl text-gray-900">{room.code}</h3>
              <button
                onClick={() => handleDelete(room.id)}
                className="p-2 text-red-600 hover:bg-red-100 rounded-lg"
                title="Delete"
              >
                🗑️
              </button>
            </div>
            <div className="space-y-1 text-sm">
              <p className="text-gray-600">📁 Type: <span className="font-semibold">{room.type}</span></p>
              <p className="text-gray-600">👥 Capacity: <span className="font-semibold">{room.capacite}</span></p>
            </div>
          </div>
        ))}
      </div>

      {filteredRooms.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">🚪</div>
          <p className="text-gray-600 font-medium">No rooms found</p>
        </div>
      )}
    </div>
  );
}

// Subjects Manager with full CRUD
function SubjectsManager() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [allLevels, setAllLevels] = useState<any[]>([]); // All levels from DB
  const [allSpecialties, setAllSpecialties] = useState<any[]>([]); // All specialties from DB
  const [availableSpecialties, setAvailableSpecialties] = useState<any[]>([]); // Filtered by department
  const [availableLevels, setAvailableLevels] = useState<any[]>([]); // Filtered by specialty
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDept, setFilterDept] = useState('');
  const [formData, setFormData] = useState({
    nom: '',
    coefficient: 1.0,
    semester: '',
    id_departement: '',
    id_niveau: '',
    id_specialite: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  // STEP 1: When department changes → Load specialties for that department
  useEffect(() => {
    if (formData.id_departement) {
      loadSpecialtiesForDepartment(formData.id_departement);
      // Reset specialty and level when department changes
      setFormData(prev => ({ ...prev, id_specialite: '', id_niveau: '' }));
      setAvailableLevels([]);
    } else {
      setAvailableSpecialties([]);
      setAvailableLevels([]);
      setFormData(prev => ({ ...prev, id_specialite: '', id_niveau: '' }));
    }
  }, [formData.id_departement]);

  // STEP 2: When specialty changes → Load levels for that specialty
  useEffect(() => {
    if (formData.id_specialite) {
      loadLevelsForSpecialty(formData.id_specialite);
      // Reset level when specialty changes
      setFormData(prev => ({ ...prev, id_niveau: '' }));
    } else {
      setAvailableLevels([]);
      setFormData(prev => ({ ...prev, id_niveau: '' }));
    }
  }, [formData.id_specialite]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [subjectsRes, deptsRes, levelsRes, specsRes] = await Promise.all([
        globalCrudApi.subjects.list({ limit: 100 }),
        globalCrudApi.departments.list({ limit: 100 }),
        globalCrudApi.levels.list({ limit: 100 }),
        globalCrudApi.specialties.list({ limit: 100 })
      ]);
      setSubjects(subjectsRes.data || []);
      setDepartments(deptsRes.data || []);
      setAllLevels(levelsRes.data || []);
      setAllSpecialties(specsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load specialties that belong to the selected department
  const loadSpecialtiesForDepartment = async (deptId: string) => {
    try {
      // Use backend filtering with department_id
      const specsRes = await globalCrudApi.specialties.list({ 
        department_id: deptId,
        limit: 100 
      });
      
      setAvailableSpecialties(specsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load specialties:', error);
      setAvailableSpecialties([]);
    }
  };

  // Load levels for the selected specialty
  const loadLevelsForSpecialty = async (specialtyId: string) => {
    try {
      // Use backend filtering with specialty_id
      const levelsRes = await globalCrudApi.levels.list({ 
        specialty_id: specialtyId,
        limit: 100 
      });
      
      setAvailableLevels(levelsRes.data || []);
    } catch (error: any) {
      console.error('Failed to load levels:', error);
      setAvailableLevels([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.id_specialite) {
      alert('Please select a specialty');
      return;
    }
    
    try {
      const submitData = {
        nom: formData.nom,
        coefficient: formData.coefficient,
        semester: formData.semester || undefined,
        id_departement: formData.id_departement,
        id_niveau: formData.id_niveau,
        id_specialite: formData.id_specialite
      };
      await globalCrudApi.subjects.create(submitData);
      setShowForm(false);
      setFormData({ nom: '', coefficient: 1.0, semester: '', id_departement: '', id_niveau: '', id_specialite: '' });
      setAvailableLevels([]);
      setAvailableSpecialties([]);
      loadData();
    } catch (error: any) {
      alert('Error: ' + (error.message || 'Operation failed'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this subject? This will also remove it from all schedules.')) return;
    try {
      await globalCrudApi.subjects.delete(id, false);
      loadData();
    } catch (error: any) {
      if (error.message.includes('force') || error.message.includes('sessions') || error.message.includes('grades')) {
        if (confirm('This subject has related data (schedules/grades). Force delete?')) {
          await globalCrudApi.subjects.delete(id, true);
          loadData();
        }
      } else {
        alert('Error: ' + (error.message || 'Delete failed'));
      }
    }
  };

  const filteredSubjects = subjects.filter(s => {
    const matchesSearch = s.nom.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDept = !filterDept || s.id_departement === filterDept;
    return matchesSearch && matchesDept;
  });

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-4 border-red-600 border-t-transparent"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span>📚</span> Subjects Management
            </h2>
            <p className="text-sm text-gray-600 mt-1">{filteredSubjects.length} subject{filteredSubjects.length !== 1 ? 's' : ''}</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-2 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 font-semibold shadow-md"
          >
            {showForm ? '✕ Cancel' : '+ Add Subject'}
          </button>
        </div>
        
        <div className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            placeholder="🔍 Search subjects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500"
          />
          <select
            value={filterDept}
            onChange={(e) => setFilterDept(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500"
          >
            <option value="">All Departments</option>
            {departments.map(dept => (
              <option key={dept.id} value={dept.id}>{dept.nom}</option>
            ))}
          </select>
        </div>
      </div>

      {showForm && (
        <div className="bg-gradient-to-br from-red-50 to-pink-100 border-2 border-red-300 rounded-2xl p-6 shadow-lg">
          <h3 className="text-lg font-bold mb-4 text-red-900">➕ Create New Subject</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Subject Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g., Advanced Mathematics"
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Coefficient *
                </label>
                <input
                  type="number"
                  step="0.1"
                  placeholder="1.0"
                  value={formData.coefficient}
                  onChange={(e) => setFormData({ ...formData, coefficient: parseFloat(e.target.value) || 1.0 })}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500"
                  min="0.1"
                  max="10"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Semester
                </label>
                <select
                  value={formData.semester}
                  onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500"
                >
                  <option value="">Select Semester (Optional)</option>
                  <option value="S1">Semester 1 (S1)</option>
                  <option value="S2">Semester 2 (S2)</option>
                  <option value="S3">Semester 3 (S3)</option>
                  <option value="S4">Semester 4 (S4)</option>
                  <option value="S5">Semester 5 (S5)</option>
                  <option value="S6">Semester 6 (S6)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Department *
                </label>
                <select
                  value={formData.id_departement}
                  onChange={(e) => {
                    const deptId = e.target.value;
                    setFormData({ ...formData, id_departement: deptId, id_specialite: '', id_niveau: '' });
                    if (deptId) {
                      loadSpecialtiesForDepartment(deptId);
                    } else {
                      setAvailableSpecialties([]);
                      setAvailableLevels([]);
                    }
                  }}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500"
                  required
                >
                  <option value="">Select Department</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>{dept.nom}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Specialty *
                  {availableSpecialties.length > 0 && (
                    <span className="text-xs text-green-600 ml-2">({availableSpecialties.length} available)</span>
                  )}
                </label>
                <select
                  value={formData.id_specialite}
                  onChange={(e) => {
                    const specId = e.target.value;
                    setFormData({ ...formData, id_specialite: specId, id_niveau: '' });
                    if (specId) {
                      loadLevelsForSpecialty(specId);
                    } else {
                      setAvailableLevels([]);
                    }
                  }}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  disabled={!formData.id_departement || availableSpecialties.length === 0}
                  required
                >
                  <option value="">
                    {!formData.id_departement 
                      ? 'Select a department first' 
                      : availableSpecialties.length === 0 
                      ? 'No specialties available for this department'
                      : 'Select Specialty'}
                  </option>
                  {availableSpecialties.map(spec => (
                    <option key={spec.id} value={spec.id}>{spec.nom}</option>
                  ))}
                </select>
                {!formData.id_departement && (
                  <p className="text-xs text-gray-500 mt-1">Select a department first</p>
                )}
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Level *
                  {availableLevels.length > 0 && (
                    <span className="text-xs text-green-600 ml-2">({availableLevels.length} available)</span>
                  )}
                </label>
                <select
                  value={formData.id_niveau}
                  onChange={(e) => setFormData({ ...formData, id_niveau: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                  disabled={!formData.id_specialite || availableLevels.length === 0}
                  required
                >
                  <option value="">
                    {!formData.id_departement 
                      ? 'Select a department first' 
                      : !formData.id_specialite 
                      ? 'Select a specialty first'
                      : availableLevels.length === 0
                      ? 'No levels available for this specialty'
                      : 'Select Level'}
                  </option>
                  {availableLevels.map(level => (
                    <option key={level.id} value={level.id}>{level.nom}</option>
                  ))}
                </select>
                <p className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                  <span>ℹ️</span>
                  <span>
                    Each specialty contains specific levels (e.g., Computer Science → 1st year, 2nd year, 3rd year).
                  </span>
                </p>
              </div>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">
                ℹ️ <strong>Note:</strong> Teachers are assigned to subjects in the schedule/timetable, 
                not here. This allows different teachers to teach the same subject in different semesters.
              </p>
            </div>
            <button type="submit" className="px-6 py-3 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl font-semibold shadow-md">
              ➕ Create Subject
            </button>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSubjects.map((subject) => (
          <div key={subject.id} className="bg-white border-2 border-gray-200 rounded-xl p-5 hover:shadow-xl hover:border-red-300 transition-all">
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h3 className="font-bold text-lg text-gray-900">{subject.nom}</h3>
                <div className="mt-2 space-y-1">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-semibold text-gray-600">📊 Coefficient:</span>
                    <span className="bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full text-xs font-semibold">
                      {subject.coefficient}
                    </span>
                  </div>
                  {subject.semester && (
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <span className="font-semibold">📅 Semester:</span>
                      <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">
                        {subject.semester}
                      </span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-xs text-gray-600">
                    <span className="font-semibold">🏢 Department:</span>
                    <span>{subject.departement?.nom || 'N/A'}</span>
                  </div>
                  {subject.niveau && (
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <span className="font-semibold">📈 Level:</span>
                      <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-semibold">
                        {subject.niveau.nom}
                      </span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-xs text-gray-600">
                    <span className="font-semibold">🎯 Specialty:</span>
                    <span className={`px-2 py-0.5 rounded-full font-semibold ${
                      subject.specialite?.nom?.toLowerCase().includes('tronc commun') || 
                      subject.specialite?.nom?.toLowerCase().includes('commun')
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-indigo-100 text-indigo-700'
                    }`}>
                      {subject.specialite?.nom || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleDelete(subject.id)}
                className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                title="Delete"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredSubjects.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">📚</div>
          <p className="text-gray-600 font-medium">No subjects found</p>
          <p className="text-sm text-gray-500 mt-1">
            {searchTerm || filterDept ? 'Try adjusting your filters' : 'Create your first subject to get started'}
          </p>
        </div>
      )}
    </div>
  );
}
