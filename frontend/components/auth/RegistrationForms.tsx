'use client';

import React, { useState, useEffect } from 'react';
import { authApi } from '@/lib/auth-api-fixed';
import type { 
  DepartmentHeadRegistrationData, 
  TeacherRegistrationData, 
  StudentRegistrationData,
  Department, 
  Specialty, 
  Group 
} from '@/lib/auth-api-fixed';

// Registration Form Props
interface RegistrationFormProps {
  onSuccess?: (user: any) => void;
  onError?: (error: string) => void;
}

// Department Head Registration Form
export const DepartmentHeadRegistrationForm: React.FC<RegistrationFormProps> = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    password: '',
    confirmPassword: '',
    department_id: ''
  });
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadAvailableDepartments();
  }, []);

  const loadAvailableDepartments = async () => {
    const result = await authApi.getAvailableDepartments();
    if (result.success && result.data) {
      setDepartments(result.data);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nom.trim()) newErrors.nom = 'Le nom est requis';
    if (!formData.prenom.trim()) newErrors.prenom = 'Le prénom est requis';
    if (!formData.email.trim()) newErrors.email = 'L\'email est requis';
    if (!formData.password) newErrors.password = 'Le mot de passe est requis';
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }
    if (!formData.department_id) newErrors.department_id = 'Le département est requis';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    const registrationData: DepartmentHeadRegistrationData = {
      nom: formData.nom.trim(),
      prenom: formData.prenom.trim(),
      email: formData.email.trim(),
      password: formData.password,
      role: 'DEPARTMENT_HEAD',
      department_id: formData.department_id
    };

    const result = await authApi.registerDepartmentHead(registrationData);
    
    if (result.success && result.data) {
      onSuccess?.(result.data);
    } else {
      onError?.(result.error || 'Erreur lors de l\'inscription');
    }
    
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center mb-6">Inscription Chef de Département</h2>
      
      <div>
        <label htmlFor="nom" className="block text-sm font-medium mb-1">
          Nom *
        </label>
        <input
          type="text"
          id="nom"
          name="nom"
          value={formData.nom}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.nom ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Votre nom"
        />
        {errors.nom && <p className="text-red-500 text-sm mt-1">{errors.nom}</p>}
      </div>

      <div>
        <label htmlFor="prenom" className="block text-sm font-medium mb-1">
          Prénom *
        </label>
        <input
          type="text"
          id="prenom"
          name="prenom"
          value={formData.prenom}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.prenom ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Votre prénom"
        />
        {errors.prenom && <p className="text-red-500 text-sm mt-1">{errors.prenom}</p>}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email *
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="votre.email@university.com"
        />
        {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="department_id" className="block text-sm font-medium mb-1">
          Département *
        </label>
        <select
          id="department_id"
          name="department_id"
          value={formData.department_id}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.department_id ? 'border-red-500' : 'border-gray-300'}`}
        >
          <option value="">Sélectionnez un département</option>
          {departments.map((dept) => (
            <option key={dept.id} value={dept.id}>
              {dept.nom}
            </option>
          ))}
        </select>
        {errors.department_id && <p className="text-red-500 text-sm mt-1">{errors.department_id}</p>}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">
          Mot de passe *
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Minimum 6 caractères"
        />
        {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1">
          Confirmer le mot de passe *
        </label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Répétez le mot de passe"
        />
        {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Inscription en cours...' : 'S\'inscrire comme Chef de Département'}
      </button>
    </form>
  );
};

// Teacher Registration Form
export const TeacherRegistrationForm: React.FC<RegistrationFormProps> = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    password: '',
    confirmPassword: '',
    department_id: ''
  });
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    const result = await authApi.getDepartments();
    if (result.success && result.data) {
      setDepartments(result.data);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nom.trim()) newErrors.nom = 'Le nom est requis';
    if (!formData.prenom.trim()) newErrors.prenom = 'Le prénom est requis';
    if (!formData.email.trim()) newErrors.email = 'L\'email est requis';
    if (!formData.password) newErrors.password = 'Le mot de passe est requis';
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }
    if (!formData.department_id) newErrors.department_id = 'Le département est requis';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    const registrationData: TeacherRegistrationData = {
      nom: formData.nom.trim(),
      prenom: formData.prenom.trim(),
      email: formData.email.trim(),
      password: formData.password,
      role: 'TEACHER',
      department_id: formData.department_id
    };

    const result = await authApi.registerTeacher(registrationData);
    
    if (result.success && result.data) {
      onSuccess?.(result.data);
    } else {
      onError?.(result.error || 'Erreur lors de l\'inscription');
    }
    
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center mb-6">Inscription Enseignant</h2>
      
      <div>
        <label htmlFor="nom" className="block text-sm font-medium mb-1">
          Nom *
        </label>
        <input
          type="text"
          id="nom"
          name="nom"
          value={formData.nom}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.nom ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Votre nom"
        />
        {errors.nom && <p className="text-red-500 text-sm mt-1">{errors.nom}</p>}
      </div>

      <div>
        <label htmlFor="prenom" className="block text-sm font-medium mb-1">
          Prénom *
        </label>
        <input
          type="text"
          id="prenom"
          name="prenom"
          value={formData.prenom}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.prenom ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Votre prénom"
        />
        {errors.prenom && <p className="text-red-500 text-sm mt-1">{errors.prenom}</p>}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email *
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="votre.email@university.com"
        />
        {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="department_id" className="block text-sm font-medium mb-1">
          Département *
        </label>
        <select
          id="department_id"
          name="department_id"
          value={formData.department_id}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.department_id ? 'border-red-500' : 'border-gray-300'}`}
        >
          <option value="">Sélectionnez votre département</option>
          {departments.map((dept) => (
            <option key={dept.id} value={dept.id}>
              {dept.nom}
            </option>
          ))}
        </select>
        {errors.department_id && <p className="text-red-500 text-sm mt-1">{errors.department_id}</p>}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">
          Mot de passe *
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Minimum 6 caractères"
        />
        {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1">
          Confirmer le mot de passe *
        </label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Répétez le mot de passe"
        />
        {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-green-600 text-white p-2 rounded-md hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? 'Inscription en cours...' : 'S\'inscrire comme Enseignant'}
      </button>
    </form>
  );
};

// Student Registration Form  
export const StudentRegistrationForm: React.FC<RegistrationFormProps> = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    password: '',
    confirmPassword: '',
    specialty_id: '',
    group_id: ''
  });
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadSpecialties();
  }, []);

  const loadSpecialties = async () => {
    const result = await authApi.getSpecialties();
    if (result.success && result.data) {
      setSpecialties(result.data);
    }
  };

  const loadGroups = async (specialty_id: string) => {
    const result = await authApi.getGroups(specialty_id);
    if (result.success && result.data) {
      setGroups(result.data);
    } else {
      setGroups([]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Load groups when specialty changes
    if (name === 'specialty_id' && value) {
      loadGroups(value);
      setFormData(prev => ({ ...prev, group_id: '' })); // Reset group selection
    }
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nom.trim()) newErrors.nom = 'Le nom est requis';
    if (!formData.prenom.trim()) newErrors.prenom = 'Le prénom est requis';
    if (!formData.email.trim()) newErrors.email = 'L\'email est requis';
    if (!formData.password) newErrors.password = 'Le mot de passe est requis';
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    const registrationData: StudentRegistrationData = {
      nom: formData.nom.trim(),
      prenom: formData.prenom.trim(),
      email: formData.email.trim(),
      password: formData.password,
      role: 'STUDENT',
      ...(formData.specialty_id && { specialty_id: formData.specialty_id }),
      ...(formData.group_id && { group_id: formData.group_id })
    };

    const result = await authApi.registerStudent(registrationData);
    
    if (result.success && result.data) {
      onSuccess?.(result.data);
    } else {
      onError?.(result.error || 'Erreur lors de l\'inscription');
    }
    
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center mb-6">Inscription Étudiant</h2>
      
      <div>
        <label htmlFor="nom" className="block text-sm font-medium mb-1">
          Nom *
        </label>
        <input
          type="text"
          id="nom"
          name="nom"
          value={formData.nom}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.nom ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Votre nom"
        />
        {errors.nom && <p className="text-red-500 text-sm mt-1">{errors.nom}</p>}
      </div>

      <div>
        <label htmlFor="prenom" className="block text-sm font-medium mb-1">
          Prénom *
        </label>
        <input
          type="text"
          id="prenom"
          name="prenom"
          value={formData.prenom}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.prenom ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Votre prénom"
        />
        {errors.prenom && <p className="text-red-500 text-sm mt-1">{errors.prenom}</p>}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email *
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="votre.email@student.university.com"
        />
        {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="specialty_id" className="block text-sm font-medium mb-1">
          Spécialité (optionnel)
        </label>
        <select
          id="specialty_id"
          name="specialty_id"
          value={formData.specialty_id}
          onChange={handleChange}
          className="w-full p-2 border rounded-md border-gray-300"
        >
          <option value="">Sélectionnez une spécialité (optionnel)</option>
          {specialties.map((spec) => (
            <option key={spec.id} value={spec.id}>
              {spec.nom} - {spec.departement?.nom || ''}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="group_id" className="block text-sm font-medium mb-1">
          Groupe (optionnel)
        </label>
        <select
          id="group_id"
          name="group_id"
          value={formData.group_id}
          onChange={handleChange}
          className="w-full p-2 border rounded-md border-gray-300"
          disabled={!formData.specialty_id}
        >
          <option value="">Sélectionnez un groupe (optionnel)</option>
          {groups.map((group) => (
            <option key={group.id} value={group.id}>
              {group.nom} - {group.niveau?.nom || ''}
            </option>
          ))}
        </select>
        {!formData.specialty_id && (
          <p className="text-gray-500 text-sm mt-1">
            Sélectionnez d'abord une spécialité pour voir les groupes
          </p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">
          Mot de passe *
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Minimum 6 caractères"
        />
        {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1">
          Confirmer le mot de passe *
        </label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          className={`w-full p-2 border rounded-md ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Répétez le mot de passe"
        />
        {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-purple-600 text-white p-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
      >
        {loading ? 'Inscription en cours...' : 'S\'inscrire comme Étudiant'}
      </button>
    </form>
  );
};