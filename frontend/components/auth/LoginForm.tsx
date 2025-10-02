'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useAuth } from '@/contexts/AuthContext'
import { LoginFormData } from '@/types/auth'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Loader2, Mail, Lock } from 'lucide-react'

const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'L\'email est requis')
    .email('Format d\'email invalide'),
  password: z
    .string()
    .min(1, 'Le mot de passe est requis')
    .min(6, 'Le mot de passe doit contenir au moins 6 caractères'),
})

export function LoginForm() {
  const { login, loading } = useAuth()
  const [submitError, setSubmitError] = useState<string>('')

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setSubmitError('')
      await login(data)
      // Redirect will happen in the auth context
    } catch (error) {
      console.error('Login error:', error)
      setSubmitError('Erreur de connexion. Veuillez vérifier vos identifiants.')
    }
  }

  const fillDemoCredentials = (role: 'admin' | 'teacher' | 'student' | 'depthead') => {
    const credentials = {
      admin: { email: 'admin@university.com', password: 'admin123' },
      teacher: { email: 'jean.dupont@university.com', password: 'teacher123' },
      student: { email: 'marie.martin@student.university.edu', password: 'student123' },
      depthead: { email: 'pierre.leclerc@university.com', password: 'depthead123' },
    }
    
    form.setValue('email', credentials[role].email)
    form.setValue('password', credentials[role].password)
  }

  return (
    <div className="space-y-6">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {submitError && (
            <Alert variant="destructive">
              <AlertDescription>{submitError}</AlertDescription>
            </Alert>
          )}

          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="votre.email@university.com"
                      className="pl-10"
                      disabled={loading}
                      {...field}
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Mot de passe</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      type="password"
                      placeholder="••••••••"
                      className="pl-10"
                      disabled={loading}
                      {...field}
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button 
            type="submit" 
            className="w-full bg-blue-600 hover:bg-blue-700"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Connexion en cours...
              </>
            ) : (
              'Se connecter'
            )}
          </Button>
        </form>
      </Form>

      {/* Demo credentials */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Comptes de démonstration :</h3>
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('admin')}
            className="text-xs"
            disabled={loading}
          >
            Admin
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('teacher')}
            className="text-xs"
            disabled={loading}
          >
            Enseignant
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('student')}
            className="text-xs"
            disabled={loading}
          >
            Étudiant
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fillDemoCredentials('depthead')}
            className="text-xs"
            disabled={loading}
          >
            Chef Dépt
          </Button>
        </div>
      </div>
    </div>
  )
}