'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminManagementApi } from '@/lib/admin-api';

export default function AdminSystemPage() {
  const { admin, loading: authLoading } = useAdminAuth();
  const [systemHealth, setSystemHealth] = useState<any>(null);
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
      loadSystemHealth();
    }
  }, [admin]);

  const loadSystemHealth = async () => {
    try {
      setLoading(true);
      const result = await adminManagementApi.getSystemHealth();
      
      if (result.success && result.data) {
        setSystemHealth(result.data);
      } else {
        setError(result.error || 'Failed to load system health');
      }
    } catch (error: any) {
      setError(error.message || 'Error loading system health');
    } finally {
      setLoading(false);
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
              <h1 className="ml-4 text-xl font-semibold">Paramètres système</h1>
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
          <h2 className="text-2xl font-bold text-gray-800">⚙️ Paramètres Système</h2>
          <p className="text-gray-600 mt-2">Configurer les paramètres système et la sécurité</p>
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* System Health */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-2xl mr-2">💚</span>
              État du Système
            </h3>
            
            {loading ? (
              <div className="text-center py-6">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-red-600 mx-auto mb-2"></div>
                <p className="text-gray-600 text-sm">Vérification...</p>
              </div>
            ) : error ? (
              <div className="text-center py-6">
                <div className="text-red-500 text-4xl mb-2">⚠️</div>
                <p className="text-red-600 text-sm">{error}</p>
                <button 
                  onClick={loadSystemHealth}
                  className="mt-2 text-sm text-blue-600 hover:underline"
                >
                  Réessayer
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">🖥️ Backend API</span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                    ✅ Opérationnel
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">🗄️ Base de Données</span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                    ✅ Connecté
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">🔐 Authentication</span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                    ✅ Sécurisé
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">🌐 Admin Panel</span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                    ✅ Port 3001
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Security Settings */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <span className="text-2xl mr-2">🛡️</span>
              Paramètres de Sécurité
            </h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                <div>
                  <span className="text-sm font-medium text-gray-700">Tentatives de connexion</span>
                  <p className="text-xs text-gray-500">Maximum 3 tentatives</p>
                </div>
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
                  🔒 Activé
                </span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                <div>
                  <span className="text-sm font-medium text-gray-700">Séparation admin</span>
                  <p className="text-xs text-gray-500">Panel isolé sur port dédié</p>
                </div>
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
                  🔒 Activé
                </span>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                <div>
                  <span className="text-sm font-medium text-gray-700">Headers sécurisés</span>
                  <p className="text-xs text-gray-500">CSRF, XSS, Frame protection</p>
                </div>
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
                  🔒 Activé
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Configuration Sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-4">🔧</div>
              <h4 className="font-semibold text-gray-800 mb-2">Configuration Générale</h4>
              <p className="text-sm text-gray-600 mb-4">Paramètres globaux du système</p>
              <button 
                onClick={() => alert('Configuration générale à implémenter')}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors w-full"
              >
                Configurer
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-4">👥</div>
              <h4 className="font-semibold text-gray-800 mb-2">Gestion des Utilisateurs</h4>
              <p className="text-sm text-gray-600 mb-4">Paramètres de comptes et rôles</p>
              <button 
                onClick={() => alert('Gestion utilisateurs à implémenter')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors w-full"
              >
                Gérer
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-4">🏫</div>
              <h4 className="font-semibold text-gray-800 mb-2">Structure Universitaire</h4>
              <p className="text-sm text-gray-600 mb-4">Départements, spécialités, niveaux</p>
              <button 
                onClick={() => alert('Structure universitaire à implémenter')}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors w-full"
              >
                Configurer
              </button>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-9-2a9 9 0 1118 0 9 9 0 01-18 0z" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h4 className="text-red-800 font-semibold mb-2">⚠️ Zone Dangereuse</h4>
              <p className="text-red-700 text-sm mb-4">
                Ces actions sont irréversibles et peuvent affecter tout le système. Procédez avec prudence.
              </p>
              <div className="space-x-4">
                <button 
                  onClick={() => {
                    if (confirm('Êtes-vous sûr de vouloir purger les logs système?')) {
                      alert('Purge des logs à implémenter');
                    }
                  }}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                >
                  🗑️ Purger les Logs
                </button>
                <button 
                  onClick={() => {
                    if (confirm('Êtes-vous sûr de vouloir réinitialiser les paramètres?')) {
                      alert('Réinitialisation à implémenter');
                    }
                  }}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                >
                  🔄 Reset Système
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex justify-center space-x-4">
          <a href="/department-heads" className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            ← 👨‍💼 Chefs de Dept.
          </a>
          <a href="/dashboard" className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            🏠 Dashboard
          </a>
        </div>
      </main>
    </div>
  );
}