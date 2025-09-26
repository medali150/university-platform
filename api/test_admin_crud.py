#!/usr/bin/env python3
"""
Comprehensive Admin CRUD Operations Test Suite
Tests all admin functionalities for managing students, teachers, and department heads
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional


class AdminCRUDTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.test_data = {}
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_subsection(self, title: str):
        """Print a formatted subsection header"""
        print(f"\n{'-'*40}")
        print(f" {title}")
        print(f"{'-'*40}")
    
    def setup_admin_auth(self):
        """Setup admin authentication"""
        self.print_section("ADMIN AUTHENTICATION SETUP")
        
        # Login as admin
        admin_credentials = {
            "login": "admin",
            "password": "admin123"
        }
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json=admin_credentials
        )
        
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.admin_token}"
            })
            print(f"✅ Admin authentication successful")
            print(f"   Token: {self.admin_token[:50]}...")
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        return True
    
    def setup_test_data(self):
        """Setup required test data (departments, specialties, etc.)"""
        self.print_section("TEST DATA SETUP")
        
        # Create faculty
        faculty_data = {
            "name": "Faculty of Engineering",
            "description": "Engineering disciplines and technology"
        }
        
        response = self.session.post(
            f"{self.base_url}/admin/faculties/",
            json=faculty_data
        )
        
        if response.status_code == 201:
            self.test_data["faculty"] = response.json()
            print(f"✅ Faculty created: {self.test_data['faculty']['name']}")
        else:
            print(f"ℹ️  Faculty might already exist, continuing...")
            # Try to get existing faculty
            response = self.session.get(f"{self.base_url}/faculties/")
            if response.status_code == 200:
                faculties = response.json()
                if faculties:
                    self.test_data["faculty"] = faculties[0]
                    print(f"✅ Using existing faculty: {self.test_data['faculty']['name']}")
        
        # Create department
        dept_data = {
            "name": "Computer Science Department",
            "description": "Computer Science and Software Engineering",
            "facultyId": self.test_data["faculty"]["id"]
        }
        
        response = self.session.post(
            f"{self.base_url}/admin/departments/",
            json=dept_data
        )
        
        if response.status_code == 201:
            self.test_data["department"] = response.json()
            print(f"✅ Department created: {self.test_data['department']['name']}")
        else:
            print(f"ℹ️  Department might already exist, continuing...")
            # Try to get existing department
            response = self.session.get(f"{self.base_url}/departments/")
            if response.status_code == 200:
                departments = response.json()
                if departments:
                    self.test_data["department"] = departments[0]
                    print(f"✅ Using existing department: {self.test_data['department']['name']}")
        
        # Create specialty
        specialty_data = {
            "name": "Software Engineering",
            "description": "Software development and engineering practices",
            "departmentId": self.test_data["department"]["id"]
        }
        
        response = self.session.post(
            f"{self.base_url}/admin/specialties/",
            json=specialty_data
        )
        
        if response.status_code == 201:
            self.test_data["specialty"] = response.json()
            print(f"✅ Specialty created: {self.test_data['specialty']['name']}")
        else:
            print(f"ℹ️  Specialty might already exist, continuing...")
            # Try to get existing specialty
            response = self.session.get(f"{self.base_url}/specialties/")
            if response.status_code == 200:
                specialties = response.json()
                if specialties:
                    self.test_data["specialty"] = specialties[0]
                    print(f"✅ Using existing specialty: {self.test_data['specialty']['name']}")
    
    def test_student_crud(self):
        """Test complete Student CRUD operations"""
        self.print_section("STUDENT CRUD OPERATIONS")
        
        # CREATE STUDENT
        self.print_subsection("CREATE STUDENT")
        student_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe.student@university.com",
            "login": "john.doe.student",
            "password": "student123",
            "role": "STUDENT"
        }
        
        url = f"{self.base_url}/admin/students/"
        if "specialty" in self.test_data:
            url += f"?specialty_id={self.test_data['specialty']['id']}"
        
        response = self.session.post(url, json=student_data)
        
        if response.status_code in [200, 201]:
            student = response.json()
            self.test_data["test_student"] = student
            print(f"✅ Student created successfully")
            print(f"   ID: {student['id']}")
            print(f"   Name: {student['firstName']} {student['lastName']}")
            print(f"   Email: {student['email']}")
        else:
            print(f"❌ Failed to create student: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # GET ALL STUDENTS
        self.print_subsection("GET ALL STUDENTS")
        response = self.session.get(f"{self.base_url}/admin/students/")
        
        if response.status_code == 200:
            students = response.json()
            print(f"✅ Retrieved {len(students)} students")
            for i, student in enumerate(students[:3]):  # Show first 3
                print(f"   {i+1}. {student.get('firstName', 'N/A')} {student.get('lastName', 'N/A')} - {student.get('email', 'N/A')}")
        else:
            print(f"❌ Failed to get students: {response.status_code}")
        
        # GET STUDENT BY ID
        if "test_student" in self.test_data:
            self.print_subsection("GET STUDENT BY ID")
            student_id = self.test_data["test_student"]["id"]
            response = self.session.get(f"{self.base_url}/admin/students/{student_id}")
            
            if response.status_code == 200:
                student = response.json()
                print(f"✅ Retrieved student by ID")
                print(f"   Name: {student['firstName']} {student['lastName']}")
                print(f"   Role: {student['role']}")
                if "studentInfo" in student:
                    print(f"   Student Info: {student['studentInfo']}")
            else:
                print(f"❌ Failed to get student: {response.status_code}")
    
    def test_teacher_crud(self):
        """Test complete Teacher CRUD operations"""
        self.print_section("TEACHER CRUD OPERATIONS")
        
        # CREATE TEACHER
        self.print_subsection("CREATE TEACHER")
        teacher_data = {
            "firstName": "Dr. Jane",
            "lastName": "Smith",
            "email": "jane.smith.teacher@university.com",
            "login": "jane.smith.teacher",
            "password": "teacher123",
            "role": "TEACHER"
        }
        
        url = f"{self.base_url}/admin/teachers/"
        params = []
        if "department" in self.test_data:
            params.append(f"department_id={self.test_data['department']['id']}")
        params.append("academic_title=Professor")
        params.append("years_of_experience=15")
        
        if params:
            url += "?" + "&".join(params)
        
        response = self.session.post(url, json=teacher_data)
        
        if response.status_code in [200, 201]:
            teacher = response.json()
            self.test_data["test_teacher"] = teacher
            print(f"✅ Teacher created successfully")
            print(f"   ID: {teacher['id']}")
            print(f"   Name: {teacher['firstName']} {teacher['lastName']}")
            print(f"   Email: {teacher['email']}")
        else:
            print(f"❌ Failed to create teacher: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # GET ALL TEACHERS
        self.print_subsection("GET ALL TEACHERS")
        response = self.session.get(f"{self.base_url}/admin/teachers/")
        
        if response.status_code == 200:
            teachers = response.json()
            print(f"✅ Retrieved {len(teachers)} teachers")
            for i, teacher in enumerate(teachers[:3]):  # Show first 3
                print(f"   {i+1}. {teacher.get('firstName', 'N/A')} {teacher.get('lastName', 'N/A')} - {teacher.get('email', 'N/A')}")
        else:
            print(f"❌ Failed to get teachers: {response.status_code}")
        
        # GET TEACHER BY ID
        if "test_teacher" in self.test_data:
            self.print_subsection("GET TEACHER BY ID")
            teacher_id = self.test_data["test_teacher"]["id"]
            response = self.session.get(f"{self.base_url}/admin/teachers/{teacher_id}")
            
            if response.status_code == 200:
                teacher = response.json()
                print(f"✅ Retrieved teacher by ID")
                print(f"   Name: {teacher['firstName']} {teacher['lastName']}")
                print(f"   Role: {teacher['role']}")
                if "teacherInfo" in teacher:
                    print(f"   Teacher Info: {teacher['teacherInfo']}")
            else:
                print(f"❌ Failed to get teacher: {response.status_code}")
    
    def test_department_head_crud(self):
        """Test complete Department Head CRUD operations"""
        self.print_section("DEPARTMENT HEAD CRUD OPERATIONS")
        
        # CREATE DEPARTMENT HEAD
        self.print_subsection("CREATE DEPARTMENT HEAD")
        dept_head_data = {
            "firstName": "Prof. Robert",
            "lastName": "Johnson",
            "email": "robert.johnson.head@university.com",
            "login": "robert.johnson.head",
            "password": "head123",
            "role": "DEPARTMENT_HEAD"
        }
        
        url = f"{self.base_url}/admin/department-heads/"
        if "department" in self.test_data:
            url += f"?department_id={self.test_data['department']['id']}"
            url += f"&appointment_date={datetime.now().strftime('%Y-%m-%d')}"
        
        response = self.session.post(url, json=dept_head_data)
        
        if response.status_code in [200, 201]:
            dept_head = response.json()
            self.test_data["test_dept_head"] = dept_head
            print(f"✅ Department Head created successfully")
            print(f"   ID: {dept_head['id']}")
            print(f"   Name: {dept_head['firstName']} {dept_head['lastName']}")
            print(f"   Email: {dept_head['email']}")
        else:
            print(f"❌ Failed to create department head: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # GET ALL DEPARTMENT HEADS
        self.print_subsection("GET ALL DEPARTMENT HEADS")
        response = self.session.get(f"{self.base_url}/admin/department-heads/")
        
        if response.status_code == 200:
            dept_heads = response.json()
            print(f"✅ Retrieved {len(dept_heads)} department heads")
            for i, head in enumerate(dept_heads[:3]):  # Show first 3
                print(f"   {i+1}. {head.get('firstName', 'N/A')} {head.get('lastName', 'N/A')} - {head.get('email', 'N/A')}")
        else:
            print(f"❌ Failed to get department heads: {response.status_code}")
    
    def test_admin_dashboard(self):
        """Test Admin Dashboard functionality"""
        self.print_section("ADMIN DASHBOARD")
        
        # GET STATISTICS
        self.print_subsection("DASHBOARD STATISTICS")
        response = self.session.get(f"{self.base_url}/admin/dashboard/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Retrieved dashboard statistics")
            print(f"   Total Users: {stats.get('overview', {}).get('totalUsers', 0)}")
            print(f"   Total Students: {stats.get('overview', {}).get('totalStudents', 0)}")
            print(f"   Total Teachers: {stats.get('overview', {}).get('totalTeachers', 0)}")
            print(f"   Total Dept Heads: {stats.get('overview', {}).get('totalDepartmentHeads', 0)}")
            
            if "roleDistribution" in stats:
                print(f"   Role Distribution: {stats['roleDistribution']}")
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
        
        # GET RECENT ACTIVITY
        self.print_subsection("RECENT ACTIVITY")
        response = self.session.get(f"{self.base_url}/admin/dashboard/recent-activity?limit=5")
        
        if response.status_code == 200:
            activity = response.json()
            print(f"✅ Retrieved recent activity")
            print(f"   Recent registrations: {activity.get('totalRecentUsers', 0)}")
        else:
            print(f"❌ Failed to get recent activity: {response.status_code}")
        
        # GET SYSTEM HEALTH
        self.print_subsection("SYSTEM HEALTH")
        response = self.session.get(f"{self.base_url}/admin/dashboard/system-health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Retrieved system health")
            print(f"   Database Status: {health.get('database', {}).get('status', 'unknown')}")
            print(f"   Data Integrity: {health.get('dataIntegrity', {}).get('status', 'unknown')}")
            
            inconsistencies = health.get('dataIntegrity', {}).get('inconsistencies', [])
            if inconsistencies:
                print(f"   Found {len(inconsistencies)} inconsistencies:")
                for inc in inconsistencies:
                    print(f"     - {inc.get('description', 'Unknown issue')}")
        else:
            print(f"❌ Failed to get system health: {response.status_code}")
        
        # SEARCH USERS
        self.print_subsection("USER SEARCH")
        response = self.session.get(f"{self.base_url}/admin/dashboard/search?query=john&limit=10")
        
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search completed")
            print(f"   Found {search_results.get('count', 0)} results for 'john'")
            
            results = search_results.get('results', [])
            for i, user in enumerate(results[:3]):
                print(f"   {i+1}. {user.get('firstName', '')} {user.get('lastName', '')} ({user.get('role', '')})")
        else:
            print(f"❌ Failed to search users: {response.status_code}")
    
    def display_swagger_examples(self):
        """Display Swagger UI testing examples"""
        self.print_section("SWAGGER UI TESTING EXAMPLES")
        
        print("🌐 Open Swagger UI at: http://127.0.0.1:8000/docs")
        print("\n📋 Test the following endpoints with these examples:")
        
        # Student creation example
        print("\n1️⃣  CREATE STUDENT - POST /admin/students/")
        student_example = {
            "firstName": "Alice",
            "lastName": "Wonder",
            "email": "alice.wonder@university.com", 
            "login": "alice.wonder",
            "password": "student123",
            "role": "STUDENT"
        }
        print("   JSON Body:")
        print(f"   {json.dumps(student_example, indent=3)}")
        print("   Query Parameters: specialty_id, level_id, group_id")
        
        # Teacher creation example
        print("\n2️⃣  CREATE TEACHER - POST /admin/teachers/")
        teacher_example = {
            "firstName": "Dr. Michael",
            "lastName": "Thompson",
            "email": "michael.thompson@university.com",
            "login": "michael.thompson", 
            "password": "teacher123",
            "role": "TEACHER"
        }
        print("   JSON Body:")
        print(f"   {json.dumps(teacher_example, indent=3)}")
        print("   Query Parameters: department_id, academic_title, years_of_experience")
        
        # Department Head creation example
        print("\n3️⃣  CREATE DEPARTMENT HEAD - POST /admin/department-heads/")
        dept_head_example = {
            "firstName": "Prof. Sarah",
            "lastName": "Wilson",
            "email": "sarah.wilson@university.com",
            "login": "sarah.wilson",
            "password": "head123", 
            "role": "DEPARTMENT_HEAD"
        }
        print("   JSON Body:")
        print(f"   {json.dumps(dept_head_example, indent=3)}")
        print("   Query Parameters: department_id (required), appointment_date")
        
        print("\n4️⃣  ADMIN DASHBOARD - GET /admin/dashboard/statistics")
        print("   No body required - returns comprehensive statistics")
        
        print("\n🔑 Don't forget to:")
        print("   1. Login as admin first: POST /auth/login")
        print("   2. Copy the access_token from login response")
        print("   3. Click 'Authorize' button in Swagger UI")
        print("   4. Enter: Bearer YOUR_ACCESS_TOKEN")
    
    def run_all_tests(self):
        """Run all admin CRUD tests"""
        print("🎓 University Admin CRUD Operations Test Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Cannot proceed without admin authentication")
            return
        
        self.setup_test_data()
        
        # Run tests
        self.test_student_crud()
        self.test_teacher_crud()
        self.test_department_head_crud()
        self.test_admin_dashboard()
        
        # Display Swagger examples
        self.display_swagger_examples()
        
        self.print_section("TEST SUMMARY")
        print("✅ Admin CRUD test suite completed!")
        print("📊 Check the admin dashboard at: http://127.0.0.1:8000/admin/dashboard/statistics")
        print("📚 Full API documentation: http://127.0.0.1:8000/docs")


def main():
    """Main function to run the admin CRUD tests"""
    tester = AdminCRUDTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()