#!/usr/bin/env python3
"""
Create test accounts for absence notification testing
Creates a student account and a teacher account with proper setup
"""
import asyncio
import sys
import os
from datetime import datetime
import hashlib

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def create_test_accounts():
    """Create student and teacher accounts for notification testing"""
    
    print("🏫 CREATING TEST ACCOUNTS FOR ABSENCE NOTIFICATION TESTING")
    print("=" * 70)
    print(f"📅 Creation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Import database models and connection
        from app.database import get_db
        from app.models.user import User
        from app.models.student import Student
        from app.models.teacher import Teacher
        from app.models.subject import Subject
        from app.models.class_model import Class
        from app.models.department import Department
        from app.models.schedule import Schedule
        from sqlalchemy.orm import Session
        from sqlalchemy import text
        
        # Get database session
        db_gen = get_db()
        db: Session = next(db_gen)
        
        print("✅ Database connection established")
        print()
        
        # Helper function to hash password
        def hash_password(password: str) -> str:
            return hashlib.sha256(password.encode()).hexdigest()
        
        # Check if accounts already exist
        existing_student = db.query(User).filter(User.email == "test.student@university.edu").first()
        existing_teacher = db.query(User).filter(User.email == "test.teacher@university.edu").first()
        
        if existing_student or existing_teacher:
            print("⚠️ Test accounts already exist. Cleaning up first...")
            
            # Clean up existing test data
            if existing_student:
                # Delete related student data
                student_record = db.query(Student).filter(Student.user_id == existing_student.id).first()
                if student_record:
                    db.delete(student_record)
                db.delete(existing_student)
                print("   🗑️ Removed existing student account")
            
            if existing_teacher:
                # Delete related teacher data
                teacher_record = db.query(Teacher).filter(Teacher.user_id == existing_teacher.id).first()
                if teacher_record:
                    db.delete(teacher_record)
                db.delete(existing_teacher)
                print("   🗑️ Removed existing teacher account")
            
            db.commit()
            print("   ✅ Cleanup completed")
            print()
        
        # Create or get test department
        test_department = db.query(Department).filter(Department.name == "Computer Science").first()
        if not test_department:
            test_department = Department(
                name="Computer Science",
                description="Computer Science Department for testing"
            )
            db.add(test_department)
            db.commit()
            db.refresh(test_department)
            print("✅ Created test department: Computer Science")
        else:
            print("✅ Using existing department: Computer Science")
        
        # Create test subject
        test_subject = db.query(Subject).filter(Subject.name == "Programming Fundamentals").first()
        if not test_subject:
            test_subject = Subject(
                name="Programming Fundamentals",
                code="CS101",
                credits=3,
                department_id=test_department.id,
                description="Introduction to programming concepts"
            )
            db.add(test_subject)
            db.commit()
            db.refresh(test_subject)
            print("✅ Created test subject: Programming Fundamentals (CS101)")
        else:
            print("✅ Using existing subject: Programming Fundamentals (CS101)")
        
        # Create test class
        test_class = db.query(Class).filter(Class.name == "CS101-A").first()
        if not test_class:
            test_class = Class(
                name="CS101-A",
                department_id=test_department.id,
                year=2025,
                semester="Fall"
            )
            db.add(test_class)
            db.commit()
            db.refresh(test_class)
            print("✅ Created test class: CS101-A")
        else:
            print("✅ Using existing class: CS101-A")
        
        print()
        
        # 1. CREATE STUDENT ACCOUNT
        print("👨‍🎓 CREATING STUDENT ACCOUNT")
        print("-" * 40)
        
        # Create student user
        student_user = User(
            username="test_student",
            email="test.student@university.edu",
            password_hash=hash_password("student123"),
            first_name="Ahmed",
            last_name="Ben Ali",
            role="student",
            is_active=True
        )
        
        db.add(student_user)
        db.commit()
        db.refresh(student_user)
        
        # Create student record
        student_record = Student(
            user_id=student_user.id,
            student_id="STU2025001",
            class_id=test_class.id,
            department_id=test_department.id,
            year_of_study=2,
            enrollment_date=datetime.now()
        )
        
        db.add(student_record)
        db.commit()
        db.refresh(student_record)
        
        print(f"✅ Student Account Created:")
        print(f"   📧 Email: {student_user.email}")
        print(f"   👤 Username: {student_user.username}")
        print(f"   🔑 Password: student123")
        print(f"   📛 Name: {student_user.first_name} {student_user.last_name}")
        print(f"   🆔 Student ID: {student_record.student_id}")
        print(f"   🏫 Class: {test_class.name}")
        print(f"   📚 Department: {test_department.name}")
        print()
        
        # 2. CREATE TEACHER ACCOUNT
        print("👨‍🏫 CREATING TEACHER ACCOUNT")
        print("-" * 40)
        
        # Create teacher user
        teacher_user = User(
            username="test_teacher",
            email="test.teacher@university.edu",
            password_hash=hash_password("teacher123"),
            first_name="Prof. Mohammed",
            last_name="Slimi",
            role="teacher",
            is_active=True
        )
        
        db.add(teacher_user)
        db.commit()
        db.refresh(teacher_user)
        
        # Create teacher record
        teacher_record = Teacher(
            user_id=teacher_user.id,
            employee_id="TEACH2025001",
            department_id=test_department.id,
            title="Professor",
            specialization="Computer Science",
            hire_date=datetime.now()
        )
        
        db.add(teacher_record)
        db.commit()
        db.refresh(teacher_record)
        
        print(f"✅ Teacher Account Created:")
        print(f"   📧 Email: {teacher_user.email}")
        print(f"   👤 Username: {teacher_user.username}")
        print(f"   🔑 Password: teacher123")
        print(f"   📛 Name: {teacher_user.first_name} {teacher_user.last_name}")
        print(f"   🆔 Employee ID: {teacher_record.employee_id}")
        print(f"   🏢 Title: {teacher_record.title}")
        print(f"   📚 Department: {test_department.name}")
        print()
        
        # 3. CREATE SCHEDULE ENTRY
        print("📅 CREATING SCHEDULE ENTRY")
        print("-" * 40)
        
        # Create schedule entry linking student, teacher, and subject
        schedule_entry = Schedule(
            subject_id=test_subject.id,
            teacher_id=teacher_record.id,
            class_id=test_class.id,
            day_of_week="Monday",
            start_time="09:00",
            end_time="10:30",
            room="Room A101"
        )
        
        db.add(schedule_entry)
        db.commit()
        db.refresh(schedule_entry)
        
        print(f"✅ Schedule Entry Created:")
        print(f"   📚 Subject: {test_subject.name} ({test_subject.code})")
        print(f"   👨‍🏫 Teacher: {teacher_user.first_name} {teacher_user.last_name}")
        print(f"   🏫 Class: {test_class.name}")
        print(f"   📅 Day: {schedule_entry.day_of_week}")
        print(f"   ⏰ Time: {schedule_entry.start_time} - {schedule_entry.end_time}")
        print(f"   🏢 Room: {schedule_entry.room}")
        print()
        
        # 4. DISPLAY TEST INFORMATION
        print("📋 TEST ACCOUNT SUMMARY")
        print("=" * 70)
        print()
        
        print("🔐 LOGIN CREDENTIALS:")
        print("-" * 30)
        print(f"👨‍🎓 STUDENT LOGIN:")
        print(f"   Email: test.student@university.edu")
        print(f"   Password: student123")
        print()
        print(f"👨‍🏫 TEACHER LOGIN:")
        print(f"   Email: test.teacher@university.edu")
        print(f"   Password: teacher123")
        print()
        
        print("🧪 TESTING SCENARIO:")
        print("-" * 30)
        print(f"1. Login as teacher: test.teacher@university.edu")
        print(f"2. Mark student absent: {student_user.first_name} {student_user.last_name}")
        print(f"3. Check notification sent to: test.student@university.edu")
        print(f"4. Student can justify absence through student portal")
        print(f"5. Teacher receives justification notification")
        print()
        
        print("📡 API ENDPOINTS FOR TESTING:")
        print("-" * 40)
        print("🔍 Login Endpoint:")
        print("   POST /auth/login")
        print("   Body: {\"email\": \"test.student@university.edu\", \"password\": \"student123\"}")
        print()
        print("📝 Mark Absence Endpoint (Teacher):")
        print("   POST /teacher/mark-absence")
        print(f"   Body: {{")
        print(f"     \"student_id\": {student_record.id},")
        print(f"     \"subject_id\": {test_subject.id},")
        print(f"     \"absence_date\": \"{datetime.now().strftime('%Y-%m-%d')}\",")
        print(f"     \"absence_time\": \"09:30\",")
        print(f"     \"reason\": \"Late arrival\"")
        print(f"   }}")
        print()
        print("✅ Check Notifications Endpoint:")
        print("   GET /notifications/user/{user_id}")
        print(f"   Example: GET /notifications/user/{student_user.id}")
        print()
        
        # Store test data for quick reference
        test_data = {
            "student": {
                "id": student_user.id,
                "email": student_user.email,
                "password": "student123",
                "name": f"{student_user.first_name} {student_user.last_name}",
                "student_record_id": student_record.id
            },
            "teacher": {
                "id": teacher_user.id,
                "email": teacher_user.email,
                "password": "teacher123",
                "name": f"{teacher_user.first_name} {teacher_user.last_name}",
                "teacher_record_id": teacher_record.id
            },
            "subject": {
                "id": test_subject.id,
                "name": test_subject.name,
                "code": test_subject.code
            },
            "class": {
                "id": test_class.id,
                "name": test_class.name
            }
        }
        
        print("💾 TEST DATA IDs:")
        print("-" * 30)
        print(f"Student User ID: {student_user.id}")
        print(f"Student Record ID: {student_record.id}")
        print(f"Teacher User ID: {teacher_user.id}")
        print(f"Teacher Record ID: {teacher_record.id}")
        print(f"Subject ID: {test_subject.id}")
        print(f"Class ID: {test_class.id}")
        print(f"Schedule ID: {schedule_entry.id}")
        print()
        
        print("🎯 NEXT STEPS:")
        print("-" * 30)
        print("1. ✅ Accounts created successfully")
        print("2. 🚀 Start the API server: uvicorn main:app --reload")
        print("3. 🧪 Test absence marking with created accounts")
        print("4. 📧 Verify notification delivery")
        print("5. 📱 Test the complete absence workflow")
        
        return test_data
        
    except Exception as e:
        print(f"❌ Error creating test accounts: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_data = asyncio.run(create_test_accounts())
    if test_data:
        print("\n🎉 Test accounts created successfully!")
        print("Ready to test absence notifications! 🚀")
    else:
        print("\n❌ Failed to create test accounts.")