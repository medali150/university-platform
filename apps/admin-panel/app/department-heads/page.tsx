'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminDeptHeadApi, adminUniversityApi } from '@/lib/admin-api';

interface DepartmentHead {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  login: string;
  role: string;
  createdAt: string;
  departmentHeadInfo?: {
    id: string;
    department: {
      id: string;
      name: string;
    };
    createdAt: string;
  };
}

interface Department {
  id: string;
  name: string;
  description?: string;
}

interface CreateDeptHeadForm {
  firstName: string;
  lastName: string;
  email: string;
  login: string;
  password: string;
  departmentId: string;
}

interface EditDeptHeadForm {
  firstName: string;
  lastName: string;
  email: string;
  login: string;
}

export default function AdminDepartmentHeadsPage() {
  const { admin, loading: authLoading } = useAdminAuth();
  const [departmentHeads, setDepartmentHeads] = useState<DepartmentHead[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingDeptHead, setEditingDeptHead] = useState<DepartmentHead | null>(null);
  
  // Form states
  const [createForm, setCreateForm] = useState<CreateDeptHeadForm>({
    firstName: '',
    lastName: '',
    email: '',
    login: '',
    password: '',
    departmentId: ''
  });
  
  const [editForm, setEditForm] = useState<EditDeptHeadForm>({
    firstName: '',
    lastName: '',
    email: '',
    login: ''
  });

  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  useEffect(() => {
    if (admin) {
      loadData();
    }
  }, [admin]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load department heads and departments in parallel
      const [deptHeadsResult, departmentsResult] = await Promise.all([
        adminDeptHeadApi.getAll(),
        adminUniversityApi.getDepartments()
      ]);
      
      if (deptHeadsResult.success && deptHeadsResult.data) {
        setDepartmentHeads(deptHeadsResult.data);
      } else {
        setError(deptHeadsResult.error || 'Failed to load department heads');
      }

      if (departmentsResult.success && departmentsResult.data) {
        setDepartments(departmentsResult.data);
      }
    } catch (error: any) {
      setError(error.message || 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  // Create department head
  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessages();

    if (!createForm.firstName || !createForm.lastName || !createForm.email || 
        !createForm.login || !createForm.password || !createForm.departmentId) {
      setError('Tous les champs sont requis');
      return;
    }

    try {
      const result = await adminDeptHeadApi.create(
        {
          firstName: createForm.firstName,
          lastName: createForm.lastName,
          email: createForm.email,
          login: createForm.login,
          password: createForm.password,
          role: 'DEPARTMENT_HEAD'
        },
        { department_id: createForm.departmentId }
      );

      if (result.success) {
        setSuccess('Chef de département créé avec succès');
        setShowCreateModal(false);
        setCreateForm({
          firstName: '',
          lastName: '',
          email: '',
          login: '',
          password: '',
          departmentId: ''
        });
        loadData(); // Refresh the list
      } else {
        setError(result.error || 'Erreur lors de la création');
      }
    } catch (error: any) {
      setError(error.message || 'Erreur lors de la création');
    }
  };

  // Edit department head
  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingDeptHead?.departmentHeadInfo?.id) return;
    
    clearMessages();

    try {
      const result = await adminDeptHeadApi.updateUserInfo(
        editingDeptHead.departmentHeadInfo.id,
        editForm
      );

      if (result.success) {
        setSuccess('Chef de département modifié avec succès');
        setShowEditModal(false);
        setEditingDeptHead(null);
        loadData(); // Refresh the list
      } else {
        setError(result.error || 'Erreur lors de la modification');
      }
    } catch (error: any) {
      setError(error.message || 'Erreur lors de la modification');
    }
  };

  // Delete department head
  const handleDelete = async (deptHead: DepartmentHead) => {
    if (!deptHead.departmentHeadInfo?.id) return;
    
    const confirmMessage = `Êtes-vous sûr de vouloir supprimer ${deptHead.firstName} ${deptHead.lastName}?\n\nCette action supprimera définitivement le chef de département et l'utilisateur associé.`;
    
    if (!confirm(confirmMessage)) return;
    
    clearMessages();

    try {
      const result = await adminDeptHeadApi.delete(deptHead.departmentHeadInfo.id);

      if (result.success) {
        setSuccess('Chef de département supprimé avec succès');
        loadData(); // Refresh the list
      } else {
        setError(result.error || 'Erreur lors de la suppression');
      }
    } catch (error: any) {
      setError(error.message || 'Erreur lors de la suppression');
    }
  };

  // Open edit modal
  const openEditModal = (deptHead: DepartmentHead) => {
    setEditingDeptHead(deptHead);
    setEditForm({
      firstName: deptHead.firstName,
      lastName: deptHead.lastName,
      email: deptHead.email,
      login: deptHead.login
    });
    setShowEditModal(true);
    clearMessages();
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
              <h1 className="ml-4 text-xl font-semibold">Chefs de département</h1>
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
              <h2 className="text-2xl font-bold text-gray-800">👨‍💼 Chefs de Département</h2>
              <p className="text-gray-600 mt-2">Gérer les affectations des chefs de service</p>
            </div>
            <button 
              onClick={() => {
                setShowCreateModal(true);
                clearMessages();
              }}
              className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              ➕ Nouveau Chef de Département
            </button>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">Erreur: {error}</span>
            </div>
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">{success}</span>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-red-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement des chefs de département...</p>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">
                Liste des Chefs de Département ({departmentHeads.length})
              </h3>
            </div>
            
            {departmentHeads.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">🏢</div>
                <h3 className="text-lg font-semibold text-gray-600 mb-2">Aucun chef de département trouvé</h3>
                <p className="text-gray-500">Commencez par affecter le premier chef de département</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Chef de Département
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Login
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Département
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
                    {departmentHeads.map((deptHead) => (
                      <tr key={deptHead.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                              <span className="text-orange-600 font-semibold">
                                {deptHead.firstName.charAt(0)}{deptHead.lastName.charAt(0)}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {deptHead.firstName} {deptHead.lastName}
                              </div>
                              <div className="text-sm text-gray-500">
                                {deptHead.role}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{deptHead.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{deptHead.login}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {deptHead.departmentHeadInfo?.department?.name || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {new Date(deptHead.createdAt).toLocaleDateString('fr-FR')}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button 
                            onClick={() => openEditModal(deptHead)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            ✏️ Modifier
                          </button>
                          <button 
                            onClick={() => handleDelete(deptHead)}
                            className="text-red-600 hover:text-red-900"
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
          <a href="/teachers" className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            ← 👨‍🏫 Enseignants
          </a>
          <a href="/dashboard" className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            🏠 Dashboard
          </a>
          <a href="/system" className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            ⚙️ Système →
          </a>
        </div>
      </main>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Créer Chef de Département</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <form onSubmit={handleCreateSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Prénom</label>
                  <input
                    type="text"
                    value={createForm.firstName}
                    onChange={(e) => setCreateForm({...createForm, firstName: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Nom</label>
                  <input
                    type="text"
                    value={createForm.lastName}
                    onChange={(e) => setCreateForm({...createForm, lastName: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    value={createForm.email}
                    onChange={(e) => setCreateForm({...createForm, email: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Login</label>
                  <input
                    type="text"
                    value={createForm.login}
                    onChange={(e) => setCreateForm({...createForm, login: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Mot de passe</label>
                  <input
                    type="password"
                    value={createForm.password}
                    onChange={(e) => setCreateForm({...createForm, password: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Département</label>
                  <select
                    value={createForm.departmentId}
                    onChange={(e) => setCreateForm({...createForm, departmentId: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  >
                    <option value="">Sélectionner un département</option>
                    {departments.map((dept) => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
                  >
                    Créer
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingDeptHead && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Modifier Chef de Département</h3>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <form onSubmit={handleEditSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Prénom</label>
                  <input
                    type="text"
                    value={editForm.firstName}
                    onChange={(e) => setEditForm({...editForm, firstName: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Nom</label>
                  <input
                    type="text"
                    value={editForm.lastName}
                    onChange={(e) => setEditForm({...editForm, lastName: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({...editForm, email: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Login</label>
                  <input
                    type="text"
                    value={editForm.login}
                    onChange={(e) => setEditForm({...editForm, login: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500"
                    required
                  />
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowEditModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Modifier
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}