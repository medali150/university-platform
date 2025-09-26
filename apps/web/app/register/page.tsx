'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('STUDENT');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, register } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      router.push('/');
    }
  }, [user, router]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    if (!fullName.trim()) {
      setError('Le nom complet est requis');
      return;
    }

    setLoading(true);

    try {
      // Split fullName into firstName and lastName
      const nameParts = fullName.trim().split(' ');
      const firstName = nameParts[0] || '';
      const lastName = nameParts.slice(1).join(' ') || '';
      
      await register({
        email,
        password,
        firstName,
        lastName,
        role
      });
      router.push('/');
    } catch (error: any) {
      if (error.message.includes('email already exists')) {
        setError('Cet email est déjà utilisé');
      } else if (error.message.includes('invalid email')) {
        setError('Email invalide');
      } else if (error.message.includes('password')) {
        setError('Mot de passe trop faible');
      } else {
        setError(error.message || 'Erreur lors de la création du compte');
      }
      console.error('Error creating account:', error);
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return null;
  }

  return (
    <div className="container">
      <h1 className="title">Créer un compte</h1>
      <form onSubmit={handleRegister} className="form">
        <input
          type="text"
          placeholder="Nom complet"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
          className="input"
        />
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
          placeholder="Mot de passe (min. 6 caractères)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
          className="input"
        />
        <input
          type="password"
          placeholder="Confirmer le mot de passe"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          minLength={6}
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
          {loading ? 'Création...' : 'Créer le compte'}
        </button>
        {error && <div className="error">{error}</div>}
        <p style={{textAlign: 'center', marginTop: '16px'}}>
          Déjà un compte ?{' '}
          <a 
            href="/login" 
            style={{color: '#007bff', textDecoration: 'none'}}
          >
            Se connecter
          </a>
        </p>
      </form>
    </div>
  );
}