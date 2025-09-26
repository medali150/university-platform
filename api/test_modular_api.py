"""
University Management API Test Script
=====================================

This script provides comprehensive testing for the refactored University Management API.
It includes tests for all endpoints with proper authentication flow.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8000"
headers = {"Content-Type": "application/json"}

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def set_auth_header(self):
        """Set authorization header with access token"""
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
    
    def setup_departments_for_registration(self):
        """Setup initial departments for user registration"""
        print("📋 Setting up departments for registration...")
        
        # Create basic departments without authentication (for initial setup)
        departments = [
            {"name": "Computer Science"},
            {"name": "Mathematics"},
            {"name": "Physics"},
            {"name": "Engineering"},
            {"name": "Biology"},
            {"name": "Chemistry"}
        ]
        
        # Store departments for later use
        self.available_departments = departments
        
    def display_registration_form_example(self):
        """Display example of enhanced registration form"""
        print("\n📝 Enhanced Registration Form Example:")
        print("=" * 50)
        
        form_example = {
            "firstName": "Maria",
            "lastName": "Rodriguez",
            "email": "maria.rodriguez@university.com",
            "login": "mariarodriguez",
            "password": "securepass2024",
            "role": "STUDENT",  # Options: STUDENT, TEACHER, DEPARTMENT_HEAD, ADMIN
            "selectedDepartment": "Computer Science",  # Department selection
            "personalInfo": {
                "phone": "+1-555-0123",
                "address": "123 University Ave, Student City, SC 12345",
                "dateOfBirth": "2000-05-15",
                "emergencyContact": "parent@email.com"
            }
        }
        
        print("Registration Form Fields:")
        print(f"• First Name: {form_example['firstName']}")
        print(f"• Last Name: {form_example['lastName']}")
        print(f"• Email: {form_example['email']}")
        print(f"• Login: {form_example['login']}")
        print(f"• Password: [Hidden for security]")
        print(f"• Role: {form_example['role']}")
        print(f"• Department: {form_example['selectedDepartment']}")
        print(f"• Additional Info: Phone, Address, DOB, Emergency Contact")
        print("=" * 50)
    
    def test_enhanced_user_registration(self):
        """Test enhanced user registration with department selection and role-specific data"""
        print("\n🎓 Testing Enhanced User Registration...")
        
        # Display form example
        self.display_registration_form_example()
        
        # Enhanced test users with more realistic data
        enhanced_test_users = [
            {
                "firstName": "Dr. Patricia",
                "lastName": "Chen",
                "email": "patricia.chen@university.com",
                "login": "drchen",
                "password": "prof2024secure",
                "role": "TEACHER",
                "department": "Computer Science",
                "specialization": "Artificial Intelligence",
                "experience": "10 years"
            },
            {
                "firstName": "Prof. James",
                "lastName": "Wilson",
                "email": "james.wilson@university.com",
                "login": "profwilson",
                "password": "teacher2024",
                "role": "TEACHER", 
                "department": "Mathematics",
                "specialization": "Statistics and Data Analysis",
                "experience": "15 years"
            },
            {
                "firstName": "Elena",
                "lastName": "Martinez",
                "email": "elena.martinez@student.university.com",
                "login": "elenamartinez",
                "password": "student2024",
                "role": "STUDENT",
                "department": "Computer Science",
                "year": "3rd Year",
                "gpa": "3.8"
            },
            {
                "firstName": "David",
                "lastName": "Kim",
                "email": "david.kim@student.university.com",
                "login": "davidkim",
                "password": "student2024secure",
                "role": "STUDENT",
                "department": "Engineering",
                "year": "2nd Year", 
                "gpa": "3.6"
            },
            {
                "firstName": "Lisa",
                "lastName": "Thompson",
                "email": "lisa.thompson@student.university.com",
                "login": "lisathompson",
                "password": "mystudentpass",
                "role": "STUDENT",
                "department": "Mathematics",
                "year": "1st Year",
                "gpa": "3.9"
            }
        ]
        
        print(f"\nRegistering {len(enhanced_test_users)} users with department assignments...")
        
        created_users = []
        for user_data in enhanced_test_users:
            try:
                # Prepare registration payload (only include API-required fields)
                registration_payload = {
                    "firstName": user_data["firstName"],
                    "lastName": user_data["lastName"],
                    "email": user_data["email"],
                    "login": user_data["login"],
                    "password": user_data["password"],
                    "role": user_data["role"]
                }
                
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json=registration_payload
                )
                
                print(f"\n👤 Registering {user_data['role']}: {user_data['firstName']} {user_data['lastName']}")
                print(f"   📧 Email: {user_data['email']}")
                print(f"   🏢 Department: {user_data['department']}")
                
                if user_data['role'] == 'TEACHER':
                    print(f"   🎓 Specialization: {user_data.get('specialization', 'N/A')}")
                    print(f"   📊 Experience: {user_data.get('experience', 'N/A')}")
                elif user_data['role'] == 'STUDENT':
                    print(f"   📚 Academic Year: {user_data.get('year', 'N/A')}")
                    print(f"   📈 GPA: {user_data.get('gpa', 'N/A')}")
                
                print(f"   ⏰ Status: {response.status_code}")
                
                if response.status_code == 200:
                    user_response = response.json()
                    print(f"   ✅ Successfully registered!")
                    created_users.append(user_response)
                    
                    # Save admin user ID for later use
                    if user_data['role'] == 'ADMIN':
                        self.user_id = user_response['id']
                else:
                    error_detail = response.json()
                    print(f"   ❌ Registration failed: {error_detail}")
                    
            except Exception as e:
                print(f"   ❌ Error registering {user_data['login']}: {e}")
        
        print(f"\n📊 Registration Summary: {len(created_users)} users successfully registered")
        return len(created_users) > 0
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        print("\n🏠 Testing Root Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("\n🏥 Testing Health Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration with department selection"""
        print("\n👤 Testing User Registration...")
        
        # First, create some departments for user registration
        self.setup_departments_for_registration()
        
        test_users = [
            {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@university.com",
                "login": "johndoe",
                "password": "securepassword123",
                "role": "ADMIN"
            },
            {
                "firstName": "Jane",
                "lastName": "Smith", 
                "email": "jane.smith@university.com",
                "login": "janesmith",
                "password": "securepassword456",
                "role": "DEPARTMENT_HEAD"
            },
            {
                "firstName": "Dr. Michael",
                "lastName": "Brown",
                "email": "michael.brown@university.com", 
                "login": "michaelbrown",
                "password": "teacherpass123",
                "role": "TEACHER"
            },
            {
                "firstName": "Sarah",
                "lastName": "Davis",
                "email": "sarah.davis@university.com",
                "login": "sarahdavis", 
                "password": "teacherpass456",
                "role": "TEACHER"
            },
            {
                "firstName": "Alice",
                "lastName": "Wilson",
                "email": "alice.wilson@university.com",
                "login": "alicewilson", 
                "password": "studentpass123",
                "role": "STUDENT"
            },
            {
                "firstName": "Bob",
                "lastName": "Johnson",
                "email": "bob.johnson@university.com",
                "login": "bobjohnson", 
                "password": "studentpass456",
                "role": "STUDENT"
            },
            {
                "firstName": "Emma",
                "lastName": "Garcia",
                "email": "emma.garcia@university.com",
                "login": "emmagarcia", 
                "password": "studentpass789",
                "role": "STUDENT"
            }
        ]
        
        created_users = []
        for user_data in test_users:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json=user_data
                )
                print(f"Creating {user_data['role']}: {response.status_code}")
                if response.status_code == 200:
                    user_response = response.json()
                    print(f"✅ Created user: {user_response['firstName']} {user_response['lastName']} ({user_response['role']})")
                    created_users.append(user_response)
                    
                    # Save admin user ID for later use
                    if user_data['role'] == 'ADMIN':
                        self.user_id = user_response['id']
                else:
                    print(f"❌ Failed to create user: {response.json()}")
            except Exception as e:
                print(f"❌ Error creating user {user_data['login']}: {e}")
        
        return len(created_users) > 0
    
    def test_user_login(self):
        """Test user login and get access token"""
        print("\n🔐 Testing User Login...")
        
        login_data = {
            "login": "johndoe",
            "password": "securepassword123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            print(f"Login Status: {response.status_code}")
            
            if response.status_code == 200:
                token_response = response.json()
                self.access_token = token_response["access_token"]
                self.set_auth_header()
                print(f"✅ Login successful! Token obtained.")
                print(f"Access Token: {self.access_token[:50]}...")
                return True
            else:
                print(f"❌ Login failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def test_get_current_user(self):
        """Test getting current user info"""
        print("\n👤 Testing Get Current User...")
        
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Current user: {user_info['firstName']} {user_info['lastName']} ({user_info['role']})")
                return True
            else:
                print(f"❌ Failed to get user info: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return False
    
    def test_get_users(self):
        """Test getting all users"""
        print("\n📋 Testing Get All Users...")
        
        try:
            response = self.session.get(f"{self.base_url}/auth/users")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Retrieved {len(users)} users")
                for user in users[:3]:  # Show first 3 users
                    print(f"   - {user['firstName']} {user['lastName']} ({user['role']})")
                return True
            else:
                print(f"❌ Failed to get users: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return False
    
    def test_create_department(self):
        """Test creating departments"""
        print("\n🏢 Testing Create Department...")
        
        departments = [
            {"name": "Computer Science"},
            {"name": "Mathematics"},
            {"name": "Physics"},
            {"name": "Engineering"}
        ]
        
        created_departments = []
        for dept_data in departments:
            try:
                response = self.session.post(
                    f"{self.base_url}/departments/",
                    json=dept_data
                )
                print(f"Creating {dept_data['name']}: {response.status_code}")
                
                if response.status_code == 200:
                    dept_response = response.json()
                    print(f"✅ Created department: {dept_response['name']}")
                    created_departments.append(dept_response)
                else:
                    print(f"❌ Failed to create department: {response.json()}")
            except Exception as e:
                print(f"❌ Error creating department {dept_data['name']}: {e}")
        
        return len(created_departments) > 0
    
    def test_get_departments(self):
        """Test getting all departments"""
        print("\n🏢 Testing Get Departments...")
        
        try:
            response = self.session.get(f"{self.base_url}/departments/")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                departments = response.json()
                print(f"✅ Retrieved {len(departments)} departments")
                for dept in departments:
                    print(f"   - {dept['name']} (ID: {dept['id']})")
                return departments
            else:
                print(f"❌ Failed to get departments: {response.json()}")
                return []
        except Exception as e:
            print(f"❌ Error getting departments: {e}")
            return []
    
    def test_create_specialty(self, departments):
        """Test creating specialties"""
        print("\n🎓 Testing Create Specialty...")
        
        if not departments:
            print("❌ No departments available for specialty creation")
            return False
        
        # Create specialties for the first department
        dept_id = departments[0]['id']
        specialties = [
            {"name": "Artificial Intelligence", "departmentId": dept_id},
            {"name": "Software Engineering", "departmentId": dept_id},
            {"name": "Data Science", "departmentId": dept_id}
        ]
        
        created_specialties = []
        for spec_data in specialties:
            try:
                response = self.session.post(
                    f"{self.base_url}/specialties/",
                    json=spec_data
                )
                print(f"Creating {spec_data['name']}: {response.status_code}")
                
                if response.status_code == 200:
                    spec_response = response.json()
                    print(f"✅ Created specialty: {spec_response['name']}")
                    created_specialties.append(spec_response)
                else:
                    print(f"❌ Failed to create specialty: {response.json()}")
            except Exception as e:
                print(f"❌ Error creating specialty {spec_data['name']}: {e}")
        
        return len(created_specialties) > 0
    
    def test_get_specialties(self):
        """Test getting all specialties"""
        print("\n🎓 Testing Get Specialties...")
        
        try:
            response = self.session.get(f"{self.base_url}/specialties/")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                specialties = response.json()
                print(f"✅ Retrieved {len(specialties)} specialties")
                for spec in specialties:
                    dept_name = spec.get('department', {}).get('name', 'Unknown')
                    print(f"   - {spec['name']} (Department: {dept_name})")
                return True
            else:
                print(f"❌ Failed to get specialties: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Error getting specialties: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests with enhanced registration"""
        print("🚀 Starting Enhanced University Management API Tests")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 10
        
        # Basic endpoint tests
        if self.test_root_endpoint():
            tests_passed += 1
            
        if self.test_health_endpoint():
            tests_passed += 1
        
        # Enhanced authentication flow
        if self.test_user_registration():
            tests_passed += 1
            
        if self.test_enhanced_user_registration():
            tests_passed += 1
            
        if self.test_user_login():
            tests_passed += 1
            
        if self.test_get_current_user():
            tests_passed += 1
            
        if self.test_get_users():
            tests_passed += 1
        
        # Department and specialty management
        if self.test_create_department():
            tests_passed += 1
            
        departments = self.test_get_departments()
        if departments:
            if self.test_create_specialty(departments):
                tests_passed += 1
        
        if self.test_get_specialties():
            tests_passed += 1
        
        # Test summary
        print("\n" + "=" * 60)
        print(f"🏁 Enhanced Test Summary: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All enhanced tests passed! API with department selection is working correctly!")
        else:
            print(f"⚠️ {total_tests - tests_passed} tests failed. Check the output above.")
        
        return tests_passed == total_tests


def main():
    """Main function to run API tests"""
    print("🎓 University Management API Tester")
    print("===================================")
    
    tester = APITester(BASE_URL)
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print(f"📖 API Documentation available at: {BASE_URL}/docs")
        print(f"🔧 ReDoc available at: {BASE_URL}/redoc")
    else:
        print("\n❌ Some tests failed. Please check the API server.")


if __name__ == "__main__":
    main()