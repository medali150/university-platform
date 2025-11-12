'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';
import { adminBulkImportApi } from '@/lib/admin-api';

interface ImportResults {
  total: number;
  created: number;
  skipped: number;
  errors: string[];
}

export default function BulkImportPage() {
  const { admin, loading: authLoading } = useAdminAuth();
  const [studentsFile, setStudentsFile] = useState<File | null>(null);
  const [teachersFile, setTeachersFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ImportResults | null>(null);
  const [importType, setImportType] = useState<'students' | 'teachers' | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !admin) {
      router.push('/login');
    }
  }, [admin, authLoading, router]);

  const handleStudentsUpload = async () => {
    if (!studentsFile) {
      alert('Veuillez sélectionner un fichier Excel');
      return;
    }

    try {
      setLoading(true);
      setResults(null);
      setImportType('students');

      const result = await adminBulkImportApi.importStudents(studentsFile);

      if (result.success && result.data) {
        setResults(result.data);
        setStudentsFile(null);
        alert(`✅ ${result.data.created} étudiants créés avec succès!`);
      } else {
        alert(`❌ Erreur: ${result.error}`);
      }
    } catch (error: any) {
      alert(`❌ Erreur: ${error.message || 'Erreur lors de l\'importation'}`);
      console.error('Import error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTeachersUpload = async () => {
    if (!teachersFile) {
      alert('Veuillez sélectionner un fichier Excel');
      return;
    }

    try {
      setLoading(true);
      setResults(null);
      setImportType('teachers');

      const result = await adminBulkImportApi.importTeachers(teachersFile);

      if (result.success && result.data) {
        setResults(result.data);
        setTeachersFile(null);
        alert(`✅ ${result.data.created} enseignants créés avec succès!`);
      } else {
        alert(`❌ Erreur: ${result.error}`);
      }
    } catch (error: any) {
      alert(`❌ Erreur: ${error.message || 'Erreur lors de l\'importation'}`);
      console.error('Import error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadStudentsTemplate = async () => {
    try {
      await adminBulkImportApi.downloadStudentsTemplate();
      alert('✅ Modèle téléchargé avec succès');
    } catch (error: any) {
      alert(`❌ Erreur: ${error.message || 'Erreur lors du téléchargement'}`);
    }
  };

  const handleDownloadTeachersTemplate = async () => {
    try {
      await adminBulkImportApi.downloadTeachersTemplate();
      alert('✅ Modèle téléchargé avec succès');
    } catch (error: any) {
      alert(`❌ Erreur: ${error.message || 'Erreur lors du téléchargement'}`);
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
              <h1 className="ml-4 text-xl font-semibold">Importation en Masse</h1>
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
          <h2 className="text-2xl font-bold text-gray-800">📊 Importation en Masse</h2>
          <p className="text-gray-600 mt-2">
            Importez plusieurs étudiants ou enseignants à la fois à partir de fichiers Excel
          </p>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">📋 Instructions</h3>
              <ol className="list-decimal list-inside space-y-1 text-blue-800">
                <li>Téléchargez le modèle Excel approprié (Étudiants ou Enseignants)</li>
                <li>Remplissez le fichier avec les données requises</li>
                <li>Téléchargez le fichier rempli en utilisant le bouton ci-dessous</li>
                <li>Les comptes seront créés automatiquement</li>
                <li>Consultez les résultats pour voir les comptes créés et les erreurs éventuelles</li>
              </ol>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Students Import Card */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
              <h3 className="text-xl font-bold text-white flex items-center">
                <span className="mr-2">👨‍🎓</span>
                Importation Étudiants
              </h3>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <button
                  onClick={handleDownloadStudentsTemplate}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Télécharger le Modèle Excel
                </button>
                <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-3 rounded-lg">
                  <p className="font-semibold mb-1">Colonnes requises:</p>
                  <p>nom, prenom, email, numero_etudiant, groupe_nom</p>
                  <p className="mt-1 font-semibold">Colonnes optionnelles:</p>
                  <p>date_naissance, telephone, adresse, password</p>
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700">
                  Fichier Excel (.xlsx, .xls)
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setStudentsFile(e.target.files?.[0] || null)}
                  disabled={loading}
                  className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:opacity-50"
                />
                {studentsFile && (
                  <p className="text-sm text-green-600 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {studentsFile.name}
                  </p>
                )}
              </div>

              <button
                onClick={handleStudentsUpload}
                disabled={!studentsFile || loading}
                className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading && importType === 'students' ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Importation en cours...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    Importer les Étudiants
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Teachers Import Card */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
              <h3 className="text-xl font-bold text-white flex items-center">
                <span className="mr-2">👨‍🏫</span>
                Importation Enseignants
              </h3>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <button
                  onClick={handleDownloadTeachersTemplate}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Télécharger le Modèle Excel
                </button>
                <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-3 rounded-lg">
                  <p className="font-semibold mb-1">Colonnes requises:</p>
                  <p>nom, prenom, email, departement_nom</p>
                  <p className="mt-1 font-semibold">Colonnes optionnelles:</p>
                  <p>telephone, specialite, password</p>
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700">
                  Fichier Excel (.xlsx, .xls)
                </label>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setTeachersFile(e.target.files?.[0] || null)}
                  disabled={loading}
                  className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
                />
                {teachersFile && (
                  <p className="text-sm text-purple-600 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {teachersFile.name}
                  </p>
                )}
              </div>

              <button
                onClick={handleTeachersUpload}
                disabled={!teachersFile || loading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading && importType === 'teachers' ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Importation en cours...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    Importer les Enseignants
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {results && (
          <div className="mt-8 bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4">
              <h3 className="text-xl font-bold text-white flex items-center">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Résultats de l'Importation
              </h3>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-blue-50 rounded-lg p-6 text-center border border-blue-200">
                  <div className="text-4xl font-bold text-blue-600 mb-2">{results.total}</div>
                  <div className="text-sm font-semibold text-blue-800 uppercase">Total Lignes</div>
                </div>
                <div className="bg-green-50 rounded-lg p-6 text-center border border-green-200">
                  <div className="text-4xl font-bold text-green-600 mb-2">{results.created}</div>
                  <div className="text-sm font-semibold text-green-800 uppercase">✅ Créés</div>
                </div>
                <div className="bg-orange-50 rounded-lg p-6 text-center border border-orange-200">
                  <div className="text-4xl font-bold text-orange-600 mb-2">{results.skipped}</div>
                  <div className="text-sm font-semibold text-orange-800 uppercase">⚠️ Ignorés</div>
                </div>
              </div>

              {results.errors.length > 0 && (
                <div>
                  <h4 className="text-lg font-bold text-gray-800 mb-3 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Erreurs et Avertissements ({results.errors.length})
                  </h4>
                  <div className="bg-orange-50 rounded-lg p-4 max-h-96 overflow-y-auto border border-orange-200">
                    <ul className="space-y-2">
                      {results.errors.map((error, index) => (
                        <li key={index} className="text-sm text-orange-900 flex items-start">
                          <span className="mr-2 mt-0.5">•</span>
                          <span>{error}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="mt-8 flex justify-center space-x-4">
          <a href="/students" className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            👨‍🎓 Étudiants
          </a>
          <a href="/teachers" className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            👨‍🏫 Enseignants
          </a>
          <a href="/dashboard" className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            ← Retour au Dashboard
          </a>
        </div>
      </main>
    </div>
  );
}
