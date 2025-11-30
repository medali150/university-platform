'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuth } from '@/contexts/AdminAuthContext';

export default function AdminLoginPage() {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-white text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-purple-400 mx-auto mb-4"></div>
            <div className="absolute inset-0 rounded-full h-20 w-20 border-4 border-purple-200/20 mx-auto animate-pulse"></div>
          </div>
          <p className="text-lg font-medium">Accessing Admin Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="max-w-md w-full relative">
        {/* Glass Card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 relative">
          {/* Gradient Border Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-blue-500/20 rounded-3xl blur-sm -z-10"></div>
          
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg transform hover:scale-105 transition-transform duration-300">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-white mb-3 bg-gradient-to-r from-purple-200 to-pink-200 bg-clip-text text-transparent">
              Admin Portal
            </h1>
            <p className="text-purple-200 text-sm font-medium">
              University Platform Management
            </p>
            <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full bg-purple-500/20 border border-purple-400/30">
              <div className="w-2 h-2 bg-purple-400 rounded-full mr-2 animate-pulse"></div>
              <span className="text-purple-200 text-xs font-medium">Secure Connection</span>
            </div>
          </div>

          {/* Security Badge */}
          {attempts > 0 && (
            <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 backdrop-blur-sm border border-amber-400/30 rounded-xl p-4 mb-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-amber-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-amber-200 font-medium">
                    Login attempts: {attempts}/3
                  </p>
                  <p className="text-xs text-amber-300/80 mt-1">
                    Account will be locked after 3 failed attempts
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label htmlFor="login" className="block text-sm font-semibold text-purple-200 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  id="login"
                  type="text"
                  placeholder="Enter admin username"
                  value={login}
                  onChange={(e) => setLogin(e.target.value)}
                  required
                  disabled={isBlocked || loading}
                  className="w-full pl-12 pr-4 py-3.5 bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:ring-2 focus:ring-purple-400 focus:border-purple-400 disabled:bg-white/5 disabled:cursor-not-allowed transition-all duration-200"
                  autoComplete="username"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-purple-200 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                </div>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isBlocked || loading}
                  className="w-full pl-12 pr-12 py-3.5 bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-xl text-white placeholder-purple-300/50 focus:ring-2 focus:ring-purple-400 focus:border-purple-400 disabled:bg-white/5 disabled:cursor-not-allowed transition-all duration-200"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-purple-300 hover:text-purple-200 transition-colors"
                  disabled={isBlocked || loading}
                >
                  {showPassword ? (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isBlocked || loading}
              className={`w-full py-4 px-4 rounded-xl font-bold text-white transition-all duration-300 transform hover:scale-[1.02] ${
                isBlocked || loading
                  ? 'bg-gray-500/50 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg shadow-purple-500/50 hover:shadow-xl hover:shadow-purple-500/60'
              }`}
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white mr-3"></div>
                  <span>Authenticating...</span>
                </div>
              ) : isBlocked ? (
                <div className="flex items-center justify-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  ACCESS BLOCKED
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  SIGN IN
                </div>
              )}
            </button>

            {error && (
              <div className={`rounded-xl border p-4 backdrop-blur-sm animate-shake ${
                isBlocked 
                  ? 'bg-red-500/20 border-red-400/30' 
                  : 'bg-orange-500/20 border-orange-400/30'
              }`}>
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-200">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </form>

          {/* Development Credentials */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-6 p-4 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-xl">
              <div className="flex items-center mb-2">
                <svg className="h-5 w-5 text-blue-300 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h4 className="text-blue-200 font-semibold text-sm">Development Mode</h4>
              </div>
              <div className="text-xs text-blue-200/80 space-y-1 ml-7">
                <p><span className="font-medium">Username:</span> admin_user</p>
                <p><span className="font-medium">Password:</span> admin_password</p>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-white/10 text-center">
            <p className="text-purple-200/60 text-xs">
              University Platform Admin Panel
            </p>
            <p className="text-purple-300/40 text-xs mt-1">
              v1.0 • Secure Access • Port 3001
            </p>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-10px); }
          75% { transform: translateX(10px); }
        }
        .animate-shake {
          animation: shake 0.4s ease-in-out;
        }
      `}</style>
    </div>
  );
}