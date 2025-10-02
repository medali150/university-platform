'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { RegisterFormData, Role } from '@/types/auth'
import { api } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2, Mail, Lock, User, GraduationCap, ArrowLeft } from 'lucide-react'
import ClientOnly from '@/components/client-only'

export default function RegisterPage() {
  const router = useRouter()
  const { register, loading, isAuthenticated } = useAuth()
  const [formData, setFormData] = useState<RegisterFormData>({
    nom: '',
    prenom: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'STUDENT',
  })
  const [departments, setDepartments] = useState<{ id: string, name: string }[]>([])
  const [specialties, setSpecialties] = useState<{ id: string, name: string, departmentId: string }[]>([])
  const [levels, setLevels] = useState<{ id: string, name: string, specialtyId: string }[]>([])
  const [loadingMeta, setLoadingMeta] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && typeof window !== 'undefined') {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Required fields
    if (!formData.nom.trim()) newErrors.nom = 'Le nom est requis'
    if (!formData.prenom.trim()) newErrors.prenom = 'Le prénom est requis'
    if (!formData.email.trim()) newErrors.email = 'L\'email est requis'
    if (!formData.password) newErrors.password = 'Le mot de passe est requis'
    if (!formData.confirmPassword) newErrors.confirmPassword = 'Veuillez confirmer le mot de passe'

    // Email validation
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Format d\'email invalide'
    }

    // Password validation
    if (formData.password && formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères'
    }

    // Password confirmation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas'
    }

    // Role-specific required fields
    if (formData.role === 'STUDENT') {
      if (!formData.departmentId) newErrors.departmentId = 'Le département est requis'
      if (!formData.specialtyId) newErrors.specialtyId = 'La spécialité est requise'
      if (!formData.levelId) newErrors.levelId = 'Le niveau est requis'
    }

    if (formData.role === 'DEPARTMENT_HEAD') {
      if (!formData.departmentId) newErrors.departmentId = 'Le département à diriger est requis'
    }



    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      const { confirmPassword, ...registerData } = formData
      
      // Create the registration payload, including departmentId for department heads
      const registrationPayload = {
        ...registerData,
        ...(registerData.role === 'DEPARTMENT_HEAD' && registerData.departmentId && {
          departmentId: registerData.departmentId
        })
      }
      
      await register(registrationPayload)
      
      // Redirect to login page after successful registration
      router.push('/login')
    } catch (error) {
      // Error is already handled in the AuthContext with toast
      console.error('Registration error:', error)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const handleRoleChange = (value: string) => {
    setFormData(prev => ({
      ...prev,
      role: value as Role,
      departmentId: undefined,
      specialtyId: undefined,
      levelId: undefined,
    }))
    // Clear any existing errors for role-specific fields
    setErrors(prev => ({
      ...prev,
      departmentId: '',
      specialtyId: '',
      levelId: ''
    }))
  }

  // Load departments/specialties/levels
  useEffect(() => {
    const loadMeta = async () => {
      setLoadingMeta(true)
      try {
        // Load departments first so the select can render even if others fail
        const deps = await api.getDepartments()
        setDepartments(deps)

        // Load specialties and levels in parallel, but don't block department
        const [specsRes, levsRes] = await Promise.allSettled([
          api.getSpecialties(),
          api.getLevels(),
        ])

        if (specsRes.status === 'fulfilled') {
          setSpecialties(specsRes.value)
        } else {
          console.error('Failed loading specialties', specsRes.reason)
        }

        if (levsRes.status === 'fulfilled') {
          setLevels(levsRes.value)
        } else {
          console.error('Failed loading levels', levsRes.reason)
        }
      } catch (e) {
        console.error('Failed loading departments', e)
      } finally {
        setLoadingMeta(false)
      }
    }
    loadMeta()
  }, [])

  if (isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <ClientOnly fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    }>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          {/* Logo and title */}
          <div className="text-center">
            <div className="flex justify-center">
              <div className="bg-blue-600 p-3 rounded-full">
                <GraduationCap className="h-8 w-8 text-white" />
              </div>
            </div>
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Plateforme Universitaire
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Créez votre compte
            </p>
          </div>

        {/* Register form */}
        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">Inscription</CardTitle>
            <CardDescription className="text-center">
              Remplissez les informations pour créer votre compte
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Personal Information */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="prenom">Prénom</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="prenom"
                      name="prenom"
                      type="text"
                      placeholder="Jean"
                      value={formData.prenom}
                      onChange={handleInputChange}
                      className="pl-10"
                      disabled={loading}
                      required
                    />
                  </div>
                  {errors.prenom && (
                    <p className="text-sm text-red-600">{errors.prenom}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nom">Nom</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="nom"
                      name="nom"
                      type="text"
                      placeholder="Dupont"
                      value={formData.nom}
                      onChange={handleInputChange}
                      className="pl-10"
                      disabled={loading}
                      required
                    />
                  </div>
                  {errors.nom && (
                    <p className="text-sm text-red-600">{errors.nom}</p>
                  )}
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="jean.dupont@university.com"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="pl-10"
                    disabled={loading}
                    required
                  />
                </div>
                {errors.email && (
                  <p className="text-sm text-red-600">{errors.email}</p>
                )}
              </div>



              {/* Role */}
              <div className="space-y-2">
                <Label htmlFor="role">Rôle</Label>
                <Select value={formData.role} onValueChange={handleRoleChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez votre rôle" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="STUDENT">Étudiant</SelectItem>
                    <SelectItem value="TEACHER">Enseignant</SelectItem>
                    <SelectItem value="DEPARTMENT_HEAD">Chef de Département</SelectItem>
                    <SelectItem value="ADMIN">Administrateur</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Role-specific selections */}
              {formData.role === 'STUDENT' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Département</Label>
                    <Select 
                      value={formData.departmentId}
                      onValueChange={(val) => {
                        setFormData(prev => ({ ...prev, departmentId: val, specialtyId: undefined, levelId: undefined }))
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={loadingMeta ? 'Chargement...' : 'Sélectionnez un département'} />
                      </SelectTrigger>
                      <SelectContent>
                        {departments.map(d => (
                          <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.departmentId && (
                      <p className="text-sm text-red-600">{errors.departmentId}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Spécialité</Label>
                    <Select 
                      value={formData.specialtyId}
                      onValueChange={(val) => {
                        setFormData(prev => ({ ...prev, specialtyId: val, levelId: undefined }))
                      }}
                      disabled={!formData.departmentId}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={!formData.departmentId ? 'Choisissez un département d’abord' : 'Sélectionnez une spécialité'} />
                      </SelectTrigger>
                      <SelectContent>
                        {specialties
                          .filter(s => s.departmentId === formData.departmentId)
                          .map(s => (
                            <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                    {errors.specialtyId && (
                      <p className="text-sm text-red-600">{errors.specialtyId}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label>Niveau</Label>
                    <Select 
                      value={formData.levelId}
                      onValueChange={(val) => setFormData(prev => ({ ...prev, levelId: val }))}
                      disabled={!formData.specialtyId}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={!formData.specialtyId ? 'Choisissez une spécialité d’abord' : 'Sélectionnez un niveau'} />
                      </SelectTrigger>
                      <SelectContent>
                        {levels
                          .filter(l => l.specialtyId === formData.specialtyId)
                          .map(l => (
                            <SelectItem key={l.id} value={l.id}>{l.name}</SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                    {errors.levelId && (
                      <p className="text-sm text-red-600">{errors.levelId}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Department Head specific selections */}
              {formData.role === 'DEPARTMENT_HEAD' && (
                <div className="space-y-2">
                  <Label>Département à diriger</Label>
                  <Select 
                    value={formData.departmentId}
                    onValueChange={(val) => {
                      setFormData(prev => ({ ...prev, departmentId: val }))
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={loadingMeta ? 'Chargement...' : 'Sélectionnez le département à diriger'} />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map(d => (
                        <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.departmentId && (
                    <p className="text-sm text-red-600">{errors.departmentId}</p>
                  )}
                  <p className="text-sm text-gray-500">
                    Sélectionnez le département dont vous serez le chef
                  </p>
                </div>
              )}

              {/* Password */}
              <div className="space-y-2">
                <Label htmlFor="password">Mot de passe</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="pl-10"
                    disabled={loading}
                    required
                  />
                </div>
                {errors.password && (
                  <p className="text-sm text-red-600">{errors.password}</p>
                )}
              </div>

              {/* Confirm Password */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className="pl-10"
                    disabled={loading}
                    required
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="text-sm text-red-600">{errors.confirmPassword}</p>
                )}
              </div>

              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Création en cours...
                  </>
                ) : (
                  'Créer le compte'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Déjà un compte ?{' '}
                <Link 
                  href="/login" 
                  className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
                >
                  Se connecter
                </Link>
              </p>
            </div>

            {/* Back to login */}
            <div className="mt-4 text-center">
              <Link 
                href="/login"
                className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                <ArrowLeft className="mr-1 h-4 w-4" />
                Retour à la connexion
              </Link>
            </div>
          </CardContent>
        </Card>
        </div>
      </div>
    </ClientOnly>
  )
}