# Debugging Department Head Login Issue

## Problem Summary
- **Backend**: ✅ Working perfectly - all roles including DEPARTMENT_HEAD can login via direct API
- **Frontend**: ✅ Teachers and students can login ❌ Department heads get 401 error

## Tests Completed

### 1. Backend Tests
All passing:
- ✅ Users exist in database (check_login_issue.py)
- ✅ Passwords are correct (check_login_issue.py)
- ✅ Direct API login works for all roles (test_direct_login.py)
- ✅ ChefDepartement records exist and linked (debug_chef_dept_login.py)
- ✅ Department heads can access /auth/me endpoint
- ✅ Department heads can access /auth/departments endpoint

### 2. Test Credentials (All verified working in backend)
```
Email: chef.dept1@university.tn
Password: Test123!
```

## Debugging Steps for Frontend

### Step 1: Check Browser Console
When trying to login as department head, open browser DevTools (F12) and check:

1. **Console tab** - Look for errors like:
   - JavaScript errors
   - React errors
   - Network errors
   - CORS errors

2. **Network tab** - Find the POST request to `/auth/login` and check:
   - Request URL: Should be `http://localhost:8000/auth/login`
   - Request Payload: Should contain `{"email": "chef.dept1@university.tn", "password": "Test123!"}`
   - Response Status: If 401, check the response body for error message
   - Response Headers: Check if CORS headers are present

### Step 2: Compare Network Requests

Login as each role and compare the network requests:

**Teacher Login** (WORKING):
- Email: teacher1@university.tn
- Password: Test123!
- Compare the `/auth/login` request

**Department Head Login** (FAILING):
- Email: chef.dept1@university.tn  
- Password: Test123!
- Compare the `/auth/login` request

Look for differences in:
- Request headers
- Request payload
- Response

### Step 3: Check localStorage

After successful teacher login, check localStorage:
```javascript
// In browser console:
console.log('authToken:', localStorage.getItem('authToken'))
console.log('userRole:', localStorage.getItem('userRole'))
console.log('userInfo:', localStorage.getItem('userInfo'))
```

Try the same after department head login attempt.

### Step 4: Test Direct Frontend API Call

Open browser console on the login page and run:
```javascript
fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'chef.dept1@university.tn',
    password: 'Test123!'
  })
})
.then(r => r.json())
.then(d => console.log('Direct fetch result:', d))
.catch(e => console.error('Direct fetch error:', e))
```

This will test if the browser can directly call the API, ruling out frontend framework issues.

### Step 5: Check if Dashboard Route Exists

Navigate directly to the department head dashboard:
```
http://localhost:3000/dashboard/department-head
```

Check if:
- Page loads (even if it says "unauthorized")
- Gets redirected to login
- Shows 404 error
- Shows other errors

## Possible Causes

Based on the tests, the issue is NOT:
- ❌ Backend authentication (proven working)
- ❌ Database records (all exist and correct)
- ❌ Password hashing (verified correct)
- ❌ CORS configuration (accepts all origins)

The issue COULD BE:
1. **Frontend API client issue**: Something in AuthContext or auth-api.ts that treats DEPARTMENT_HEAD differently
2. **Post-login navigation issue**: The redirect to `/dashboard/department-head` might be failing
3. **Frontend dashboard permission check**: The dashboard might be making an API call that fails for dept heads
4. **Browser caching**: Old tokens or data causing conflicts

## Quick Fixes to Try

### Fix 1: Clear Browser Data
1. Open DevTools (F12)
2. Go to Application tab
3. Click "Clear storage"
4. Refresh page
5. Try login again

### Fix 2: Check Frontend Environment
Ensure Next.js is running on port 3000:
```powershell
cd frontend
npm run dev
```

Check that it shows:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Fix 3: Verify API URL
Check `frontend/.env.local` (or create if missing):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Fix 4: Restart Both Servers
```powershell
# Kill all processes
# Restart backend
cd api
.\.venv\Scripts\python.exe main.py

# Restart frontend  
cd frontend
npm run dev
```

## Expected Behavior After Login

For department heads, after successful login:
1. localStorage should contain:
   - `authToken`: JWT token
   - `userRole`: "DEPARTMENT_HEAD"
   - `userInfo`: JSON with user details

2. Should redirect to: `/dashboard/department-head`

3. Dashboard should load and make these API calls:
   - GET `/auth/me` (get current user)
   - GET `/auth/departments` (get departments list)
   - Various other endpoints for dashboard data

## Next Steps

1. Follow the debugging steps above
2. Report what you find in the browser console (screenshots helpful)
3. Share the network request/response for the failing login
4. We can then create a targeted fix

## Verification Script

Once fixed, verify all roles work:

```javascript
// Run in browser console on login page
const testCredentials = [
  { email: 'teacher1@university.tn', password: 'Test123!', role: 'TEACHER' },
  { email: 'student1@university.tn', password: 'Test123!', role: 'STUDENT' },
  { email: 'chef.dept1@university.tn', password: 'Test123!', role: 'DEPARTMENT_HEAD' }
];

for (const cred of testCredentials) {
  fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: cred.email, password: cred.password })
  })
  .then(r => r.json())
  .then(d => console.log(`${cred.role}: ✅`, d.user?.prenom))
  .catch(e => console.error(`${cred.role}: ❌`, e));
}
```

All three should show ✅.
