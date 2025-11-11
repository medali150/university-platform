'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Mail, CheckCircle, Loader2, GraduationCap } from 'lucide-react'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })

      if (response.ok) {
        setSent(true)
      } else {
        const data = await response.json()
        // Handle both simple string errors and FastAPI validation errors
        if (typeof data.detail === 'string') {
          setError(data.detail)
        } else if (Array.isArray(data.detail)) {
          // FastAPI validation errors are arrays
          setError(data.detail[0]?.msg || 'Erreur de validation')
        } else {
          setError('Une erreur est survenue')
        }
      }
    } catch (err) {
      setError('Impossible de se connecter au serveur')
    } finally {
      setLoading(false)
    }
  }

  // Success screen
  if (sent) {
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
              Email Envoyé!
            </CardTitle>
            <CardDescription className="text-center">
              Vérifiez votre boîte de réception
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-gray-700">
                Un email contenant les instructions pour réinitialiser votre mot de passe a été envoyé à <strong>{email}</strong>.
              </p>
            </div>

            <div className="space-y-2 text-sm text-gray-600">
              <p>• Vérifiez également votre dossier spam</p>
              <p>• Le lien est valable pendant 1 heure</p>
              <p>• Si vous ne recevez pas l&apos;email, contactez l&apos;administration</p>
            </div>

            <Link href="/login" className="block pt-4">
              <Button className="w-full">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Retour à la Connexion
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Form screen
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="max-w-md w-full space-y-6">
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
              Mot de Passe Oublié?
            </CardTitle>
            <CardDescription className="text-center">
              Entrez votre email pour recevoir un lien de réinitialisation
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-4">
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email">Adresse Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="votre.email@university.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
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
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Envoi en cours...
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      Envoyer le Lien
                    </>
                  )}
                </Button>
              </div>
            </form>

            <div className="mt-6 text-center">
              <Link
                href="/login"
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="mr-1 h-4 w-4" />
                Retour à la connexion
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-700 text-center">
              <strong>Note:</strong> Seuls les comptes créés par l&apos;administration peuvent se connecter. Si vous n&apos;avez pas encore de compte, contactez votre établissement.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
