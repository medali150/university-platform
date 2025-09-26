'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api-utils';

export default function AdminLoginPage() {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if already authenticated as admin
    if (authApi.isAuthenticated()) {
      const user = authApi.getCurrentUser();
      if (user?.role === 'ADMIN') {
        router.push('/admin/dashboard');
      }
    }
  }, [router]);

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('Attempting admin login for:', login);
      
      const result = await authApi.login(login, password);
      
      if (result.success && result.data) {
        // Check if user is admin
        if (result.data.user.role === 'ADMIN') {
          console.log('Admin login successful');
          router.push('/admin/dashboard');
        } else {
          setError(`Access denied. Admin privileges required. Your role: ${result.data.user.role}`);
          authApi.logout(); // Clear non-admin session
        }
      } else {
        setError(result.error || 'Login failed');
      }
      
    } catch (error: any) {
      console.error('Admin login error:', error);
      setError(error.message || 'Login error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h1 className="title">🔐 Administrator Login</h1>
        <p style={{ color: '#666', fontSize: '14px' }}>
          Reserved for authorized administrators
        </p>
      </div>

      <form onSubmit={handleAdminLogin} className="form">
        <input
          type="text"
          placeholder="Administrator Login"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          required
          className="input"
          style={{ borderColor: '#dc3545' }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="input"
        />
        <button 
          type="submit" 
          disabled={loading}
          className="button"
          style={{ backgroundColor: '#dc3545' }}
        >
          {loading ? 'Logging in...' : '🔐 Admin Login'}
        </button>
        
        {error && (
          <div style={{ 
            color: '#dc3545', 
            background: '#f8d7da', 
            padding: '10px', 
            borderRadius: '4px', 
            marginTop: '10px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}
      </form>

      <div style={{ 
        marginTop: '30px', 
        padding: '15px', 
        background: '#d1ecf1', 
        borderRadius: '8px',
        border: '1px solid #bee5eb'
      }}>
        <h4 style={{ color: '#0c5460', margin: '0 0 10px 0' }}>
          📧 Test Administrator Account:
        </h4>
        <div style={{ fontSize: '14px', color: '#0c5460' }}>
          <p><strong>Login:</strong> {process.env.NEXT_PUBLIC_ADMIN_LOGIN || 'admin_user'}</p>
          <p><strong>Password:</strong> {process.env.NEXT_PUBLIC_ADMIN_PASSWORD || 'admin_password'}</p>
          <p style={{ fontSize: '12px', marginTop: '10px', fontStyle: 'italic' }}>
            Note: These credentials are configured in your .env.local file
          </p>
        </div>
      </div>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <a 
          href="/login" 
          style={{ color: '#007bff', textDecoration: 'none', fontSize: '14px' }}
        >
          ← Regular User Login
        </a>
        <br/>
        <a 
          href="/" 
          style={{ color: '#007bff', textDecoration: 'none', fontSize: '14px', marginTop: '10px', display: 'inline-block' }}
        >
          Return to Home
        </a>
      </div>
    </div>
  );
}