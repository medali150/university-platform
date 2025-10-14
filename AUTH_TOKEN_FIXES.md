# Authentication Token Storage Fixes

## Issue
The authentication system was storing tokens with different keys causing 401 Unauthorized errors on protected endpoints like `/teacher/profile` and `/teacher/departments`.

## Root Cause
- **auth-api.ts** stores tokens as: `localStorage.setItem('authToken', loginResponse.access_token)`
- **api.ts** was reading tokens as: `localStorage.getItem('access_token')`
- This mismatch meant authenticated requests had no token header

## Fixes Applied

### 1. getAuthHeaders() Function (api.ts line 826)
**Before:**
```typescript
const token = typeof window !== 'undefined'
  ? localStorage.getItem('access_token')
  : null
```

**After:**
```typescript
const token = typeof window !== 'undefined'
  ? (localStorage.getItem('authToken') || localStorage.getItem('access_token'))
  : null
```

### 2. ApiClient.getToken() Method (api.ts line 47)
**Before:**
```typescript
private getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}
```

**After:**
```typescript
private getToken(): string | null {
  if (typeof window === 'undefined') return null
  // Check both keys for compatibility
  return localStorage.getItem('authToken') || localStorage.getItem('access_token')
}
```

### 3. ApiClient.setToken() Method (api.ts line 53)
**Before:**
```typescript
private setToken(token: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem('access_token', token)
}
```

**After:**
```typescript
private setToken(token: string): void {
  if (typeof window === 'undefined') return
  // Set both keys for compatibility
  localStorage.setItem('authToken', token)
  localStorage.setItem('access_token', token)
}
```

### 4. ApiClient.removeToken() Method (api.ts line 60)
**Before:**
```typescript
private removeToken(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}
```

**After:**
```typescript
private removeToken(): void {
  if (typeof window === 'undefined') return
  // Remove all token keys
  localStorage.removeItem('authToken')
  localStorage.removeItem('access_token')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('user')
  localStorage.removeItem('userRole')
}
```

## Token Storage Strategy

### Primary Keys (Used by auth-api.ts)
- `authToken` - JWT access token
- `refreshToken` - JWT refresh token  
- `userInfo` - User profile data
- `userRole` - User role (ADMIN, DEPARTMENT_HEAD, TEACHER, STUDENT)

### Legacy Keys (For backwards compatibility)
- `access_token`
- `refresh_token`
- `user`

## Testing Instructions

1. **Clear localStorage:**
   ```javascript
   localStorage.clear()
   ```

2. **Login as teacher:**
   - Navigate to login page
   - Enter teacher credentials
   - Verify login successful

3. **Test protected endpoints:**
   ```javascript
   // Open browser console
   console.log('Token:', localStorage.getItem('authToken'))
   console.log('Role:', localStorage.getItem('userRole'))
   ```

4. **Navigate to teacher profile:**
   - Should load without 401 errors
   - Should display teacher information
   - Should show department and specialty

5. **Check network tab:**
   - Request headers should include: `Authorization: Bearer <token>`
   - Response should be 200 OK, not 401 Unauthorized

## Expected Behavior

✅ Teacher can login successfully  
✅ Token is stored as 'authToken' in localStorage  
✅ Protected endpoints receive Authorization header  
✅ /teacher/profile returns 200 OK  
✅ /teacher/departments returns 200 OK  
✅ /teacher/schedule returns 200 OK  

## Files Modified
- `frontend/lib/api.ts` - Updated all token storage methods
- `frontend/lib/auth-api.ts` - Already using correct 'authToken' key
- `frontend/contexts/AuthContext.tsx` - Already using auth-api.ts methods

## Backwards Compatibility
The updated code checks both 'authToken' and 'access_token' keys when reading, ensuring it works with:
- New login sessions (uses 'authToken')
- Existing login sessions (uses 'access_token')
- Token refresh operations
- Manual token updates

## Related Issues Fixed
- ❌ HTTP 401 Unauthorized on /teacher/profile
- ❌ HTTP 401 Unauthorized on /teacher/departments
- ❌ Missing Authorization header on protected endpoints
- ❌ Teacher profile page showing login errors

## Status
✅ **FIXED** - All token storage operations now use consistent 'authToken' key with backwards compatibility for legacy 'access_token' key.
