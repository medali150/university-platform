'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle, GraduationCap, Lock, Mail } from 'lucide-react'

export default function RegisterPage() {
  const router = useRouter()
  
  // Registration is disabled - only admins can create accounts
  useEffect(() => {
    // Auto-redirect after 5 seconds
    const timer = setTimeout(() => {
      router.push('/login')
    }, 5000)
    
    return () => clearTimeout(timer)
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="max-w-md w-full space-y-6">
        {/* Logo */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-blue-600 p-3 rounded-full">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Plateforme Universitaire
          </h2>
        </div>

        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1">
            <div className="flex justify-center mb-4">
              <div className="bg-yellow-100 p-3 rounded-full">
                <AlertCircle className="h-8 w-8 text-yellow-600" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-center">
              Inscription Désactivée
            </CardTitle>
            <CardDescription className="text-center">
              Les comptes sont créés uniquement par l'administration
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="space-y-4 text-center">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800 font-medium mb-2">
                  Pour les Étudiants et Enseignants
                </p>
                <p className="text-sm text-gray-700">
                  Votre compte a été créé par l'administration. Utilisez vos identifiants fournis pour vous connecter.
                </p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-800 font-medium mb-2">
                  Premier Accès?
                </p>
                <p className="text-sm text-gray-700">
                  Si c'est votre première connexion, vous devrez réinitialiser votre mot de passe.
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-3 pt-4">
              <Link href="/login" className="block">
                <Button className="w-full bg-blue-600 hover:bg-blue-700" size="lg">
                  <Mail className="mr-2 h-4 w-4" />
                  Aller à la Connexion
                </Button>
              </Link>

              <Link href="/forgot-password" className="block">
                <Button variant="outline" className="w-full" size="lg">
                  <Lock className="mr-2 h-4 w-4" />
                  Réinitialiser mon Mot de Passe
                </Button>
              </Link>
            </div>

            {/* Auto redirect notice */}
            <p className="text-xs text-center text-gray-500 pt-4">
              Redirection automatique vers la page de connexion dans 5 secondes...
            </p>
          </CardContent>
        </Card>

        {/* Help text */}
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600 text-center">
              <strong>Besoin d'aide?</strong><br />
              Contactez l'administration de votre établissement pour obtenir vos identifiants.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
