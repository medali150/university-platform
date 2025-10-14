"""
Comprehensive Absence System Test Script
Tests all absence management functionality with the provided user credentials.
User: wahid@gmail.com
Password: dalighgh15
"""
import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "wahid@gmail.com"
TEST_USER_PASSWORD = "dalighgh15"

class AbsenceSystemTester:
    def __init__(self):
        self.token = None
        self.user_info = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate(self):
        """Authenticate with the provided credentials"""
        print(f"\n🔐 Authenticating user: {TEST_USER_EMAIL}")
        print("=" * 60)
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_info = data.get("user")
                
                print(f"User ID: {self.user_info.get('id')}")
                print(f"Role: {self.user_info.get('role')}")
                print(f"Name: {self.user_info.get('prenom')} {self.user_info.get('nom')}")
                print(f"Email: {self.user_info.get('email')}")
                
                self.log_test("Authentication", True, "Successfully logged in", {
                    "user_id": self.user_info.get('id'),
                    "role": self.user_info.get('role')
                })
                return True
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_get_user_absences(self):
        """Test getting user's absences (works for all roles)"""
        print(f"\n📋 Testing Get User Absences")
        print("=" * 60)
        
        try:
            # Test getting student absences if user is student
            if self.user_info.get('role') == 'STUDENT':
                response = requests.get(
                    f"{BASE_URL}/absences/student/my-absences",
                    headers=self.get_headers()
                )
            else:
                # For teachers/admins, get all absences
                response = requests.get(
                    f"{BASE_URL}/absences/all",
                    headers=self.get_headers()
                )
            
            if response.status_code == 200:
                data = response.json()
                absences = data.get('absences', [])
                print(f"Found {len(absences)} absences")
                
                if absences:
                    print("\nSample absence:")
                    sample = absences[0]
                    for key, value in sample.items():
                        print(f"  {key}: {value}")
                
                self.log_test("Get User Absences", True, f"Retrieved {len(absences)} absences", {
                    "count": len(absences),
                    "sample": absences[0] if absences else None
                })
                return absences
            else:
                self.log_test("Get User Absences", False, f"Failed to get absences: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get User Absences", False, f"Error getting absences: {str(e)}")
            return []
    
    def test_get_schedules(self):
        """Test getting user's schedules"""
        print(f"\n📅 Testing Get Schedules")
        print("=" * 60)
        
        try:
            if self.user_info.get('role') == 'TEACHER':
                # Get teacher's schedule
                response = requests.get(
                    f"{BASE_URL}/teacher/schedule/today",
                    headers=self.get_headers()
                )
            elif self.user_info.get('role') == 'STUDENT':
                # Get student's schedule (if endpoint exists)
                response = requests.get(
                    f"{BASE_URL}/student/schedule/today",
                    headers=self.get_headers()
                )
            else:
                # For department heads/admins, try getting all schedules
                response = requests.get(
                    f"{BASE_URL}/schedules",
                    headers=self.get_headers()
                )
            
            if response.status_code == 200:
                schedules = response.json()
                if isinstance(schedules, list):
                    count = len(schedules)
                else:
                    count = len(schedules.get('schedules', [])) if 'schedules' in schedules else 1
                
                print(f"Found {count} schedule(s)")
                
                if schedules:
                    print("\nSample schedule:")
                    sample = schedules[0] if isinstance(schedules, list) else schedules
                    for key, value in sample.items():
                        print(f"  {key}: {value}")
                
                self.log_test("Get Schedules", True, f"Retrieved {count} schedule(s)", {
                    "count": count,
                    "sample": sample if schedules else None
                })
                return schedules
            else:
                self.log_test("Get Schedules", False, f"Failed to get schedules: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get Schedules", False, f"Error getting schedules: {str(e)}")
            return []
    
    def test_create_absence(self):
        """Test creating an absence (for teachers/admins)"""
        print(f"\n➕ Testing Create Absence")
        print("=" * 60)
        
        if self.user_info.get('role') not in ['TEACHER', 'DEPARTMENT_HEAD', 'ADMIN']:
            self.log_test("Create Absence", False, "User role not authorized to create absences")
            return None
        
        try:
            # First, try to get some test data (students and schedules)
            # Get students
            students_response = requests.get(
                f"{BASE_URL}/admin/students",
                headers=self.get_headers()
            )
            
            if students_response.status_code != 200:
                self.log_test("Create Absence", False, "Could not retrieve students for testing")
                return None
            
            students = students_response.json()
            if not students or len(students) == 0:
                self.log_test("Create Absence", False, "No students found for testing")
                return None
            
            # Get schedules
            schedules_response = requests.get(
                f"{BASE_URL}/schedules",
                headers=self.get_headers()
            )
            
            if schedules_response.status_code != 200:
                self.log_test("Create Absence", False, "Could not retrieve schedules for testing")
                return None
            
            schedules = schedules_response.json()
            if not schedules or len(schedules) == 0:
                self.log_test("Create Absence", False, "No schedules found for testing")
                return None
            
            # Create test absence
            test_student = students[0]
            test_schedule = schedules[0]
            
            absence_data = {
                "studentId": test_student.get('id'),
                "scheduleId": test_schedule.get('id'),
                "reason": f"Test absence created by {self.user_info.get('email')} at {datetime.now().isoformat()}",
                "status": "unjustified"
            }
            
            print(f"Creating absence for student: {test_student.get('nom')} {test_student.get('prenom')}")
            print(f"Schedule ID: {test_schedule.get('id')}")
            
            response = requests.post(
                f"{BASE_URL}/absences",
                headers=self.get_headers(),
                json=absence_data
            )
            
            if response.status_code in [200, 201]:
                created_absence = response.json()
                print(f"✅ Absence created successfully!")
                print(f"Absence ID: {created_absence.get('id')}")
                print(f"Notification sent: {created_absence.get('notification_sent', 'N/A')}")
                
                self.log_test("Create Absence", True, "Successfully created test absence", {
                    "absence_id": created_absence.get('id'),
                    "student_id": test_student.get('id'),
                    "schedule_id": test_schedule.get('id')
                })
                return created_absence
            else:
                self.log_test("Create Absence", False, f"Failed to create absence: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Absence", False, f"Error creating absence: {str(e)}")
            return None
    
    def test_justify_absence(self, absence_id=None):
        """Test justifying an absence (for students)"""
        print(f"\n📝 Testing Justify Absence")
        print("=" * 60)
        
        if not absence_id:
            # Try to find an unjustified absence
            absences = self.test_get_user_absences()
            unjustified = [a for a in absences if a.get('status') == 'unjustified']
            
            if not unjustified:
                self.log_test("Justify Absence", False, "No unjustified absences found to test")
                return None
            
            absence_id = unjustified[0].get('id')
        
        try:
            justification_data = {
                "justification_text": f"Test justification submitted by {self.user_info.get('email')} at {datetime.now().isoformat()}"
            }
            
            print(f"Justifying absence ID: {absence_id}")
            
            response = requests.put(
                f"{BASE_URL}/absences/{absence_id}/justify",
                headers=self.get_headers(),
                json=justification_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Absence justified successfully!")
                print(f"Message: {result.get('message')}")
                
                self.log_test("Justify Absence", True, "Successfully justified absence", {
                    "absence_id": absence_id,
                    "justification": justification_data["justification_text"]
                })
                return result
            else:
                self.log_test("Justify Absence", False, f"Failed to justify absence: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Justify Absence", False, f"Error justifying absence: {str(e)}")
            return None
    
    def test_review_absence(self, absence_id=None):
        """Test reviewing an absence (for department heads/admins)"""
        print(f"\n🔍 Testing Review Absence")
        print("=" * 60)
        
        if self.user_info.get('role') not in ['DEPARTMENT_HEAD', 'ADMIN']:
            self.log_test("Review Absence", False, "User role not authorized to review absences")
            return None
        
        if not absence_id:
            # Try to find a pending absence
            absences = self.test_get_user_absences()
            pending = [a for a in absences if a.get('status') in ['pending_review', 'unjustified']]
            
            if not pending:
                self.log_test("Review Absence", False, "No pending absences found to test")
                return None
            
            absence_id = pending[0].get('id')
        
        try:
            review_data = {
                "action": "approve",
                "review_notes": f"Test review by {self.user_info.get('email')} at {datetime.now().isoformat()}"
            }
            
            print(f"Reviewing absence ID: {absence_id}")
            print(f"Action: {review_data['action']}")
            
            response = requests.put(
                f"{BASE_URL}/absences/{absence_id}/review",
                headers=self.get_headers(),
                json=review_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Absence reviewed successfully!")
                print(f"Message: {result.get('message')}")
                
                self.log_test("Review Absence", True, "Successfully reviewed absence", {
                    "absence_id": absence_id,
                    "action": review_data["action"],
                    "notes": review_data["review_notes"]
                })
                return result
            else:
                self.log_test("Review Absence", False, f"Failed to review absence: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Review Absence", False, f"Error reviewing absence: {str(e)}")
            return None
    
    def test_absence_statistics(self):
        """Test getting absence statistics"""
        print(f"\n📊 Testing Absence Statistics")
        print("=" * 60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/absences/statistics",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Statistics retrieved successfully!")
                
                print("\nStatistics Summary:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                
                self.log_test("Absence Statistics", True, "Successfully retrieved statistics", stats)
                return stats
            else:
                self.log_test("Absence Statistics", False, f"Failed to get statistics: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Absence Statistics", False, f"Error getting statistics: {str(e)}")
            return None
    
    def test_delete_absence(self, absence_id=None):
        """Test deleting an absence"""
        print(f"\n🗑️  Testing Delete Absence")
        print("=" * 60)
        
        if self.user_info.get('role') not in ['TEACHER', 'DEPARTMENT_HEAD', 'ADMIN']:
            self.log_test("Delete Absence", False, "User role not authorized to delete absences")
            return None
        
        if not absence_id:
            # Try to find an absence to delete
            absences = self.test_get_user_absences()
            if not absences:
                self.log_test("Delete Absence", False, "No absences found to test deletion")
                return None
            
            absence_id = absences[-1].get('id')  # Delete the last one
        
        try:
            print(f"Deleting absence ID: {absence_id}")
            
            response = requests.delete(
                f"{BASE_URL}/absences/{absence_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Absence deleted successfully!")
                print(f"Message: {result.get('message')}")
                
                self.log_test("Delete Absence", True, "Successfully deleted absence", {
                    "absence_id": absence_id
                })
                return result
            else:
                self.log_test("Delete Absence", False, f"Failed to delete absence: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Delete Absence", False, f"Error deleting absence: {str(e)}")
            return None
    
    def run_comprehensive_test(self):
        """Run all absence system tests"""
        print("🚀 Starting Comprehensive Absence System Test")
        print("=" * 60)
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"API Base URL: {BASE_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("\n❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Step 2: Get current absences
        absences = self.test_get_user_absences()
        
        # Step 3: Get schedules
        schedules = self.test_get_schedules()
        
        # Step 4: Test creating an absence (if authorized)
        created_absence = self.test_create_absence()
        
        # Step 5: Test justifying an absence
        if created_absence:
            self.test_justify_absence(created_absence.get('id'))
        else:
            self.test_justify_absence()
        
        # Step 6: Test reviewing an absence (if authorized)
        if created_absence:
            self.test_review_absence(created_absence.get('id'))
        else:
            self.test_review_absence()
        
        # Step 7: Test getting statistics
        self.test_absence_statistics()
        
        # Step 8: Test deleting an absence (if authorized)
        # Note: We'll skip this in the comprehensive test to avoid deleting important data
        # self.test_delete_absence()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Save results to file
        with open('absence_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100,
                    'test_date': datetime.now().isoformat(),
                    'user': TEST_USER_EMAIL
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: absence_test_results.json")

if __name__ == "__main__":
    tester = AbsenceSystemTester()
    tester.run_comprehensive_test()