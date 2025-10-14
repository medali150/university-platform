# 🐛 DEBUG MODE - How to Find the Root Cause

## Current Status
The website is still experiencing redirect loops. To fix this, we need to understand **exactly** what's happening.

## Debug Tools Enabled

### 1. Debug Auth Page
Navigate to: **http://localhost:3000/debug-auth**

This page shows:
- ✅ Current loading state
- ✅ Authentication status
- ✅ User object (if exists)
- ✅ LocalStorage contents (authToken, userInfo)

### 2. Console Logging
All auth operations now log to browser console with prefixes:
- `[AuthContext]` - Auth initialization and state changes
- `[LoginPage]` - Login page behavior
- `[useRequireRole]` - Protected route checks

### 3. Redirects Temporarily Disabled
- ❌ Login page WON'T redirect to dashboard (disabled)
- ❌ Protected pages WON'T redirect to login (disabled)

This lets us see what WOULD happen without actually doing it.

---

## Steps to Debug

### Step 1: Clear Everything
```
1. Open http://localhost:3000
2. Press F12 (open Developer Tools)
3. Go to Console tab
4. Run this command:
   localStorage.clear()
5. Refresh the page (F5)
```

### Step 2: Check Initial State
```
1. You should be on /login page
2. Check console logs - should see:
   [AuthContext] Initializing auth from storage...
   [AuthContext] Stored data check { hasUser: false, hasToken: false }
   [AuthContext] No stored auth data found
   [AuthContext] Initialization complete
   [LoginPage] Not authenticated, staying on login
```

### Step 3: Try Logging In
```
1. Use test credentials:
   Email: chef.dept1@university.tn
   Password: Test123!
   
2. Click "Se connecter"

3. Watch console logs carefully - should see:
   Attempting login with: { email: '...', password: '***' }
   [AuthContext] ... (login process)
   [LoginPage] ✅ AUTHENTICATED - would redirect to: /dashboard/department-head
```

### Step 4: Check Debug Page
```
1. Manually navigate to: http://localhost:3000/debug-auth
2. Check what it shows:
   - Loading: should be ✅ NO
   - Is Authenticated: should be ✅ YES (if logged in)
   - Has User Object: should be ✅ YES (if logged in)
   - User Details: should show your user info
   - LocalStorage: should show token and user data
```

### Step 5: Try Dashboard
```
1. Manually navigate to: http://localhost:3000/dashboard/department-head
2. Check console logs - should see:
   [useRequireRole] Auth check: { ... }
   
   Either:
   [useRequireRole] ✅ Access granted
   OR:
   [useRequireRole] NOT AUTHENTICATED - would redirect to login
```

---

## What to Look For

### 🔴 Problem Signs
- [ ] Auth state changing rapidly (loading true/false/true)
- [ ] User object appearing then disappearing
- [ ] "NOT AUTHENTICATED" message appearing when you ARE logged in
- [ ] LocalStorage showing token but isAuthenticated = false
- [ ] Multiple initialization messages in quick succession

### ✅ Good Signs
- [ ] Single initialization message
- [ ] Loading state: true → false (once)
- [ ] User object persists after login
- [ ] LocalStorage matches auth state
- [ ] No rapid state changes

---

## Common Issues & Causes

### Issue 1: Token in localStorage but not authenticated
**Cause**: Auth initialization not reading from localStorage correctly
**Check**: Does getStoredToken() return the token?

### Issue 2: User object disappearing
**Cause**: Something is calling clearAuthData() or setUser(null)
**Check**: Look for "Clear auth data" or similar messages

### Issue 3: Rapid loading state changes
**Cause**: Multiple components initializing auth separately
**Check**: Count how many "[AuthContext] Initializing..." messages appear

### Issue 4: Redirect loop
**Cause**: Login page and dashboard fighting over where user should be
**Check**: Do you see both "would redirect to dashboard" AND "would redirect to login"?

---

## After Debugging

Once you've gathered the console logs and debug page info, we can:
1. Identify the exact point where auth state breaks
2. Fix the specific issue (not guessing)
3. Re-enable redirects
4. Test thoroughly

---

## Quick Commands

Clear localStorage:
```javascript
localStorage.clear()
```

Check auth state:
```javascript
console.log({
  token: localStorage.getItem('authToken'),
  user: localStorage.getItem('userInfo'),
  role: localStorage.getItem('userRole')
})
```

Manual login test (in console after visiting login page):
```javascript
// This won't work because of CORS, but shows the process
fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'chef.dept1@university.tn',
    password: 'Test123!'
  })
}).then(r => r.json()).then(console.log)
```

---

## Report Format

When reporting what you see, please include:

1. **Console Logs** (copy/paste):
   ```
   [AuthContext] ...
   [LoginPage] ...
   [useRequireRole] ...
   ```

2. **Debug Page Screenshot** or info:
   - Loading: YES/NO
   - Is Authenticated: YES/NO
   - Has User: YES/NO
   - LocalStorage token: (first 20 chars)

3. **Steps taken**:
   - Cleared localStorage? YES/NO
   - Logged in? YES/NO
   - Which pages visited?
   - Any errors in console?

This will help us fix it quickly and correctly! 🎯
