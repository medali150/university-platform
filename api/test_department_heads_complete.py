#!/usr/bin/env python3
"""
Comprehensive Department Heads CRUD Test
Tests all fixed CRUD operations for department heads
"""

import requests
import json
import time
from datetime import datetime

class DepartmentHeadsCRUDTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.test_data = {}
        
    def print_section(self, title: str):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_subsection(self, title: str):
        """Print formatted subsection header"""
        print(f"\n{'-'*40}")
        print(f" {title}")
        print(f"{'-'*40}")
    
    def setup_admin_auth(self):
        """Setup admin authentication"""
        self.print_section("ADMIN AUTHENTICATION")
        
        # Try existing admin first
        admin_credentials = {"login": "admin", "password": "admin123"}
        
        response = self.session.post(f"{self.base_url}/auth/login", json=admin_credentials)
        
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
            print("✅ Admin authentication successful")
            return True
        
        # Try to create admin if login failed
        admin_data = {
            "firstName": "System",
            "lastName": "Administrator",
            "email": "admin@university.com",
            "login": "admin",
            "password": "admin123",
            "role": "ADMIN"
        }
        
        register_response = self.session.post(f"{self.base_url}/auth/register", json=admin_data)
        
        if register_response.status_code in [200, 201]:
            print("✅ Admin user created successfully")
            # Try login again
            response = self.session.post(f"{self.base_url}/auth/login", json=admin_credentials)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                print("✅ Admin login successful after creation")
                return True
        
        print(f"❌ Failed to setup admin authentication")
        return False
    
    def setup_test_department(self):
        """Create a test department if needed"""
        self.print_subsection("Setup Test Department")
        
        dept_data = {
            "name": "Computer Science Test Department",
            "description": "Test department for CRUD operations"
        }
        
        # Try to create department
        response = self.session.post(f"{self.base_url}/admin/departments/", json=dept_data)
        
        if response.status_code in [200, 201]:
            self.test_data["department"] = response.json()
            print(f"✅ Test department created: {self.test_data['department']['name']}")
        else:
            # Try to get existing departments
            response = self.session.get(f"{self.base_url}/departments/")
            if response.status_code == 200:
                departments = response.json()
                if departments:
                    self.test_data["department"] = departments[0]
                    print(f"✅ Using existing department: {self.test_data['department']['name']}")
                else:
                    print("❌ No departments available for testing")
                    return False
            else:
                print("❌ Failed to get departments")
                return False
        
        return True
    
    def test_create_department_head(self):
        """Test creating a new department head"""
        self.print_subsection("CREATE DEPARTMENT HEAD")
        
        dept_head_data = {
            "firstName": "Dr. John",
            "lastName": "Smith",
            "email": "john.smith.head@university.com",
            "login": "john.smith.head",
            "password": "head123",
            "role": "DEPARTMENT_HEAD"
        }
        
        url = f"{self.base_url}/admin/department-heads/"
        if "department" in self.test_data:
            url += f"?department_id={self.test_data['department']['id']}"
        
        response = self.session.post(url, json=dept_head_data)
        
        if response.status_code in [200, 201]:
            dept_head = response.json()
            self.test_data["dept_head"] = dept_head
            print("✅ Department head created successfully")
            print(f"   Name: {dept_head['firstName']} {dept_head['lastName']}")
            print(f"   Email: {dept_head['email']}")
            if "departmentHeadInfo" in dept_head:
                print(f"   Department: {dept_head['departmentHeadInfo']['department']['name']}")
            return True
        else:
            print(f"❌ Failed to create department head: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def test_get_department_heads(self):
        """Test retrieving all department heads"""
        self.print_subsection("GET ALL DEPARTMENT HEADS")
        
        response = self.session.get(f"{self.base_url}/admin/department-heads/")
        
        if response.status_code == 200:
            dept_heads = response.json()
            print(f"✅ Retrieved {len(dept_heads)} department heads")
            
            for i, head in enumerate(dept_heads[:3], 1):
                print(f"   {i}. {head.get('firstName', '')} {head.get('lastName', '')} - {head.get('email', '')}")
                if "departmentHeadInfo" in head:
                    dept_info = head['departmentHeadInfo']['department']
                    print(f"      Department: {dept_info['name']}")
            return True
        else:
            print(f"❌ Failed to get department heads: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def test_get_department_head_by_id(self):
        """Test retrieving department head by ID"""
        if "dept_head" not in self.test_data or "departmentHeadInfo" not in self.test_data["dept_head"]:
            print("❌ No test department head available for ID test")
            return False
        
        self.print_subsection("GET DEPARTMENT HEAD BY ID")
        
        dept_head_id = self.test_data["dept_head"]["departmentHeadInfo"]["id"]
        response = self.session.get(f"{self.base_url}/admin/department-heads/{dept_head_id}")
        
        if response.status_code == 200:
            dept_head = response.json()
            print("✅ Retrieved department head by ID")
            print(f"   Name: {dept_head['firstName']} {dept_head['lastName']}")
            print(f"   Role: {dept_head['role']}")
            return True
        else:
            print(f"❌ Failed to get department head by ID: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def test_update_department_head_user_info(self):
        """Test updating department head user information"""
        if "dept_head" not in self.test_data or "departmentHeadInfo" not in self.test_data["dept_head"]:
            print("❌ No test department head available for update test")
            return False
        
        self.print_subsection("UPDATE DEPARTMENT HEAD USER INFO")
        
        dept_head_id = self.test_data["dept_head"]["departmentHeadInfo"]["id"]
        update_data = {
            "firstName": "Dr. John Updated",
            "lastName": "Smith Updated"
        }
        
        response = self.session.patch(
            f"{self.base_url}/admin/department-heads/{dept_head_id}/user",
            json=update_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Department head user info updated successfully")
            print(f"   Updated fields: {result.get('updatedFields', [])}")
            if "departmentHead" in result:
                dept_head = result["departmentHead"]
                print(f"   New name: {dept_head['firstName']} {dept_head['lastName']}")
            return True
        else:
            print(f"❌ Failed to update department head: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def test_create_teacher_and_promote(self):
        """Test creating a teacher and promoting to department head"""
        self.print_subsection("CREATE TEACHER AND PROMOTE TO DEPARTMENT HEAD")
        
        # First create a teacher
        teacher_data = {
            "firstName": "Prof. Jane",
            "lastName": "Doe",
            "email": "jane.doe.teacher@university.com",
            "login": "jane.doe.teacher",
            "password": "teacher123",
            "role": "TEACHER"
        }
        
        url = f"{self.base_url}/admin/teachers/"
        if "department" in self.test_data:
            url += f"?department_id={self.test_data['department']['id']}"
        
        response = self.session.post(url, json=teacher_data)
        
        if response.status_code in [200, 201]:
            teacher = response.json()
            print("✅ Teacher created successfully")
            
            if "teacherInfo" in teacher:
                teacher_id = teacher["teacherInfo"]["id"]
                
                # Now promote to department head
                # First, we need another department for this test
                dept2_data = {
                    "name": "Mathematics Test Department",
                    "description": "Second test department"
                }
                
                dept_response = self.session.post(f"{self.base_url}/admin/departments/", json=dept2_data)
                if dept_response.status_code in [200, 201]:
                    dept2 = dept_response.json()
                    
                    promote_url = f"{self.base_url}/admin/department-heads/assign-from-teacher/{teacher_id}"
                    promote_url += f"?department_id={dept2['id']}"
                    
                    promote_response = self.session.post(promote_url)
                    
                    if promote_response.status_code in [200, 201]:
                        result = promote_response.json()
                        print("✅ Teacher promoted to department head successfully")
                        self.test_data["promoted_dept_head"] = result["departmentHead"]
                        return True
                    else:
                        print(f"❌ Failed to promote teacher: {promote_response.status_code}")
                        return False
                else:
                    print("❌ Failed to create second department for promotion test")
                    return False
            else:
                print("❌ Teacher created but no teacher info found")
                return False
        else:
            print(f"❌ Failed to create teacher: {response.status_code}")
            return False
    
    def test_demote_department_head(self):
        """Test demoting department head back to teacher"""
        if "promoted_dept_head" not in self.test_data:
            print("❌ No promoted department head available for demotion test")
            return False
        
        self.print_subsection("DEMOTE DEPARTMENT HEAD TO TEACHER")
        
        dept_head_id = self.test_data["promoted_dept_head"]["departmentHeadInfo"]["id"]
        response = self.session.post(f"{self.base_url}/admin/department-heads/{dept_head_id}/demote-to-teacher")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Department head demoted to teacher successfully")
            print(f"   Demoted user: {result['demotedInfo']['userName']}")
            if "teacherInfo" in result:
                print(f"   Teacher department: {result['teacherInfo']['department']}")
            return True
        else:
            print(f"❌ Failed to demote department head: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def test_delete_department_head(self):
        """Test deleting a department head"""
        if "dept_head" not in self.test_data or "departmentHeadInfo" not in self.test_data["dept_head"]:
            print("❌ No test department head available for deletion test")
            return False
        
        self.print_subsection("DELETE DEPARTMENT HEAD")
        
        dept_head_id = self.test_data["dept_head"]["departmentHeadInfo"]["id"]
        response = self.session.delete(f"{self.base_url}/admin/department-heads/{dept_head_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Department head deleted successfully")
            if "deletedDepartmentHead" in result:
                deleted_info = result["deletedDepartmentHead"]
                print(f"   Deleted: {deleted_info['userName']} ({deleted_info['email']})")
                print(f"   From department: {deleted_info['departmentName']}")
            return True
        else:
            print(f"❌ Failed to delete department head: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all department head CRUD tests"""
        print("🎓 Department Heads CRUD Test Suite")
        print("="*60)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Cannot proceed without admin authentication")
            return
        
        if not self.setup_test_department():
            print("❌ Cannot proceed without test department")
            return
        
        # Test results
        results = {
            "Create Department Head": self.test_create_department_head(),
            "Get All Department Heads": self.test_get_department_heads(),
            "Get Department Head by ID": self.test_get_department_head_by_id(),
            "Update User Info": self.test_update_department_head_user_info(),
            "Create Teacher and Promote": self.test_create_teacher_and_promote(),
            "Demote to Teacher": self.test_demote_department_head(),
            "Delete Department Head": self.test_delete_department_head()
        }
        
        # Summary
        self.print_section("TEST RESULTS SUMMARY")
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<35} {status}")
        
        print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All department head CRUD operations are working correctly!")
        else:
            print("⚠️  Some operations need attention. Check the failed tests above.")
        
        print(f"\n📊 Test API endpoints at: {self.base_url}/docs")

def main():
    """Main function to run the tests"""
    tester = DepartmentHeadsCRUDTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()