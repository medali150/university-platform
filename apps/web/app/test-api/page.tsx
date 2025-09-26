'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { authApi, adminApi } from '@/lib/api-utils';

export default function TestApiPage() {
  const { user } = useAuth();
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTestApi = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await authApi.me();
      if (result.success) {
        setResponse(result.data);
      } else {
        throw new Error(result.error || 'API test failed');
      }
    } catch (err: any) {
      setError(err.message || 'Error testing API');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="container">
        <div className="welcome">
          <h1 className="title"> FastAPI Test</h1>
          <p>You must be logged in to test the API</p>
          <a href="/login" className="button">Go to Login</a>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="welcome">
        <h1 className="title"> FastAPI Test</h1>
        <p>User: {user.firstName} {user.lastName} ({user.email})</p>
        
        <button 
          onClick={handleTestApi}
          disabled={loading}
          className="button"
        >
          {loading ? 'Testing...' : 'Test FastAPI /auth/me'}
        </button>

        {error && (
          <div style={{background: '#f8d7da', padding: '15px', marginTop: '15px'}}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {response && (
          <div style={{background: '#f8f9fa', padding: '15px', marginTop: '15px'}}>
            <h4>API Response:</h4>
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </div>
        )}

        <div style={{marginTop: '20px'}}>
          <a href="/" className="button"> Back to Home</a>
        </div>
      </div>
    </div>
  );
}
