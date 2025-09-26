# Enhanced Registration Form - University Management API
# ====================================================

## Enhanced User Registration Examples for Swagger UI

### 1. Teacher Registration with Department Selection

#### Register Computer Science Teacher
```json
{
  "firstName": "Dr. Patricia",
  "lastName": "Chen",
  "email": "patricia.chen@university.com",
  "login": "drchen",
  "password": "prof2024secure",
  "role": "TEACHER"
}
```

#### Register Mathematics Teacher
```json
{
  "firstName": "Prof. James",
  "lastName": "Wilson",
  "email": "james.wilson@university.com",
  "login": "profwilson",
  "password": "teacher2024",
  "role": "TEACHER"
}
```

#### Register Physics Teacher
```json
{
  "firstName": "Dr. Maria",
  "lastName": "Rodriguez",
  "email": "maria.rodriguez@university.com",
  "login": "drrodriguez",
  "password": "physics2024",
  "role": "TEACHER"
}
```

### 2. Student Registration with Department Selection

#### Register Computer Science Student
```json
{
  "firstName": "Elena",
  "lastName": "Martinez",
  "email": "elena.martinez@student.university.com",
  "login": "elenamartinez",
  "password": "student2024",
  "role": "STUDENT"
}
```

#### Register Engineering Student
```json
{
  "firstName": "David",
  "lastName": "Kim",
  "email": "david.kim@student.university.com",
  "login": "davidkim",
  "password": "student2024secure",
  "role": "STUDENT"
}
```

#### Register Mathematics Student
```json
{
  "firstName": "Lisa",
  "lastName": "Thompson",
  "email": "lisa.thompson@student.university.com",
  "login": "lisathompson",
  "password": "mystudentpass",
  "role": "STUDENT"
}
```

#### Register Biology Student
```json
{
  "firstName": "Alex",
  "lastName": "Johnson",
  "email": "alex.johnson@student.university.com",
  "login": "alexjohnson",
  "password": "biostudent2024",
  "role": "STUDENT"
}
```

### 3. Department Head Registration

#### Register Computer Science Department Head
```json
{
  "firstName": "Dr. Sarah",
  "lastName": "Williams",
  "email": "sarah.williams@university.com",
  "login": "drwilliams",
  "password": "depthead2024",
  "role": "DEPARTMENT_HEAD"
}
```

#### Register Engineering Department Head
```json
{
  "firstName": "Prof. Michael",
  "lastName": "Brown",
  "email": "michael.brown@university.com",
  "login": "profbrown",
  "password": "engineering2024",
  "role": "DEPARTMENT_HEAD"
}
```

### 4. Enhanced Registration Form Fields (Frontend Implementation)

```html
<!-- HTML Form Example for Frontend -->
<form id="registrationForm" class="registration-form">
    <div class="form-section">
        <h3>Personal Information</h3>
        
        <div class="form-group">
            <label for="firstName">First Name *</label>
            <input type="text" id="firstName" name="firstName" required>
        </div>
        
        <div class="form-group">
            <label for="lastName">Last Name *</label>
            <input type="text" id="lastName" name="lastName" required>
        </div>
        
        <div class="form-group">
            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" required>
        </div>
        
        <div class="form-group">
            <label for="login">Username *</label>
            <input type="text" id="login" name="login" required>
        </div>
        
        <div class="form-group">
            <label for="password">Password *</label>
            <input type="password" id="password" name="password" required>
        </div>
    </div>
    
    <div class="form-section">
        <h3>University Information</h3>
        
        <div class="form-group">
            <label for="role">Role *</label>
            <select id="role" name="role" required onchange="showRoleSpecificFields()">
                <option value="">Select Role</option>
                <option value="STUDENT">Student</option>
                <option value="TEACHER">Teacher/Professor</option>
                <option value="DEPARTMENT_HEAD">Department Head</option>
                <option value="ADMIN">Administrator</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="department">Department *</label>
            <select id="department" name="department" required>
                <option value="">Select Department</option>
                <option value="Computer Science">Computer Science</option>
                <option value="Mathematics">Mathematics</option>
                <option value="Physics">Physics</option>
                <option value="Engineering">Engineering</option>
                <option value="Biology">Biology</option>
                <option value="Chemistry">Chemistry</option>
                <option value="Business">Business Administration</option>
                <option value="Psychology">Psychology</option>
            </select>
        </div>
    </div>
    
    <!-- Student-specific fields -->
    <div id="studentFields" class="form-section role-specific" style="display: none;">
        <h3>Student Information</h3>
        
        <div class="form-group">
            <label for="academicYear">Academic Year</label>
            <select id="academicYear" name="academicYear">
                <option value="">Select Year</option>
                <option value="1st Year">1st Year</option>
                <option value="2nd Year">2nd Year</option>
                <option value="3rd Year">3rd Year</option>
                <option value="4th Year">4th Year</option>
                <option value="Graduate">Graduate Student</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="studentId">Student ID</label>
            <input type="text" id="studentId" name="studentId" placeholder="Will be generated automatically">
        </div>
    </div>
    
    <!-- Teacher-specific fields -->
    <div id="teacherFields" class="form-section role-specific" style="display: none;">
        <h3>Teacher Information</h3>
        
        <div class="form-group">
            <label for="title">Academic Title</label>
            <select id="title" name="title">
                <option value="">Select Title</option>
                <option value="Assistant Professor">Assistant Professor</option>
                <option value="Associate Professor">Associate Professor</option>
                <option value="Professor">Professor</option>
                <option value="Lecturer">Lecturer</option>
                <option value="Instructor">Instructor</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="specialization">Area of Specialization</label>
            <input type="text" id="specialization" name="specialization">
        </div>
        
        <div class="form-group">
            <label for="experience">Years of Experience</label>
            <input type="number" id="experience" name="experience" min="0">
        </div>
    </div>
    
    <div class="form-section">
        <h3>Contact Information</h3>
        
        <div class="form-group">
            <label for="phone">Phone Number</label>
            <input type="tel" id="phone" name="phone">
        </div>
        
        <div class="form-group">
            <label for="address">Address</label>
            <textarea id="address" name="address" rows="3"></textarea>
        </div>
    </div>
    
    <div class="form-actions">
        <button type="submit" class="btn-primary">Register</button>
        <button type="reset" class="btn-secondary">Clear Form</button>
    </div>
</form>
```

### 5. JavaScript Form Handler

```javascript
// JavaScript for handling the enhanced registration form
document.getElementById('registrationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const registrationData = {
        firstName: formData.get('firstName'),
        lastName: formData.get('lastName'),
        email: formData.get('email'),
        login: formData.get('login'),
        password: formData.get('password'),
        role: formData.get('role')
    };
    
    // Add role-specific data
    if (registrationData.role === 'STUDENT') {
        registrationData.academicInfo = {
            department: formData.get('department'),
            year: formData.get('academicYear')
        };
    } else if (registrationData.role === 'TEACHER') {
        registrationData.professionalInfo = {
            department: formData.get('department'),
            title: formData.get('title'),
            specialization: formData.get('specialization'),
            experience: formData.get('experience')
        };
    }
    
    try {
        const response = await fetch('http://127.0.0.1:8000/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(registrationData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showSuccessMessage('Registration successful!');
            console.log('User registered:', result);
            // Redirect to login page or dashboard
        } else {
            const error = await response.json();
            showErrorMessage('Registration failed: ' + error.detail);
        }
    } catch (error) {
        showErrorMessage('Network error: ' + error.message);
    }
});

function showRoleSpecificFields() {
    const role = document.getElementById('role').value;
    
    // Hide all role-specific sections
    document.querySelectorAll('.role-specific').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show relevant section based on selected role
    if (role === 'STUDENT') {
        document.getElementById('studentFields').style.display = 'block';
    } else if (role === 'TEACHER' || role === 'DEPARTMENT_HEAD') {
        document.getElementById('teacherFields').style.display = 'block';
    }
}

function showSuccessMessage(message) {
    // Implementation for success notification
    alert('✅ ' + message);
}

function showErrorMessage(message) {
    // Implementation for error notification  
    alert('❌ ' + message);
}
```

### 6. CSS Styling for the Form

```css
/* Enhanced Registration Form Styles */
.registration-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-section {
    margin-bottom: 30px;
    padding: 20px;
    background: white;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
}

.form-section h3 {
    color: #333;
    margin-bottom: 15px;
    font-size: 1.2em;
    border-bottom: 2px solid #007bff;
    padding-bottom: 5px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 5px rgba(0,123,255,0.3);
}

.form-actions {
    text-align: center;
    margin-top: 20px;
}

.btn-primary,
.btn-secondary {
    padding: 12px 30px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin: 0 10px;
}

.btn-primary {
    background: #007bff;
    color: white;
}

.btn-primary:hover {
    background: #0056b3;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background: #545b62;
}

.role-specific {
    border-left: 4px solid #28a745;
    background: #f8fff9;
}
```

### 7. Testing the Enhanced Registration

#### Test Sequence in Swagger UI:

1. **Create Departments First**
   ```json
   POST /departments/
   {"name": "Computer Science"}
   {"name": "Mathematics"}
   {"name": "Engineering"}
   ```

2. **Register Admin User**
   ```json
   POST /auth/register
   {
     "firstName": "Admin",
     "lastName": "User",
     "email": "admin@university.com",
     "login": "admin",
     "password": "admin123",
     "role": "ADMIN"
   }
   ```

3. **Login and Get Token**
   ```json
   POST /auth/login
   {
     "login": "admin",
     "password": "admin123"
   }
   ```

4. **Register Teachers with Department Selection**
   ```json
   POST /auth/register
   {
     "firstName": "Dr. Sarah",
     "lastName": "Johnson",
     "email": "sarah.johnson@university.com",
     "login": "drjohnson",
     "password": "teacher123",
     "role": "TEACHER"
   }
   ```

5. **Register Students with Department Selection**
   ```json
   POST /auth/register
   {
     "firstName": "Mike",
     "lastName": "Chen",
     "email": "mike.chen@student.university.com",
     "login": "mikechen",
     "password": "student123",
     "role": "STUDENT"
   }
   ```

This enhanced registration system provides a comprehensive user onboarding experience with proper role-based field collection and department association.