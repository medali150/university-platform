'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminTeacherApi, adminUniversityApi } from '@/lib/admin-api';

interface Teacher {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  login: string;
  role: string;
  createdAt: string;
  teacherInfo?: {
    id: string;
    department: string | null;
    specializations: string[];
  };
}

export default function AdminTeachersPage() {
  const { admin, loading: authLoading } = useAdminAuth();
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null);
  const [addLoading, setAddLoading] = useState(false);
  const [editLoading, setEditLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState('');
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  useEffect(() => {
    if (admin) {
      loadTeachers();
    }
  }, [admin]);

  const loadTeachers = async () => {
    try {
      setLoading(true);
      const result = await adminTeacherApi.getAll();
      
      if (result.success && result.data) {
        setTeachers(result.data);
      } else {
        setError(result.error || 'Failed to load teachers');
      }
    } catch (error: any) {
      setError(error.message || 'Error loading teachers');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTeacher = async (data: {
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    password: string;
    departmentId?: string;
  }) => {
    try {
      setAddLoading(true);
      
      const teacherData = {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        login: data.login,
        password: data.password,
        role: 'TEACHER' as const
      };
      
      const options: any = {};
      if (data.departmentId) {
        options.department_id = data.departmentId;
      }
      
      const result = await adminTeacherApi.create(teacherData, options);
      
      if (result.success) {
        setShowAddModal(false);
        loadTeachers(); // Reload the list
        // Show success message (you can add a toast notification here)
      } else {
        alert('Erreur: ' + (result.error || 'Failed to create teacher'));
      }
    } catch (error: any) {
      alert('Erreur: ' + (error.message || 'Error creating teacher'));
    } finally {
      setAddLoading(false);
    }
  };

  const handleEditTeacher = async (data: {
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    password?: string;
    departmentId?: string;
  }) => {
    // Try to get teacher ID from different possible structures
    const teacherInfoId = selectedTeacher?.teacherInfo?.id;
    const directId = selectedTeacher?.id;
    
    const teacherId = teacherInfoId || directId;
    
    if (!teacherId) {
      alert('Erreur: ID de l\'enseignant introuvable');
      return;
    }
    
    try {
      setEditLoading(true);
      
      const teacherData: any = {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        login: data.login,
      };
      
      if (data.password) {
        teacherData.password = data.password;
      }
      
      const options: any = {};
      if (data.departmentId !== undefined) {
        options.department_id = data.departmentId;
      }
      
      const result = await adminTeacherApi.update(teacherId, teacherData, options);
      
      if (result.success) {
        setShowEditModal(false);
        setSelectedTeacher(null);
        loadTeachers(); // Reload the list
        alert('Enseignant mis à jour avec succès!');
      } else {
        alert('Erreur: ' + (result.error || 'Failed to update teacher'));
      }
    } catch (error: any) {
      alert('Erreur: ' + (error.message || 'Error updating teacher'));
    } finally {
      setEditLoading(false);
    }
  };

  const handleDeleteTeacher = async (teacher: Teacher) => {
    // Try to get teacher ID from different possible structures
    const teacherId = teacher?.teacherInfo?.id || teacher?.id;
    
    if (!teacherId) {
      console.error('No teacher ID found in:', teacher);
      alert('Erreur: ID de l\'enseignant introuvable');
      return;
    }
    
    const confirmMessage = `Êtes-vous sûr de vouloir supprimer ${teacher.firstName} ${teacher.lastName}?\n\nCette action est irréversible et supprimera également le compte utilisateur associé.`;
    
    if (!confirm(confirmMessage)) return;
    
    try {
      setDeleteLoading(teacherId);
      
      const result = await adminTeacherApi.delete(teacherId);
      
      if (result.success) {
        loadTeachers(); // Reload the list
        alert('Enseignant supprimé avec succès!');
      } else {
        alert('Erreur: ' + (result.error || 'Failed to delete teacher'));
      }
    } catch (error: any) {
      alert('Erreur: ' + (error.message || 'Error deleting teacher'));
    } finally {
      setDeleteLoading('');
    }
  };

  if (authLoading || !admin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
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
              <a href="/dashboard" className="text-2xl font-bold hover:text-red-200">
                🔐 Admin Panel
              </a>
              <span className="ml-4 text-red-200">/</span>
              <h1 className="ml-4 text-xl font-semibold">Gérer les enseignants</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-red-100">Welcome,</p>
                <p className="font-semibold">{admin.firstName} {admin.lastName}</p>
              </div>
              <a href="/dashboard" className="bg-red-700 hover:bg-red-600 px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
                🏠 Dashboard
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">👨‍🏫 Gestion des Enseignants</h2>
              <p className="text-gray-600 mt-2">Créer, modifier et gérer les comptes d'enseignant</p>
            </div>
            <button 
              onClick={() => setShowAddModal(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              ➕ Nouvel Enseignant
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-red-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement des enseignants...</p>
          </div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">Erreur: {error}</span>
            </div>
            <button 
              onClick={loadTeachers}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Réessayer
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">
                Liste des Enseignants ({teachers.length})
              </h3>
            </div>
            
            {teachers.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">🏫</div>
                <h3 className="text-lg font-semibold text-gray-600 mb-2">Aucun enseignant trouvé</h3>
                <p className="text-gray-500">Commencez par créer le premier compte enseignant</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Enseignant
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Login
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Créé le
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {teachers.map((teacher) => (
                      <tr key={teacher.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                              <span className="text-purple-600 font-semibold">
                                {teacher.firstName.charAt(0)}{teacher.lastName.charAt(0)}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {teacher.firstName} {teacher.lastName}
                              </div>
                              <div className="text-sm text-gray-500">
                                {teacher.role}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{teacher.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{teacher.login}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {new Date(teacher.createdAt).toLocaleDateString('fr-FR')}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button 
                            onClick={() => {
                              setSelectedTeacher(teacher);
                              setShowEditModal(true);
                            }}
                            disabled={editLoading || deleteLoading === teacher.teacherInfo?.id}
                            className="text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            ✏️ Modifier
                          </button>
                          <button 
                            onClick={() => handleDeleteTeacher(teacher)}
                            disabled={editLoading || deleteLoading === (teacher.teacherInfo?.id || teacher.id)}
                            className="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {deleteLoading === (teacher.teacherInfo?.id || teacher.id) ? '⏳' : '🗑️'} Supprimer
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex justify-center space-x-4">
          <a href="/students" className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            ← 👨‍🎓 Étudiants
          </a>
          <a href="/dashboard" className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            🏠 Dashboard
          </a>
          <a href="/department-heads" className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            👨‍💼 Chefs de Dept. →
          </a>
        </div>
      </main>

      {/* Add Teacher Modal */}
      {showAddModal && (
        <AddTeacherModal
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddTeacher}
          loading={addLoading}
        />
      )}

      {/* Edit Teacher Modal */}
      {showEditModal && selectedTeacher && (
        <EditTeacherModal
          teacher={selectedTeacher}
          onClose={() => {
            setShowEditModal(false);
            setSelectedTeacher(null);
          }}
          onSubmit={handleEditTeacher}
          loading={editLoading}
        />
      )}
    </div>
  );
}

// Add Teacher Modal Component
interface AddTeacherModalProps {
  onClose: () => void;
  onSubmit: (data: {
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    password: string;
    departmentId?: string;
  }) => void;
  loading: boolean;
}

function AddTeacherModal({ onClose, onSubmit, loading }: AddTeacherModalProps) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    login: '',
    password: '',
    departmentId: ''
  });
  
  const [departments, setDepartments] = useState<any[]>([]);
  const [loadingDepartments, setLoadingDepartments] = useState(true);

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    try {
      setLoadingDepartments(true);
      const result = await adminUniversityApi.getDepartments();
      if (result.success && result.data) {
        setDepartments(result.data);
      }
    } catch (error) {
      console.error('Error loading departments:', error);
    } finally {
      setLoadingDepartments(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.login || !formData.password) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    onSubmit({
      firstName: formData.firstName,
      lastName: formData.lastName,
      email: formData.email,
      login: formData.login,
      password: formData.password,
      departmentId: formData.departmentId || undefined
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6 max-h-90vh overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Nouvel Enseignant
          </h2>
          <button
            onClick={onClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
              Prénom *
            </label>
            <input
              type="text"
              id="firstName"
              value={formData.firstName}
              onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
              Nom *
            </label>
            <input
              type="text"
              id="lastName"
              value={formData.lastName}
              onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="login" className="block text-sm font-medium text-gray-700 mb-1">
              Login *
            </label>
            <input
              type="text"
              id="login"
              value={formData.login}
              onChange={(e) => setFormData(prev => ({ ...prev, login: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Mot de passe *
            </label>
            <input
              type="password"
              id="password"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
              Département (optionnel)
            </label>
            <select
              id="department"
              value={formData.departmentId}
              onChange={(e) => setFormData(prev => ({ ...prev, departmentId: e.target.value }))}
              disabled={loading || loadingDepartments}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50"
            >
              <option value="">Sélectionner un département</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Création...' : 'Créer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Edit Teacher Modal Component
interface EditTeacherModalProps {
  teacher: Teacher;
  onClose: () => void;
  onSubmit: (data: {
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    password?: string;
    departmentId?: string;
  }) => void;
  loading: boolean;
}

function EditTeacherModal({ teacher, onClose, onSubmit, loading }: EditTeacherModalProps) {
  const [formData, setFormData] = useState({
    firstName: teacher.firstName || '',
    lastName: teacher.lastName || '',
    email: teacher.email || '',
    login: teacher.login || '',
    password: '',
    departmentId: ''
  });
  
  const [departments, setDepartments] = useState<any[]>([]);
  const [loadingDepartments, setLoadingDepartments] = useState(true);

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    try {
      setLoadingDepartments(true);
      const result = await adminUniversityApi.getDepartments();
      if (result.success && result.data) {
        setDepartments(result.data);
      }
    } catch (error) {
      console.error('Error loading departments:', error);
    } finally {
      setLoadingDepartments(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.firstName?.trim() || !formData.lastName?.trim() || !formData.email?.trim() || !formData.login?.trim()) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    const submitData: any = {
      firstName: formData.firstName.trim(),
      lastName: formData.lastName.trim(),
      email: formData.email.trim(),
      login: formData.login.trim(),
      departmentId: formData.departmentId || undefined
    };

    // Only include password if it's provided (for updates)
    if (formData.password && formData.password.trim()) {
      submitData.password = formData.password.trim();
    }

    onSubmit(submitData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6 max-h-90vh overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Modifier l'Enseignant
          </h2>
          <button
            onClick={onClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="edit-firstName" className="block text-sm font-medium text-gray-700 mb-1">
              Prénom *
            </label>
            <input
              type="text"
              id="edit-firstName"
              value={formData.firstName}
              onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="edit-lastName" className="block text-sm font-medium text-gray-700 mb-1">
              Nom *
            </label>
            <input
              type="text"
              id="edit-lastName"
              value={formData.lastName}
              onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="edit-email" className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              id="edit-email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="edit-login" className="block text-sm font-medium text-gray-700 mb-1">
              Login *
            </label>
            <input
              type="text"
              id="edit-login"
              value={formData.login}
              onChange={(e) => setFormData(prev => ({ ...prev, login: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              required
            />
          </div>

          <div>
            <label htmlFor="edit-password" className="block text-sm font-medium text-gray-700 mb-1">
              Nouveau mot de passe (optionnel)
            </label>
            <input
              type="password"
              id="edit-password"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              placeholder="Laisser vide pour ne pas changer"
            />
          </div>

          <div>
            <label htmlFor="edit-department" className="block text-sm font-medium text-gray-700 mb-1">
              Département
            </label>
            <select
              id="edit-department"
              value={formData.departmentId}
              onChange={(e) => setFormData(prev => ({ ...prev, departmentId: e.target.value }))}
              disabled={loading || loadingDepartments}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            >
              <option value="">Aucun département</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Mise à jour...' : 'Mettre à jour'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}