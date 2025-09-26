'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function HomePage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);



  if (loading) {
    return (
      <div className="container">
        <div className="welcome">
          <h1>Chargement...</h1>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <div className="container">
      <div className="welcome">
        <h1 className="title">Bienvenue !</h1>
        <div>
          <p>Bonjour, <strong>{user.firstName} {user.lastName}</strong></p>
          <p>Email: {user.email}</p>
          <p>Rôle: {user.role === 'STUDENT' ? 'Étudiant' : user.role === 'TEACHER' ? 'Enseignant' : user.role === 'DEPARTMENT_HEAD' ? 'Directeur de département' : 'Administrateur'}</p>
          <p>Membre depuis: {new Date(user.createdAt).toLocaleDateString('fr-FR')}</p>
        </div>
        <button 
          onClick={handleLogout}
          className="button logout-button"
        >
          Se déconnecter
        </button>
        
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <a 
            href="/test-api" 
            className="button"
            style={{ 
              textDecoration: 'none', 
              display: 'inline-block',
              backgroundColor: '#28a745',
              marginTop: '10px',
              marginRight: '10px'
            }}
          >
            🧪 Test FastAPI Backend
          </a>
          
          <a 
            href="/admin" 
            className="button"
            style={{ 
              textDecoration: 'none', 
              display: 'inline-block',
              backgroundColor: '#dc3545',
              marginTop: '10px'
            }}
          >
            🔐 Zone Admin
          </a>
        </div>
      </div>
    </div>
  );
}