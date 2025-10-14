'use client'

import { useState, useEffect } from 'react'
import { useRequireRole } from '@/hooks/useRequireRole'
import { Role } from '@/types/auth'
import { api } from '@/lib/api'

export default function DebugTimetablePage() {
  const { user, isLoading } = useRequireRole('DEPARTMENT_HEAD' as Role)
  const [debugData, setDebugData] = useState<any>({})
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<any>({})

  const testApiEndpoints = async () => {
    setLoading(true)
    setErrors({})
    setDebugData({})

    const endpoints = [
      { name: 'groups', call: () => api.getTimetableGroups() },
      { name: 'teachers', call: () => api.getTimetableTeachers() },
      { name: 'subjects', call: () => api.getTimetableSubjects() },
      { name: 'specialities', call: () => api.getTimetableSpecialities() },
      { name: 'rooms', call: () => api.getTimetableRooms() }
    ]

    const results: any = {}
    const errorResults: any = {}

    for (const endpoint of endpoints) {
      try {
        console.log(`🔍 Testing ${endpoint.name}...`)
        const data = await endpoint.call()
        results[endpoint.name] = {
          success: true,
          count: Array.isArray(data) ? data.length : 0,
          data: Array.isArray(data) ? data.slice(0, 2) : data // First 2 items for preview
        }
        console.log(`✅ ${endpoint.name}: ${results[endpoint.name].count} items`)
      } catch (error: any) {
        console.error(`❌ ${endpoint.name} failed:`, error)
        errorResults[endpoint.name] = {
          success: false,
          error: error.message || 'Unknown error',
          status: error.status || 'No status',
          details: error
        }
      }
    }

    setDebugData(results)
    setErrors(errorResults)
    setLoading(false)
  }

  useEffect(() => {
    if (user && !isLoading) {
      console.log('🔐 User authenticated:', user)
      testApiEndpoints()
    }
  }, [user, isLoading])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4">Chargement de l'authentification...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-8">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-red-600 mb-4">Accès Refusé</h2>
              <p>Vous devez être connecté en tant que Chef de Département.</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Debug Timetable API</h1>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-green-800">✅ User Authenticated</h3>
            <p className="text-green-700">Email: {user.email}</p>
            <p className="text-green-700">Role: {user.role}</p>
          </div>
          
          <button
            onClick={testApiEndpoints}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test API Endpoints'}
          </button>
        </div>

        {/* Success Results */}
        {Object.keys(debugData).length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-green-600 mb-4">✅ Successful API Calls</h2>
            {Object.entries(debugData).map(([key, value]: [string, any]) => (
              <div key={key} className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-semibold text-green-800 capitalize">{key}</h3>
                <p className="text-green-700">Count: {value.count}</p>
                {value.data && value.count > 0 && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-green-600">Show sample data</summary>
                    <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                      {JSON.stringify(value.data, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Error Results */}
        {Object.keys(errors).length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-red-600 mb-4">❌ Failed API Calls</h2>
            {Object.entries(errors).map(([key, value]: [string, any]) => (
              <div key={key} className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <h3 className="font-semibold text-red-800 capitalize">{key}</h3>
                <p className="text-red-700">Error: {value.error}</p>
                <p className="text-red-700">Status: {value.status}</p>
                <details className="mt-2">
                  <summary className="cursor-pointer text-red-600">Show error details</summary>
                  <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                    {JSON.stringify(value.details, null, 2)}
                  </pre>
                </details>
              </div>
            ))}
          </div>
        )}

        {/* Test Login Instructions */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-blue-600 mb-4">🔐 Test Login</h2>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800"><strong>Email:</strong> test.depthead@university.com</p>
            <p className="text-blue-800"><strong>Password:</strong> test123</p>
            <p className="text-blue-700 text-sm mt-2">Use these credentials to test the timetable functionality</p>
          </div>
        </div>
      </div>
    </div>
  )
}