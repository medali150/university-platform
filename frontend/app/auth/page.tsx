'use client';

import React, { useState } from 'react';
import { LoginForm } from '@/components/auth/LoginForm';
import { 
  DepartmentHeadRegistrationForm, 
  TeacherRegistrationForm, 
  StudentRegistrationForm 
} from '@/components/auth/RegistrationForms';
import type { LoginResponse } from '@/lib/auth-api-fixed';

type AuthMode = 'login' | 'register-dept-head' | 'register-teacher' | 'register-student';

export default function AuthPage() {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleAuthSuccess = (response: LoginResponse | any) => {
    if ('access_token' in response) {
      // Login success
      setMessage({ 
        type: 'success', 
        text: `Connexion réussie ! Bienvenue ${response.user.prenom} ${response.user.nom}` 
      });
      // Redirect will be handled by LoginForm
    } else {
      // Registration success  
      setMessage({ 
        type: 'success', 
        text: `Inscription réussie ! Vous pouvez maintenant vous connecter.` 
      });
      // Switch to login mode
      setAuthMode('login');
    }
  };

  const handleAuthError = (error: string) => {
    setMessage({ type: 'error', text: error });
  };

  const clearMessage = () => {
    setMessage(null);
  };

  const renderForm = () => {
    switch (authMode) {
      case 'login':
        return <LoginForm onSuccess={handleAuthSuccess} onError={handleAuthError} />;
      case 'register-dept-head':
        return <DepartmentHeadRegistrationForm onSuccess={handleAuthSuccess} onError={handleAuthError} />;
      case 'register-teacher':
        return <TeacherRegistrationForm onSuccess={handleAuthSuccess} onError={handleAuthError} />;
      case 'register-student':
        return <StudentRegistrationForm onSuccess={handleAuthSuccess} onError={handleAuthError} />;
      default:
        return <LoginForm onSuccess={handleAuthSuccess} onError={handleAuthError} />;
    }
  };

  const renderModeButtons = () => (
    <div className="mb-6">
      <div className="flex flex-wrap justify-center gap-2 mb-4">
        <button
          onClick={() => {
            setAuthMode('login');
            clearMessage();
          }}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            authMode === 'login'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Connexion
        </button>
        
        <button
          onClick={() => {
            setAuthMode('register-dept-head');
            clearMessage();
          }}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            authMode === 'register-dept-head'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Chef de Département
        </button>
        
        <button
          onClick={() => {
            setAuthMode('register-teacher');
            clearMessage();
          }}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            authMode === 'register-teacher'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Enseignant
        </button>
        
        <button
          onClick={() => {
            setAuthMode('register-student');
            clearMessage();
          }}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            authMode === 'register-student'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Étudiant
        </button>
      </div>
      
      <div className="text-center text-sm text-gray-600">
        {authMode === 'login' ? (
          <p>Cliquez sur votre rôle pour vous inscrire</p>
        ) : (
          <p>Déjà inscrit ? <button onClick={() => setAuthMode('login')} className="text-blue-600 hover:underline">Se connecter</button></p>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-3xl font-bold text-gray-900 mb-2">
            Système Universitaire
          </h1>
          <p className="text-center text-gray-600">
            Authentification et inscription
          </p>
        </div>

        {renderModeButtons()}

        {message && (
          <div
            className={`p-4 rounded-md ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200 text-green-700'
                : 'bg-red-50 border border-red-200 text-red-700'
            }`}
          >
            <div className="flex justify-between items-start">
              <p>{message.text}</p>
              <button
                onClick={clearMessage}
                className="ml-2 text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        <div className="bg-white shadow-md rounded-lg p-6">
          {renderForm()}
        </div>

        <div className="text-center text-xs text-gray-500">
          <p>Système de gestion universitaire</p>
          <p>Authentification sécurisée pour tous les rôles</p>
        </div>
      </div>
    </div>
  );
}