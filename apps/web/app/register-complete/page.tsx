'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function CompleteRegisterPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'ADMIN' as 'STUDENT' | 'TEACHER' | 'ADMIN' | 'DEPARTMENT_HEAD'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, register } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      router.push('/');
    }
  }, [user, router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    if (!formData.firstName || !formData.lastName) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);

    try {
      console.log('Tentative de création de compte pour:', formData.email);
      
      await register({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        role: formData.role
      });
      
      console.log('Compte créé avec succès');

      router.push('/');
    } catch (error: any) {
      console.error('Erreur complète:', error);
      
      if (error.message.includes('email already exists')) {
        setError('Cet email est déjà utilisé');
      } else if (error.message.includes('invalid email')) {
        setError('Email invalide');
      } else if (error.message.includes('password')) {
        setError('Mot de passe trop faible (minimum 6 caractères)');
      } else {
        setError(error.message || 'Erreur lors de la création du compte');
      }
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return null;
  }

  return (
    <div className="container">
      <h1 className="title">Inscription Complète</h1>
      <form onSubmit={handleRegister} className="form">
        <input
          type="text"
          name="firstName"
          placeholder="Prénom *"
          value={formData.firstName}
          onChange={handleInputChange}
          required
          className="input"
        />
        <input
          type="text"
          name="lastName"
          placeholder="Nom *"
          value={formData.lastName}
          onChange={handleInputChange}
          required
          className="input"
        />
        <input
          type="email"
          name="email"
          placeholder="Email *"
          value={formData.email}
          onChange={handleInputChange}
          required
          className="input"
        />
        <select
          name="role"
          value={formData.role}
          onChange={handleInputChange}
          className="input"
        >
          <option value="STUDENT">Étudiant</option>
          <option value="TEACHER">Enseignant</option>
          <option value="DEPARTMENT_HEAD">Directeur de département</option>
          <option value="ADMIN">Administrateur</option>
        </select>
        <input
          type="password"
          name="password"
          placeholder="Mot de passe (min. 6 caractères) *"
          value={formData.password}
          onChange={handleInputChange}
          required
          minLength={6}
          className="input"
        />
        <input
          type="password"
          name="confirmPassword"
          placeholder="Confirmer le mot de passe *"
          value={formData.confirmPassword}
          onChange={handleInputChange}
          required
          minLength={6}
          className="input"
        />
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