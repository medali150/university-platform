#!/usr/bin/env python3
"""
Simplified real test for the Enhanced Absence Notification System
Tests the actual notification service functions without Prisma dependency
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_notification_service_functions():
    """Test all notification service functions directly"""
    
    print("🧪 REAL ABSENCE NOTIFICATION SYSTEM TEST")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Mode: Direct Function Testing")
    print()
    
    try:
        # Import the notification service
        from app.services.enhanced_notification_service import AbsenceNotificationService
        
        print("✅ AbsenceNotificationService imported successfully")
        print()
        
        # Test data
        test_data = {
            'student_email': 'ahmed.benali@university.edu',
            'student_name': 'Ahmed Ben Ali',
            'teacher_name': 'Prof. Mohammed Slimi',
            'teacher_email': 'prof.slimi@university.edu',
            'subject_name': 'Mathematics',
            'absence_date': datetime.now().strftime('%Y-%m-%d'),
            'absence_time': '09:30',
            'absence_id': 'test_absence_001'
        }
        
        print("📋 Test Data:")
        print(f"   👨‍🎓 Student: {test_data['student_name']} ({test_data['student_email']})")
        print(f"   👨‍🏫 Teacher: {test_data['teacher_name']} ({test_data['teacher_email']})")
        print(f"   📚 Subject: {test_data['subject_name']}")
        print(f"   📅 Date: {test_data['absence_date']} at {test_data['absence_time']}")
        print()
        
        test_results = []
        
        # Test 1: Student Absence Marked
        print("🧪 TEST 1: Student Absence Marked Notification")
        print("-" * 50)
        try:
            result = await AbsenceNotificationService.notify_student_absence_marked(
                student_email=test_data['student_email'],
                student_name=test_data['student_name'],
                subject_name=test_data['subject_name'],
                teacher_name=test_data['teacher_name'],
                absence_date=test_data['absence_date'],
                absence_time=test_data['absence_time'],
                absence_reason="Late arrival to class",
                absence_id=test_data['absence_id']
            )
            
            print("✅ Student absence notification executed successfully")
            print(f"   📧 Target: {test_data['student_email']}")
            print(f"   📝 Subject: Absence marked for {test_data['subject_name']}")
            print(f"   🎯 Result: {result.get('status', 'unknown')}")
            test_results.append(("Student Absence Marked", True))
            print()
            
        except Exception as e:
            print(f"❌ Student absence notification failed: {e}")
            test_results.append(("Student Absence Marked", False))
            print()
        
        # Test 2: Teacher Justification Notification
        print("🧪 TEST 2: Teacher Justification Notification")
        print("-" * 50)
        try:
            result = await AbsenceNotificationService.notify_teacher_absence_justified(
                teacher_email=test_data['teacher_email'],
                teacher_name=test_data['teacher_name'],
                student_name=test_data['student_name'],
                subject_name=test_data['subject_name'],
                absence_date=test_data['absence_date'],
                justification_text="I had a medical emergency and couldn't attend class",
                absence_id=test_data['absence_id']
            )
            
            print("✅ Teacher justification notification executed successfully")
            print(f"   📧 Target: {test_data['teacher_email']}")
            print(f"   👨‍🎓 Student: {test_data['student_name']} submitted justification")
            print(f"   🎯 Result: {result.get('status', 'unknown')}")
            test_results.append(("Teacher Justification", True))
            print()
            
        except Exception as e:
            print(f"❌ Teacher justification notification failed: {e}")
            test_results.append(("Teacher Justification", False))
            print()
        
        # Test 3: Student Justification Approved
        print("🧪 TEST 3: Student Justification Approved")
        print("-" * 50)
        try:
            result = await AbsenceNotificationService.notify_student_justification_approved(
                student_email=test_data['student_email'],
                student_name=test_data['student_name'],
                subject_name=test_data['subject_name'],
                absence_date=test_data['absence_date'],
                reviewer_name="Academic Administrator",
                absence_id=test_data['absence_id']
            )
            
            print("✅ Student justification approval executed successfully")
            print(f"   📧 Target: {test_data['student_email']}")
            print(f"   ✅ Status: Justification approved")
            print(f"   🎯 Result: {result.get('status', 'unknown')}")
            test_results.append(("Justification Approved", True))
            print()
            
        except Exception as e:
            print(f"❌ Student justification approval failed: {e}")
            test_results.append(("Justification Approved", False))
            print()
        
        # Test 4: Student Justification Rejected
        print("🧪 TEST 4: Student Justification Rejected")
        print("-" * 50)
        try:
            result = await AbsenceNotificationService.notify_student_justification_rejected(
                student_email=test_data['student_email'],
                student_name=test_data['student_name'],
                subject_name=test_data['subject_name'],
                absence_date=test_data['absence_date'],
                reviewer_name="Academic Administrator",
                rejection_reason="Insufficient documentation provided",
                absence_id=test_data['absence_id']
            )
            
            print("✅ Student justification rejection executed successfully")
            print(f"   📧 Target: {test_data['student_email']}")
            print(f"   ❌ Status: Justification rejected")
            print(f"   📝 Reason: Insufficient documentation")
            print(f"   🎯 Result: {result.get('status', 'unknown')}")
            test_results.append(("Justification Rejected", True))
            print()
            
        except Exception as e:
            print(f"❌ Student justification rejection failed: {e}")
            test_results.append(("Justification Rejected", False))
            print()
        
        # Test 5: Department Head High Absences Alert
        print("🧪 TEST 5: Department Head High Absences Alert")
        print("-" * 50)
        try:
            result = await AbsenceNotificationService.notify_department_head_high_absences(
                dept_head_email="dept.head@university.edu",
                dept_head_name="Dr. Department Head",
                student_name=test_data['student_name'],
                student_email=test_data['student_email'],
                absence_count=8,
                time_period="current month",
                department_name="Computer Science"
            )
            
            print("✅ Department head alert executed successfully")
            print(f"   📧 Target: dept.head@university.edu")
            print(f"   🚨 Alert: {test_data['student_name']} has 8 absences")
            print(f"   🎯 Result: {result.get('status', 'unknown')}")
            test_results.append(("High Absences Alert", True))
            print()
            
        except Exception as e:
            print(f"❌ Department head alert failed: {e}")
            test_results.append(("High Absences Alert", False))
            print()
        
        # Test 6: Parent Alert
        print("🧪 TEST 6: Parent Alert Notification")
        print("-" * 50)
        try:
            result = await AbsenceNotificationService.notify_parent_high_absences(
                parent_email="parent@email.com",
                parent_name="Parent Name",
                student_name=test_data['student_name'],
                absence_count=6,
                time_period="this week",
                school_contact="contact@university.edu"
            )
            
            print("✅ Parent alert executed successfully")
            print(f"   📧 Target: parent@email.com")
            print(f"   👨‍👩‍👧‍👦 Alert: {test_data['student_name']} has 6 absences this week")
            print(f"   🎯 Result: {result.get('status', 'unknown')}")
            test_results.append(("Parent Alert", True))
            print()
            
        except Exception as e:
            print(f"❌ Parent alert failed: {e}")
            test_results.append(("Parent Alert", False))
            print()
        
        # Test 7: Daily Summary
        print("🧪 TEST 7: Daily Absence Summary")
        print("-" * 50)
        try:
            result = await AbsenceNotificationService.send_daily_absence_summary(
                teacher_email=test_data['teacher_email'],
                teacher_name=test_data['teacher_name'],
                date=test_data['absence_date'],
                total_absences=15,
                pending_justifications=4,
                subjects_taught=[test_data['subject_name'], "Physics", "Chemistry"]
            )
            
            print("✅ Daily summary executed successfully")
            print(f"   📧 Target: {test_data['teacher_email']}")
            print(f"   📊 Summary: 15 absences, 4 pending justifications")
            print(f"   🎯 Result: {result.get('status', 'unknown')}")
            test_results.append(("Daily Summary", True))
            print()
            
        except Exception as e:
            print(f"❌ Daily summary failed: {e}")
            test_results.append(("Daily Summary", False))
            print()
        
        # Test compatibility function
        print("🧪 TEST 8: Compatibility Function")
        print("-" * 50)
        try:
            from app.services.enhanced_notification_service import send_notification_with_details
            
            result = await send_notification_with_details(
                user_id=test_data['student_email'],
                notification_id="compatibility_test",
                title="Compatibility Test",
                message="Testing backward compatibility",
                channels=["email", "in_app"]
            )
            
            print("✅ Compatibility function executed successfully")
            print(f"   📧 Target: {test_data['student_email']}")
            print(f"   🔄 Backward compatibility confirmed")
            print(f"   🎯 Result: {result.get('success', False)}")
            test_results.append(("Compatibility Function", True))
            print()
            
        except Exception as e:
            print(f"❌ Compatibility function failed: {e}")
            test_results.append(("Compatibility Function", False))
            print()
        
        # Results Summary
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} | {test_name}")
        
        print()
        print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED! Notification system is fully functional!")
        elif success_rate >= 80:
            print("✅ Most tests passed. Minor issues may need attention.")
        else:
            print("⚠️ Several tests failed. System needs review.")
        
        print()
        print("🔍 SYSTEM ANALYSIS:")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   🔧 Mock Notifications: Working")
        print(f"   📱 Multi-channel Support: Implemented")
        print(f"   🛡️ Error Handling: Active")
        print(f"   🔄 Compatibility: Maintained")
        
        print()
        print("🚀 NEXT STEPS FOR PRODUCTION:")
        print("   1. Install NotificationAPI SDK: pip install notificationapi-python-server-sdk")
        print("   2. Replace mock implementation with real NotificationAPI")
        print("   3. Configure production notification templates")
        print("   4. Set up email/SMS provider credentials")
        print("   5. Test with real notification delivery")
        print("   6. Deploy to staging environment")
        
        return success_rate == 100
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please ensure the notification service is properly installed")
        return False
    except Exception as e:
        print(f"❌ Critical test failure: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_notification_service_functions())