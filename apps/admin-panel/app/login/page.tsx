'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';

export default function AdminLoginPage() {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [isBlocked, setIsBlocked] = useState(false);
  
  const { admin, login: adminLogin } = useAdminAuth();
  const router = useRouter();

  useEffect(() => {
    if (admin) {
      router.push('/dashboard');
    }
  }, [admin, router]);

  // Security: Block after 3 failed attempts
  useEffect(() => {
    if (attempts >= 3) {
      setIsBlocked(true);
      setError('Too many failed attempts. Access blocked for security.');
      
      // Auto-unlock after 5 minutes
      setTimeout(() => {
        setAttempts(0);
        setIsBlocked(false);
        setError('');
      }, 5 * 60 * 1000);
    }
  }, [attempts]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isBlocked) {
      setError('Access blocked due to security policy. Please wait.');
      return;
    }

    setError('');
    setLoading(true);

    // Basic input validation
    if (!login.trim() || !password.trim()) {
      setError('Please enter both login and password');
      setLoading(false);
      return;
    }

    try {
      await adminLogin(login.trim(), password);
      // Success - redirect will be handled by useEffect
      setAttempts(0); // Reset on success
    } catch (error: any) {
      console.error('Admin login error:', error);
      setError(error.message || 'Invalid admin credentials');
      setAttempts(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  if (admin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-900 to-red-600">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-white mx-auto mb-4"></div>
          <p>Redirecting to admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-900 to-red-600">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 border-4 border-red-800">
        {/* Security Warning Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-20 h-20 bg-red-600 rounded-full flex items-center justify-center mb-4">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m0 0v2m0-2h2m-2 0H10m0-2V9a2 2 0 012-2h0a2 2 0 012 2v4.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-red-800 mb-2">🔒 ADMIN ACCESS</h1>
          <p className="text-red-600 text-sm font-semibold">
            AUTHORIZED PERSONNEL ONLY
          </p>
          <p className="text-gray-500 text-xs mt-2">
            This system is monitored. Unauthorized access is prohibited.
          </p>
        </div>

        {/* Security Info */}
        <div className="bg-red-50 border-l-4 border-red-600 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 20 20">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                <strong>Security Notice:</strong> Maximum 3 login attempts allowed.
                {attempts > 0 && (
                  <span className="block mt-1 text-red-800 font-semibold">
                    Attempts remaining: {3 - attempts}
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label htmlFor="login" className="block text-sm font-medium text-gray-700 mb-2">
              Administrator Login
            </label>
            <input
              id="login"
              type="text"
              placeholder="Admin username"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              required
              disabled={isBlocked || loading}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              autoComplete="username"
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="Admin password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isBlocked || loading}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              autoComplete="current-password"
            />
          </div>

          <button 
            type="submit" 
            disabled={isBlocked || loading}
            className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200 ${
              isBlocked || loading
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-red-600 hover:bg-red-700 active:bg-red-800 shadow-lg hover:shadow-xl'
            }`}
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white mr-2"></div>
                Authenticating...
              </div>
            ) : isBlocked ? (
              '🔒 ACCESS BLOCKED'
            ) : (
              '🔐 SECURE LOGIN'
            )}
          </button>

          {error && (
            <div className={`p-4 rounded-lg border-l-4 ${
              isBlocked 
                ? 'bg-red-100 border-red-500 text-red-700' 
                : 'bg-orange-100 border-orange-500 text-orange-700'
            }`}>
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 20 20">
                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium">{error}</p>
                </div>
              </div>
            </div>
          )}
        </form>

        {/* Development Credentials (only show in dev mode) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="text-blue-800 font-semibold mb-2">🧪 Development Credentials:</h4>
            <div className="text-sm text-blue-700 space-y-1">
              <p><strong>Login:</strong> admin_user</p>
              <p><strong>Password:</strong> admin_password</p>
              <p className="text-xs italic text-blue-600 mt-2">
                These credentials are for development only
              </p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500">
            University Platform Admin Panel v1.0
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Secure access • Port 3001
          </p>
        </div>
      </div>
    </div>
  );
}