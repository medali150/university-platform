'use client'

import { useAuth } from '@/contexts/AuthContext'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function DebugAuthPage() {
  const { user, loading, isAuthenticated } = useAuth()

  return (
    <div className="container mx-auto p-8">
      <Card>
        <CardHeader>
          <CardTitle>🐛 Auth Debug Page</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <strong>Loading:</strong> {loading ? '⏳ YES' : '✅ NO'}
          </div>
          <div>
            <strong>Is Authenticated:</strong> {isAuthenticated ? '✅ YES' : '❌ NO'}
          </div>
          <div>
            <strong>Has User Object:</strong> {user ? '✅ YES' : '❌ NO'}
          </div>
          {user && (
            <div className="border-t pt-4 mt-4">
              <strong>User Details:</strong>
              <pre className="mt-2 p-4 bg-gray-100 rounded overflow-auto">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>
          )}
          <div className="border-t pt-4 mt-4">
            <strong>LocalStorage (authToken):</strong>
            <pre className="mt-2 p-4 bg-gray-100 rounded break-all text-xs">
              {typeof window !== 'undefined' ? localStorage.getItem('authToken') || 'NULL' : 'SSR'}
            </pre>
          </div>
          <div>
            <strong>LocalStorage (userInfo):</strong>
            <pre className="mt-2 p-4 bg-gray-100 rounded overflow-auto text-xs">
              {typeof window !== 'undefined' ? localStorage.getItem('userInfo') || 'NULL' : 'SSR'}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
