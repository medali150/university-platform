"""
Comprehensive Backend API Test Suite
Tests all available backend APIs including authentication, CRUD operations, and admin functions
"""

import requests
import json
from datetime import datetime
import asyncio
import time

BASE_URL = "http://127.0.0.1:8000"

class APITester:
    def __init__(self):
        self.admin_token = None
        self.test_data = {}
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        symbol = "✅" if status else "❌"
        print(f"   {symbol} {test_name}")
        if details:
            print(f"      {details}")
        
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "details": details
        })
        
        if status:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
    
    def test_basic_endpoints(self):
        """Test basic system endpoints"""
        print("\n🔧 Testing Basic System Endpoints")
        print("=" * 50)
        
        # Test root endpoint
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root endpoint", True, f"Message: {data.get('message', 'N/A')}")
            else:
                self.log_test("Root endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Root endpoint", False, f"Error: {str(e)}")
        
        # Test health endpoint
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status') == 'healthy'
                self.log_test("Health endpoint", status, f"Database: {data.get('database')}, Users: {data.get('users_count')}")
            else:
                self.log_test("Health endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health endpoint", False, f"Error: {str(e)}")
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication")
        print("=" * 50)
        
        # Test admin login
        login_data = {
            "login": "mohamedali.gh15@gmail.com",
            "password": "daligh15"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_test("Admin login", True, "Token received")
            else:
                self.log_test("Admin login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin login", False, f"Error: {str(e)}")
            return False
        
        # Test /auth/me endpoint
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            try:
                response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Get current user", True, f"User: {data.get('firstName')} {data.get('lastName')}")
                else:
                    self.log_test("Get current user", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get current user", False, f"Error: {str(e)}")
        
        # Test get all users
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            try:
                response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Get all users", True, f"Found {len(data)} users")
                else:
                    self.log_test("Get all users", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get all users", False, f"Error: {str(e)}")
        
        # Test user registration
        register_data = {
            "firstName": "Test",
            "lastName": "User",
            "email": "test.user@university.com",
            "login": "testuser",
            "password": "testpass123",
            "role": "STUDENT"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                data = response.json()
                self.test_data["test_user_id"] = data.get("id")
                self.log_test("User registration", True, f"User ID: {data.get('id')}")
            else:
                self.log_test("User registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("User registration", False, f"Error: {str(e)}")
        
        return True
    
    def test_departments_api(self):
        """Test departments API"""
        print("\n🏛️ Testing Departments API")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Departments API", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get departments
        try:
            response = requests.get(f"{BASE_URL}/departments/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get departments", True, f"Found {len(data)} departments")
                if data:
                    self.test_data["department_id"] = data[0].get("id")
            else:
                self.log_test("Get departments", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get departments", False, f"Error: {str(e)}")
    
    def test_specialties_api(self):
        """Test specialties API"""
        print("\n📚 Testing Specialties API")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Specialties API", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get specialties
        try:
            response = requests.get(f"{BASE_URL}/specialties/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get specialties", True, f"Found {len(data)} specialties")
                if data:
                    self.test_data["specialty_id"] = data[0].get("id")
            else:
                self.log_test("Get specialties", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get specialties", False, f"Error: {str(e)}")
    
    def test_students_crud(self):
        """Test students CRUD API"""
        print("\n👨‍🎓 Testing Students CRUD")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Students CRUD", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get students
        try:
            response = requests.get(f"{BASE_URL}/admin/students/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log_test("Get students", True, f"Found {total} students")
                if data.get("students"):
                    self.test_data["student_id"] = data["students"][0].get("id")
            else:
                self.log_test("Get students", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get students", False, f"Error: {str(e)}")
        
        # Test get single student
        if self.test_data.get("student_id"):
            try:
                student_id = self.test_data["student_id"]
                response = requests.get(f"{BASE_URL}/admin/students/{student_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    name = f"{data.get('user', {}).get('firstName', '')} {data.get('user', {}).get('lastName', '')}"
                    self.log_test("Get single student", True, f"Student: {name}")
                else:
                    self.log_test("Get single student", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get single student", False, f"Error: {str(e)}")
    
    def test_teachers_crud(self):
        """Test teachers CRUD API"""
        print("\n👨‍🏫 Testing Teachers CRUD")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Teachers CRUD", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get teachers
        try:
            response = requests.get(f"{BASE_URL}/admin/teachers/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log_test("Get teachers", True, f"Found {total} teachers")
                if data.get("teachers"):
                    self.test_data["teacher_id"] = data["teachers"][0].get("id")
            else:
                self.log_test("Get teachers", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get teachers", False, f"Error: {str(e)}")
        
        # Test get single teacher
        if self.test_data.get("teacher_id"):
            try:
                teacher_id = self.test_data["teacher_id"]
                response = requests.get(f"{BASE_URL}/admin/teachers/{teacher_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    name = f"{data.get('user', {}).get('firstName', '')} {data.get('user', {}).get('lastName', '')}"
                    self.log_test("Get single teacher", True, f"Teacher: {name}")
                else:
                    self.log_test("Get single teacher", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get single teacher", False, f"Error: {str(e)}")
    
    def test_department_heads_crud(self):
        """Test department heads CRUD API"""
        print("\n👨‍💼 Testing Department Heads CRUD")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Department Heads CRUD", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get department heads
        try:
            response = requests.get(f"{BASE_URL}/admin/department-heads/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log_test("Get department heads", True, f"Found {total} department heads")
                if data.get("departmentHeads"):
                    self.test_data["dept_head_id"] = data["departmentHeads"][0].get("id")
            else:
                self.log_test("Get department heads", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get department heads", False, f"Error: {str(e)}")
    
    def test_levels_crud(self):
        """Test levels CRUD API"""
        print("\n📈 Testing Levels CRUD")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Levels CRUD", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get levels
        try:
            response = requests.get(f"{BASE_URL}/admin/levels/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log_test("Get levels", True, f"Found {total} levels")
                if data.get("levels"):
                    self.test_data["level_id"] = data["levels"][0].get("id")
            else:
                self.log_test("Get levels", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get levels", False, f"Error: {str(e)}")
        
        # Test get single level
        if self.test_data.get("level_id"):
            try:
                level_id = self.test_data["level_id"]
                response = requests.get(f"{BASE_URL}/admin/levels/{level_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    name = data.get("name", "Unknown")
                    self.log_test("Get single level", True, f"Level: {name}")
                else:
                    self.log_test("Get single level", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get single level", False, f"Error: {str(e)}")
    
    def test_subjects_crud(self):
        """Test subjects CRUD API"""
        print("\n📖 Testing Subjects CRUD")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Subjects CRUD", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get subjects
        try:
            response = requests.get(f"{BASE_URL}/admin/subjects/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                self.log_test("Get subjects", True, f"Found {total} subjects")
            else:
                self.log_test("Get subjects", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get subjects", False, f"Error: {str(e)}")
        
        # Test helper endpoints
        try:
            response = requests.get(f"{BASE_URL}/admin/subjects/helpers/levels", headers=headers)
            if response.status_code == 200:
                data = response.json()
                levels = data.get("levels", [])
                self.log_test("Get levels helper", True, f"Found {len(levels)} levels")
                if levels:
                    self.test_data["helper_level_id"] = levels[0].get("id")
            else:
                self.log_test("Get levels helper", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get levels helper", False, f"Error: {str(e)}")
        
        try:
            response = requests.get(f"{BASE_URL}/admin/subjects/helpers/teachers", headers=headers)
            if response.status_code == 200:
                data = response.json()
                teachers = data.get("teachers", [])
                self.log_test("Get teachers helper", True, f"Found {len(teachers)} teachers")
                if teachers:
                    self.test_data["helper_teacher_id"] = teachers[0].get("id")
            else:
                self.log_test("Get teachers helper", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get teachers helper", False, f"Error: {str(e)}")
        
        # Test create subject
        if self.test_data.get("helper_level_id") and self.test_data.get("helper_teacher_id"):
            create_data = {
                "name": "Test Mathematics Course",
                "levelId": self.test_data["helper_level_id"],
                "teacherId": self.test_data["helper_teacher_id"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/admin/subjects/", json=create_data, headers=headers)
                if response.status_code == 201:
                    data = response.json()
                    subject_id = data.get("id")
                    self.test_data["test_subject_id"] = subject_id
                    self.log_test("Create subject", True, f"Subject ID: {subject_id}")
                else:
                    self.log_test("Create subject", False, f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test("Create subject", False, f"Error: {str(e)}")
        
        # Test update subject
        if self.test_data.get("test_subject_id"):
            update_data = {"name": "Advanced Mathematics Course"}
            
            try:
                subject_id = self.test_data["test_subject_id"]
                response = requests.put(f"{BASE_URL}/admin/subjects/{subject_id}", json=update_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Update subject", True, f"New name: {data.get('name')}")
                else:
                    self.log_test("Update subject", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Update subject", False, f"Error: {str(e)}")
        
        # Test delete subject
        if self.test_data.get("test_subject_id"):
            try:
                subject_id = self.test_data["test_subject_id"]
                response = requests.delete(f"{BASE_URL}/admin/subjects/{subject_id}", headers=headers)
                if response.status_code == 204:
                    self.log_test("Delete subject", True, "Subject deleted successfully")
                else:
                    self.log_test("Delete subject", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Delete subject", False, f"Error: {str(e)}")
    
    def test_admin_dashboard(self):
        """Test admin dashboard API"""
        print("\n📊 Testing Admin Dashboard")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Admin Dashboard", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test dashboard stats
        try:
            response = requests.get(f"{BASE_URL}/admin/dashboard/stats", headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Dashboard stats", True, f"Users: {data.get('users')}, Departments: {data.get('departments')}")
            else:
                self.log_test("Dashboard stats", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Dashboard stats", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🚫 Testing Error Handling")
        print("=" * 50)
        
        # Test unauthorized access
        try:
            response = requests.get(f"{BASE_URL}/admin/students/")
            if response.status_code == 401:
                self.log_test("Unauthorized access", True, "Correctly denied access without token")
            else:
                self.log_test("Unauthorized access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Unauthorized access", False, f"Error: {str(e)}")
        
        # Test invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        try:
            response = requests.get(f"{BASE_URL}/admin/students/", headers=invalid_headers)
            if response.status_code == 401:
                self.log_test("Invalid token", True, "Correctly rejected invalid token")
            else:
                self.log_test("Invalid token", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid token", False, f"Error: {str(e)}")
        
        # Test non-existent endpoint
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            try:
                response = requests.get(f"{BASE_URL}/non-existent-endpoint", headers=headers)
                if response.status_code == 404:
                    self.log_test("Non-existent endpoint", True, "Correctly returned 404")
                else:
                    self.log_test("Non-existent endpoint", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Non-existent endpoint", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE API TEST SUMMARY")
        print("=" * 70)
        
        total_tests = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Pass Rate: {pass_rate:.1f}%")
        
        if self.results["failed"] > 0:
            print(f"\n⚠️  Failed Tests:")
            for test in self.results["tests"]:
                if not test["status"]:
                    print(f"   ❌ {test['name']}: {test['details']}")
        
        print(f"\n🎯 API Status: {'🟢 HEALTHY' if pass_rate >= 80 else '🟡 NEEDS ATTENTION' if pass_rate >= 60 else '🔴 CRITICAL'}")
        
        if pass_rate >= 90:
            print("🎉 Excellent! Your backend API is working perfectly!")
        elif pass_rate >= 80:
            print("✨ Great! Your backend API is working well with minor issues.")
        elif pass_rate >= 60:
            print("⚠️  Good, but there are some issues that need attention.")
        else:
            print("🚨 Critical issues detected. Please review and fix the failing tests.")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive Backend API Testing")
        print("Make sure the FastAPI server is running on http://127.0.0.1:8000")
        print()
        
        # Check if server is running
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print("❌ Server is not healthy. Please start the FastAPI server first.")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Please start the FastAPI server first:")
            print("cd api && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
            return
        
        # Run all test suites
        self.test_basic_endpoints()
        if self.test_authentication():  # Only continue if authentication works
            self.test_departments_api()
            self.test_specialties_api()
            self.test_students_crud()
            self.test_teachers_crud()
            self.test_department_heads_crud()
            self.test_levels_crud()
            self.test_subjects_crud()
            self.test_admin_dashboard()
            self.test_error_handling()
        
        self.print_summary()


def main():
    """Main function to run all tests"""
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()