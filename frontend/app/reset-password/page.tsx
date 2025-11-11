'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Lock, CheckCircle, Loader2, GraduationCap, AlertCircle } from 'lucide-react'

export default function ResetPasswordPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [loading, setLoading] = useState(false)
  const [verifying, setVerifying] = useState(true)
  const [validToken, setValidToken] = useState(false)
  const [userInfo, setUserInfo] = useState<{ email: string; nom: string; prenom: string } | null>(null)
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setError('Lien de réinitialisation invalide')
        setVerifying(false)
        return
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/reset-password/${token}`
        )

        if (response.ok) {
          const data = await response.json()
          setValidToken(true)
          setUserInfo({
            email: data.email,
            nom: data.user.nom,
            prenom: data.user.prenom
          })
        } else {
          const data = await response.json()
          setError(data.detail || 'Lien de réinitialisation invalide ou expiré')
        }
      } catch (err) {
        setError('Impossible de vérifier le lien de réinitialisation')
      } finally {
        setVerifying(false)
      }
    }

    verifyToken()
  }, [token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (newPassword.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/reset-password`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token,
            new_password: newPassword
          })
        }
      )

      if (response.ok) {
        setSuccess(true)
        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push('/login')
        }, 3000)
      } else {
        const data = await response.json()
        setError(data.detail || 'Erreur lors de la réinitialisation')
      }
    } catch (err) {
      setError('Impossible de se connecter au serveur')
    } finally {
      setLoading(false)
    }
  }

  // Loading state
  if (verifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
            <p className="text-sm text-gray-600">Vérification du lien...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Success state
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <Card className="max-w-md w-full shadow-xl border-0">
          <CardHeader>
            <div className="flex justify-center mb-4">
              <div className="bg-green-100 p-3 rounded-full">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-center">
              Mot de Passe Réinitialisé!
            </CardTitle>
            <CardDescription className="text-center">
              Votre mot de passe a été changé avec succès
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <Alert className="bg-green-50 border-green-200">
              <AlertDescription>
                Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.
              </AlertDescription>
            </Alert>
            <p className="text-sm text-gray-500">
              Redirection vers la page de connexion...
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Invalid token
  if (!validToken) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <Card className="max-w-md w-full shadow-xl border-0">
          <CardHeader>
            <div className="flex justify-center mb-4">
              <div className="bg-red-100 p-3 rounded-full">
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-center">
              Lien Invalide
            </CardTitle>
            <CardDescription className="text-center">
              Ce lien de réinitialisation n'est pas valide
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>

            <div className="space-y-3">
              <Link href="/forgot-password" className="block">
                <Button className="w-full" variant="outline">
                  Demander un Nouveau Lien
                </Button>
              </Link>
              <Link href="/login" className="block">
                <Button className="w-full">
                  Retour à la Connexion
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Reset form
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
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-center">
              Nouveau Mot de Passe
            </CardTitle>
            <CardDescription className="text-center">
              {userInfo && `${userInfo.prenom} ${userInfo.nom} (${userInfo.email})`}
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="password">Nouveau Mot de Passe</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="pl-10"
                    required
                    disabled={loading}
                    minLength={6}
                  />
                </div>
                <p className="text-xs text-gray-500">Minimum 6 caractères</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirmer le Mot de Passe</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="pl-10"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={loading}
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Réinitialisation...
                  </>
                ) : (
                  <>
                    <Lock className="mr-2 h-4 w-4" />
                    Réinitialiser le Mot de Passe
                  </>
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <Link
                href="/login"
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                Retour à la connexion
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
