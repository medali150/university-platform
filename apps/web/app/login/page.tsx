'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('STUDENT');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, login } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      router.push('/');
    }
  }, [user, router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password, role);
      // Note: Role validation is handled by the AuthContext
      router.push('/');
    } catch (error: any) {
      setError(error.message || 'Email ou mot de passe incorrect');
      console.error('Error signing in:', error);
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return null;
  }

  return (
    <div className="container">
      <h1 className="title">Connexion</h1>
      <form onSubmit={handleLogin} className="form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="input"
        />
        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="input"
        />
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          required
          className="input"
          style={{ padding: '12px', fontSize: '16px' }}
        >
          <option value="STUDENT">👨‍🎓 Étudiant</option>
          <option value="TEACHER">👨‍🏫 Professeur</option>
          <option value="DEPARTMENT_HEAD">👨‍💼 Chef de département</option>
        </select>
        <button 
          type="submit" 
          disabled={loading}
          className="button"
        >
          {loading ? 'Connexion...' : 'Se connecter'}
        </button>
        {error && <div className="error">{error}</div>}
        <p style={{textAlign: 'center', marginTop: '16px'}}>
          Pas de compte ?{' '}
          <a 
            href="/register" 
            style={{color: '#007bff', textDecoration: 'none'}}
          >
            Créer un compte
          </a>
        </p>
        <p style={{textAlign: 'center', marginTop: '8px', fontSize: '14px'}}>
          <a 
            href="/admin/login" 
            style={{color: '#dc3545', textDecoration: 'none'}}
          >
            🔐 Connexion Administrateur
          </a>
        </p>
      </form>
    </div>
  );
}