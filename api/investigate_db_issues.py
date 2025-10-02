"""
Investigate and fix teacher/department head role issues
"""
import asyncio
from prisma import Prisma

async def investigate_role_issues():
    """Check for role inconsistencies in the database"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Investigating Role and Data Issues")
        print("=" * 60)
        
        # Get all users and their roles
        all_users = await prisma.user.find_many(
            include={
                "teacher": {"include": {"department": True}},
                "departmentHead": {"include": {"department": True}}
            }
        )
        
        print(f"📊 Total users: {len(all_users)}")
        print()
        
        # Analyze role inconsistencies
        teachers_only = []
        dept_heads_only = []
        both_roles = []
        no_role_record = []
        name_issues = []
        
        for user in all_users:
            has_teacher = user.teacher is not None
            has_dept_head = user.departmentHead is not None
            
            # Check for name issues (email in name)
            if "@" in user.firstName or "@" in user.lastName or ".com" in user.firstName or ".com" in user.lastName:
                name_issues.append(user)
            
            # Categorize by role records
            if has_teacher and has_dept_head:
                both_roles.append(user)
            elif has_teacher and not has_dept_head:
                teachers_only.append(user)
            elif has_dept_head and not has_teacher:
                dept_heads_only.append(user)
            else:
                no_role_record.append(user)
        
        print("📋 ROLE ANALYSIS:")
        print(f"   👨‍🏫 Teachers only: {len(teachers_only)}")
        print(f"   👨‍💼 Department heads only: {len(dept_heads_only)}")
        print(f"   🎭 Both roles: {len(both_roles)}")
        print(f"   ❓ No role record: {len(no_role_record)}")
        print(f"   📝 Name issues: {len(name_issues)}")
        print()
        
        # Show detailed information for problematic cases
        if both_roles:
            print("🎭 USERS WITH BOTH ROLES:")
            for user in both_roles:
                print(f"   • {user.firstName} {user.lastName} (Role: {user.role})")
                print(f"     Email: {user.email}")
                print(f"     Login: {user.login}")
                print(f"     Teacher Dept: {user.teacher.department.name if user.teacher and user.teacher.department else 'None'}")
                print(f"     DeptHead Dept: {user.departmentHead.department.name if user.departmentHead and user.departmentHead.department else 'None'}")
                print()
        
        if name_issues:
            print("📝 NAME/EMAIL ISSUES:")
            for user in name_issues:
                print(f"   ❌ '{user.firstName}' '{user.lastName}'")
                print(f"      Email: {user.email}")
                print(f"      Login: {user.login}")
                print(f"      Role: {user.role}")
                print()
        
        # Show role mismatches
        print("⚠️ ROLE MISMATCHES:")
        role_mismatches = 0
        for user in all_users:
            has_teacher = user.teacher is not None
            has_dept_head = user.departmentHead is not None
            
            # Check for mismatches
            if user.role == "TEACHER" and not has_teacher:
                print(f"   • {user.firstName} {user.lastName}: Role=TEACHER but no teacher record")
                role_mismatches += 1
            elif user.role == "DEPARTMENT_HEAD" and not has_dept_head:
                print(f"   • {user.firstName} {user.lastName}: Role=DEPARTMENT_HEAD but no dept head record")
                role_mismatches += 1
            elif user.role not in ["TEACHER", "DEPARTMENT_HEAD", "ADMIN", "STUDENT"] and (has_teacher or has_dept_head):
                print(f"   • {user.firstName} {user.lastName}: Role={user.role} but has teacher/dept records")
                role_mismatches += 1
        
        if role_mismatches == 0:
            print("   ✅ No role mismatches found")
        print()
        
        return {
            "teachers_only": teachers_only,
            "dept_heads_only": dept_heads_only,
            "both_roles": both_roles,
            "no_role_record": no_role_record,
            "name_issues": name_issues,
            "all_users": all_users
        }
        
    finally:
        await prisma.disconnect()

async def fix_data_issues():
    """Fix the identified role and data issues"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔧 FIXING DATA ISSUES")
        print("=" * 60)
        
        fixes_applied = 0
        
        # Get all users
        all_users = await prisma.user.find_many()
        
        for user in all_users:
            needs_update = False
            updates = {}
            
            # Fix name issues - remove emails from name fields
            if "@" in user.firstName:
                if user.firstName == user.email or ".com" in user.firstName:
                    # If firstName is an email, try to extract a proper name
                    email_parts = user.email.split("@")[0]
                    if "." in email_parts:
                        first_part = email_parts.split(".")[0]
                        updates["firstName"] = first_part.capitalize()
                    else:
                        updates["firstName"] = email_parts.capitalize()
                else:
                    # Remove email part from firstName
                    clean_name = user.firstName.split("@")[0].strip()
                    updates["firstName"] = clean_name
                needs_update = True
                print(f"   📝 Fixing firstName: '{user.firstName}' -> '{updates['firstName']}'")
            
            if "@" in user.lastName or ".com" in user.lastName:
                if user.lastName == user.email:
                    # If lastName is an email, leave it empty or extract from email
                    email_parts = user.email.split("@")[0]
                    if "." in email_parts:
                        parts = email_parts.split(".")
                        if len(parts) > 1:
                            updates["lastName"] = parts[1].capitalize()
                        else:
                            updates["lastName"] = ""
                    else:
                        updates["lastName"] = ""
                else:
                    updates["lastName"] = ""
                needs_update = True
                print(f"   📝 Fixing lastName: '{user.lastName}' -> '{updates.get('lastName', '')}'")
            
            # Apply updates
            if needs_update:
                await prisma.user.update(
                    where={"id": user.id},
                    data=updates
                )
                fixes_applied += 1
                print(f"   ✅ Updated user {user.id} ({user.login})")
        
        print(f"\n🎉 Applied {fixes_applied} data fixes")
        
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        asyncio.run(fix_data_issues())
        print("\n📊 CHECKING RESULTS:")
        asyncio.run(investigate_role_issues())
    else:
        asyncio.run(investigate_role_issues())
        print("\n💡 To fix data issues, run: python investigate_db_issues.py --fix")