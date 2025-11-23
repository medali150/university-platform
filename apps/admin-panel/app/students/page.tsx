'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminStudentApi, adminUniversityApi } from '@/lib/admin-api';

interface Student {
  id: string; // user ID
  studentRecordId?: string; // student record ID (added for easier access)
  firstName: string;
  lastName: string;
  email: string;
  login: string;
  role: string;
  createdAt: string;
  studentInfo?: {
    id: string; // student record ID
    specialty: string;
    specialtyId?: string;
    department: string;
    level: string;
    levelId?: string;
    group: string;
    groupId?: string;
  };
}

export default function AdminStudentsPage() {
  const { admin, loading: authLoading } = useAdminAuth();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [editLoading, setEditLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  useEffect(() => {
    if (admin) {
      loadStudents();
    }
  }, [admin]);

  const loadStudents = async () => {
    try {
      setLoading(true);
      const result = await adminStudentApi.getAll();
      
      if (result.success && result.data) {
        setStudents(result.data);
      } else {
        setError(result.error || 'Failed to load students');
      }
    } catch (error: any) {
      setError(error.message || 'Error loading students');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteStudent = async (student: Student) => {
    const confirmed = confirm(`Êtes-vous sûr de vouloir supprimer ${student.firstName} ${student.lastName}?`);
    if (!confirmed) return;

    // Try multiple ways to get the student ID for deletion
    const studentId = student.studentRecordId || student.studentInfo?.id || student.id;
    
    if (!studentId) {
      console.error('Cannot find student ID in:', student);
      alert('Impossible de trouver les informations de l&apos;étudiant');
      return;
    }

    try {
      setDeleteLoading(true);
      const result = await adminStudentApi.delete(studentId);
      
      if (result.success) {
        setStudents(prev => prev.filter(s => s.id !== student.id));
        alert('Étudiant supprimé avec succès!');
      } else {
        console.error('Delete failed:', result.error);
        alert(result.error || 'Erreur lors de la suppression');
      }
    } catch (error: any) {
      console.error('Delete error:', error);
      if (error.message.includes('fetch')) {
        alert('Erreur de connexion: Impossible de contacter le serveur API. Assurez-vous que l\'API est démarrée sur le port 8000.');
      } else {
        alert('Erreur lors de la suppression: ' + error.message);
      }
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleEditStudent = (student: Student) => {
    setEditingStudent(student);
    setShowEditModal(true);
  };

  const handleUpdateStudent = async (data: {
    specialtyId: string;
    groupId: string;
  }) => {
    if (!editingStudent) return;

    // Try multiple ways to get the student ID for update
    const studentId = editingStudent.studentRecordId || editingStudent.studentInfo?.id || editingStudent.id;
    
    if (!studentId) {
      console.error('Cannot find student ID in:', editingStudent);
      alert('Impossible de trouver les informations de l&apos;étudiant');
      return;
    }

    try {
      setEditLoading(true);
      const result = await adminStudentApi.update(studentId, {
        specialty_id: data.specialtyId,
        group_id: data.groupId
        // Note: level_id is not needed as it's inferred from the group
      });
      
      if (result.success) {
        alert('Étudiant modifié avec succès!');
        setShowEditModal(false);
        setEditingStudent(null);
        loadStudents(); // Reload the list
      } else {
        alert(result.error || 'Erreur lors de la modification');
      }
    } catch (error: any) {
      alert('Erreur lors de la modification: ' + error.message);
    } finally {
      setEditLoading(false);
    }
  };

  const handleAddStudent = async (studentData: {
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    password: string;
    specialtyId: string;
    groupId: string;
  }) => {
    try {
      setAddLoading(true);
      const result = await adminStudentApi.create({
        firstName: studentData.firstName,
        lastName: studentData.lastName,
        email: studentData.email,
        login: studentData.login,
        password: studentData.password,
        role: 'STUDENT' as const
      }, {
        specialty_id: studentData.specialtyId,
        group_id: studentData.groupId
      });
      
      if (result.success) {
        setShowAddModal(false);
        loadStudents(); // Reload the list
      } else {
        throw new Error(result.error || 'Failed to create student');
      }
    } catch (error: any) {
      alert('Erreur: ' + (error.message || 'Error creating student'));
    } finally {
      setAddLoading(false);
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
              <h1 className="ml-4 text-xl font-semibold">Gérer les élèves</h1>
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
              <h2 className="text-2xl font-bold text-gray-800">👨‍🎓 Gestion des Étudiants</h2>
              <p className="text-gray-600 mt-2">Créer, modifier et gérer les comptes d'élèves</p>
            </div>
            <button 
              onClick={() => setShowAddModal(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              ➕ Nouvel Étudiant
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-red-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement des étudiants...</p>
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
              onClick={loadStudents}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Réessayer
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">
                Liste des Étudiants ({students.length})
              </h3>
            </div>
            
            {students.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">📚</div>
                <h3 className="text-lg font-semibold text-gray-600 mb-2">Aucun étudiant trouvé</h3>
                <p className="text-gray-500">Commencez par créer le premier compte étudiant</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Étudiant
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
                    {students.map((student) => (
                      <tr key={student.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <span className="text-blue-600 font-semibold">
                                {student.firstName?.charAt(0) || '?'}{student.lastName?.charAt(0) || '?'}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {student.firstName} {student.lastName}
                              </div>
                              <div className="text-sm text-gray-500">
                                {student.role}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{student.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{student.login}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {new Date(student.createdAt).toLocaleDateString('fr-FR')}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button 
                            onClick={() => handleEditStudent(student)}
                            disabled={editLoading}
                            className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                          >
                            ✏️ Modifier
                          </button>
                          <button 
                            onClick={() => handleDeleteStudent(student)}
                            disabled={deleteLoading}
                            className="text-red-600 hover:text-red-900 disabled:opacity-50"
                          >
                            🗑️ Supprimer
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
          <a href="/dashboard" className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            ← Retour au Dashboard
          </a>
          <a href="/teachers" className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            👨‍🏫 Enseignants →
          </a>
        </div>
      </main>

      {/* Add Student Modal */}
      {showAddModal && (
        <AddStudentModal
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddStudent}
          loading={addLoading}
        />
      )}

      {/* Edit Student Modal */}
      {showEditModal && editingStudent && (
        <EditStudentModal
          student={editingStudent}
          onClose={() => {
            setShowEditModal(false);
            setEditingStudent(null);
          }}
          onSubmit={handleUpdateStudent}
          loading={editLoading}
        />
      )}
    </div>
  );
}

// Add Student Modal Component
interface AddStudentModalProps {
  onClose: () => void;
  onSubmit: (data: {
    firstName: string;
    lastName: string;
    email: string;
    login: string;
    password: string;
    specialtyId: string;
    groupId: string;
  }) => void;
  loading: boolean;
}

function AddStudentModal({ onClose, onSubmit, loading }: AddStudentModalProps) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    login: '',
    password: '',
    specialtyId: '',
    groupId: ''
  });
  
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [loadingSpecialties, setLoadingSpecialties] = useState(true);
  const [loadingGroups, setLoadingGroups] = useState(false);

  // Load specialties on mount
  useEffect(() => {
    loadSpecialties();
  }, []);

  // Load groups when specialty changes
  useEffect(() => {
    if (formData.specialtyId) {
      loadGroupsForSpecialty(formData.specialtyId);
    } else {
      setGroups([]);
      setFormData(prev => ({ ...prev, groupId: '' }));
    }
  }, [formData.specialtyId]);

  const loadSpecialties = async () => {
    try {
      setLoadingSpecialties(true);
      const result = await adminUniversityApi.getSpecialties();
      if (result.success && result.data) {
        setSpecialties(result.data);
      }
    } catch (error) {
      console.error('Error loading specialties:', error);
    } finally {
      setLoadingSpecialties(false);
    }
  };

  const loadGroupsForSpecialty = async (specialtyId: string) => {
    try {
      setLoadingGroups(true);
      
      // Get levels for the specialty
      const levelsResult = await adminUniversityApi.getLevelsBySpecialty(specialtyId);
      
      if (levelsResult.success && levelsResult.data?.levels) {
        const levels = levelsResult.data.levels;
        const allGroups: any[] = [];
        
        // Get groups for each level
        for (const level of levels) {
          try {
            const groupsResult = await adminUniversityApi.getGroupsByLevel(level.id);
            if (groupsResult.success && groupsResult.data?.groups) {
              allGroups.push(...groupsResult.data.groups);
            }
          } catch (error) {
            console.error(`Error loading groups for level ${level.id}:`, error);
          }
        }
        
        setGroups(allGroups);
      } else {
        console.warn('No levels found for specialty:', specialtyId);
        setGroups([]);
      }
    } catch (error) {
      console.error('Error loading groups:', error);
      // Fallback to empty groups array
      setGroups([]);
    } finally {
      setLoadingGroups(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.login || !formData.password) {
      alert('Tous les champs de base sont obligatoires');
      return;
    }
    
    if (!formData.specialtyId) {
      alert('Veuillez sélectionner une spécialité');
      return;
    }
    
    if (!formData.groupId) {
      alert('Veuillez sélectionner un groupe');
      return;
    }
    
    if (formData.password.length < 6) {
      alert('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }
    
    onSubmit(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-800">➕ Nouvel Étudiant</h3>
            <button
              onClick={onClose}
              disabled={loading}
              className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prénom *
              </label>
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="John"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom *
              </label>
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="john.doe@university.edu"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Login *
              </label>
              <input
                type="text"
                name="login"
                value={formData.login}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="johndoe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe *
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Au moins 6 caractères"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Spécialité *
              </label>
              <select
                name="specialtyId"
                value={formData.specialtyId}
                onChange={handleChange}
                disabled={loading || loadingSpecialties}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">
                  {loadingSpecialties ? 'Chargement...' : 'Sélectionner une spécialité'}
                </option>
                {specialties.map((specialty) => (
                  <option key={specialty.id} value={specialty.id}>
                    {specialty.name} ({specialty.department?.name})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Groupe *
              </label>
              <select
                name="groupId"
                value={formData.groupId}
                onChange={handleChange}
                disabled={loading || loadingGroups || !formData.specialtyId}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">
                  {!formData.specialtyId ? 'Sélectionner d\'abord une spécialité' : 
                   loadingGroups ? 'Chargement...' : 'Sélectionner un groupe'}
                </option>
                {groups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Création...' : 'Créer'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

// Edit Student Modal Component
interface EditStudentModalProps {
  student: Student;
  onClose: () => void;
  onSubmit: (data: {
    specialtyId: string;
    groupId: string;
  }) => void;
  loading: boolean;
}

function EditStudentModal({ student, onClose, onSubmit, loading }: EditStudentModalProps) {
  const [formData, setFormData] = useState({
    specialtyId: '',
    levelId: '',
    groupId: ''
  });
  
  const [specialties, setSpecialties] = useState<any[]>([]);
  const [levels, setLevels] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [loadingSpecialties, setLoadingSpecialties] = useState(true);
  const [loadingLevels, setLoadingLevels] = useState(false);
  const [loadingGroups, setLoadingGroups] = useState(false);

  // Load specialties on mount
  useEffect(() => {
    loadSpecialties();
  }, []);

  // Initialize form data with student's current values
  useEffect(() => {
    if (student && student.studentInfo) {
      setFormData({
        specialtyId: student.studentInfo.specialtyId || '',
        levelId: student.studentInfo.levelId || '',
        groupId: student.studentInfo.groupId || ''
      });
    }
  }, [student]);

  // Load levels when specialty changes
  useEffect(() => {
    if (formData.specialtyId) {
      loadLevelsForSpecialty(formData.specialtyId);
    } else {
      setLevels([]);
      setGroups([]);
      setFormData(prev => ({ ...prev, levelId: '', groupId: '' }));
    }
  }, [formData.specialtyId]);

  // Load groups when level changes
  useEffect(() => {
    if (formData.levelId) {
      loadGroupsForLevel(formData.levelId);
    } else {
      setGroups([]);
      setFormData(prev => ({ ...prev, groupId: '' }));
    }
  }, [formData.levelId]);

  const loadSpecialties = async () => {
    try {
      setLoadingSpecialties(true);
      const result = await adminUniversityApi.getSpecialties();
      
      if (result.success && result.data && Array.isArray(result.data)) {
        setSpecialties(result.data);
      } else {
        console.error('Specialties data is not an array:', result.data);
        setSpecialties([]);
      }
    } catch (error) {
      console.error('Error loading specialties:', error);
      setSpecialties([]);
    } finally {
      setLoadingSpecialties(false);
    }
  };

  const loadLevelsForSpecialty = async (specialtyId: string) => {
    try {
      setLoadingLevels(true);
      const result = await adminUniversityApi.getLevelsBySpecialty(specialtyId);
      
      if (result.success && result.data && result.data.levels && Array.isArray(result.data.levels)) {
        setLevels(result.data.levels);
      } else {
        console.error('Levels data is not valid:', result.data);
        setLevels([]);
      }
    } catch (error) {
      console.error('Error loading levels:', error);
      setLevels([]);
    } finally {
      setLoadingLevels(false);
    }
  };

  const loadGroupsForLevel = async (levelId: string) => {
    try {
      setLoadingGroups(true);
      const result = await adminUniversityApi.getGroupsByLevel(levelId);
      
      if (result.success && result.data && result.data.groups && Array.isArray(result.data.groups)) {
        setGroups(result.data.groups);
      } else {
        console.error('Groups data is not valid:', result.data);
        setGroups([]);
      }
    } catch (error) {
      console.error('Error loading groups:', error);
      setGroups([]);
    } finally {
      setLoadingGroups(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.specialtyId || !formData.levelId || !formData.groupId) {
      alert('Veuillez sélectionner une spécialité, un niveau et un groupe');
      return;
    }
    
    onSubmit({
      specialtyId: formData.specialtyId,
      groupId: formData.groupId
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Modifier l&apos;étudiant
          </h2>
          <button
            onClick={onClose}
            disabled={loading}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            ✕
          </button>
        </div>

        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">
            <strong>Étudiant:</strong> {student.firstName} {student.lastName}
          </p>
          <p className="text-sm text-gray-600">
            <strong>Email:</strong> {student.email}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="edit-specialty" className="block text-sm font-medium text-gray-700 mb-1">
              Spécialité *
            </label>
            <select
              id="edit-specialty"
              value={formData.specialtyId}
              onChange={(e) => setFormData(prev => ({ ...prev, specialtyId: e.target.value }))}
              disabled={loading || loadingSpecialties}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              required
            >
              <option value="">
                {loadingSpecialties ? 'Chargement...' : 'Sélectionnez une spécialité'}
              </option>
              {Array.isArray(specialties) && specialties.map((specialty) => (
                <option key={specialty.id} value={specialty.id}>
                  {specialty.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="edit-level" className="block text-sm font-medium text-gray-700 mb-1">
              Niveau *
            </label>
            <select
              id="edit-level"
              value={formData.levelId}
              onChange={(e) => setFormData(prev => ({ ...prev, levelId: e.target.value }))}
              disabled={loading || loadingLevels || !formData.specialtyId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              required
            >
              <option value="">
                {loadingLevels ? 'Chargement...' : 
                 !formData.specialtyId ? 'Sélectionnez d\'abord une spécialité' : 
                 'Sélectionnez un niveau'}
              </option>
              {Array.isArray(levels) && levels.map((level) => (
                <option key={level.id} value={level.id}>
                  {level.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="edit-group" className="block text-sm font-medium text-gray-700 mb-1">
              Groupe *
            </label>
            <select
              id="edit-group"
              value={formData.groupId}
              onChange={(e) => setFormData(prev => ({ ...prev, groupId: e.target.value }))}
              disabled={loading || loadingGroups || !formData.levelId}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 text-gray-900"
              required
            >
              <option value="" className="text-gray-500">
                {loadingGroups ? 'Chargement...' : 
                 !formData.levelId ? 'Sélectionnez d\'abord un niveau' : 
                 'Sélectionnez un groupe'}
              </option>
              {Array.isArray(groups) && groups.map((group) => (
                <option key={group.id} value={group.id} className="text-gray-900">
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Modification...' : 'Modifier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}