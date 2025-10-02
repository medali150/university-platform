from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, List
from prisma import Prisma
from datetime import datetime, timedelta

from app.db.prisma_client import get_prisma
from app.core.deps import require_admin

router = APIRouter(prefix="/admin/dashboard", tags=["Admin - Dashboard"])


@router.get("/statistics")
async def get_admin_statistics(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get comprehensive statistics for admin dashboard"""
    try:
        # Get counts for all entities
        users_count = await prisma.user.count()
        students_count = await prisma.student.count()
        teachers_count = await prisma.teacher.count()
        department_heads_count = await prisma.departmenthead.count()
        
        # University structure counts
        departments_count = await prisma.department.count()
        specialties_count = await prisma.specialty.count()
        levels_count = await prisma.level.count()
        groups_count = await prisma.group.count()
        
        # Get role distribution - simplified approach
        admin_count = await prisma.user.count(where={"role": "ADMIN"})
        student_users_count = await prisma.user.count(where={"role": "STUDENT"})
        teacher_users_count = await prisma.user.count(where={"role": "TEACHER"})
        dept_head_users_count = await prisma.user.count(where={"role": "DEPARTMENT_HEAD"})
        
        # Get students by department - simplified approach
        students_by_dept = await prisma.student.find_many(
            include={
                "specialty": {
                    "include": {"department": True}
                }
            }
        )
        
        # Process students by department
        dept_student_count = {}
        for student in students_by_dept:
            if student.specialty and student.specialty.department:
                dept_name = student.specialty.department.name
                dept_student_count[dept_name] = dept_student_count.get(dept_name, 0) + 1
        
        # Get teachers by department - simplified approach
        teachers_by_dept = await prisma.teacher.find_many(
            include={"department": True}
        )
        
        # Process teachers by department
        dept_teacher_count = {}
        for teacher in teachers_by_dept:
            if teacher.department:
                dept_name = teacher.department.name
                dept_teacher_count[dept_name] = dept_teacher_count.get(dept_name, 0) + 1
        
        # Get recent registrations (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_users = await prisma.user.count(
            where={
                "createdAt": {
                    "gte": thirty_days_ago
                }
            }
        )
        
        return {
            "overview": {
                "totalUsers": users_count,
                "totalStudents": students_count,
                "totalTeachers": teachers_count,
                "totalDepartmentHeads": department_heads_count,
                "recentRegistrations": recent_users
            },
            "universityStructure": {
                # "faculties": faculties_count,  # removed unsupported
                "departments": departments_count,
                "specialties": specialties_count,
                "levels": levels_count,
                "groups": groups_count
            },
            "roleDistribution": {
                "ADMIN": admin_count,
                "STUDENT": student_users_count,
                "TEACHER": teacher_users_count,
                "DEPARTMENT_HEAD": dept_head_users_count
            },
            "departmentStats": {
                "studentsByDepartment": dept_student_count,
                "teachersByDepartment": dept_teacher_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_admin_stats_alias(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Alias for statistics endpoint"""
    return await get_admin_statistics(prisma, current_user)


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 20,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get recent user activity for admin dashboard"""
    try:
        # Get recent users (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        recent_users = await prisma.user.find_many(
            where={
                "createdAt": {
                    "gte": seven_days_ago
                }
            },
            select={
                "id": True,
                "firstName": True,
                "lastName": True,
                "email": True,
                "role": True,
                "createdAt": True
            },
            order={"createdAt": "desc"},
            take=limit
        )
        
        return {
            "recentRegistrations": recent_users,
            "totalRecentUsers": len(recent_users)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-health")
async def get_system_health(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Get system health information"""
    try:
        # Check database connection
        try:
            # Simple query to test database connectivity
            await prisma.user.count()
            db_status = "healthy"
        except Exception as e:
            db_status = "unhealthy"
            print(f"Database health check failed: {e}")
        
        # Check for any inconsistencies
        inconsistencies = []
        
        # Check for students without specialties
        students_without_specialty = await prisma.student.count(
            where={"specialtyId": None}
        )
        if students_without_specialty > 0:
            inconsistencies.append({
                "type": "missing_data",
                "description": f"{students_without_specialty} students without assigned specialty"
            })
        
        # Check for teachers without departments
        teachers_without_dept = await prisma.teacher.count(
            where={"departmentId": None}
        )
        if teachers_without_dept > 0:
            inconsistencies.append({
                "type": "missing_data", 
                "description": f"{teachers_without_dept} teachers without assigned department"
            })
        
        # University structure counts
        departments = await prisma.department.find_many()
        dept_heads = await prisma.departmenthead.find_many()
        dept_head_dept_ids = {dh.departmentId for dh in dept_heads}
        depts_without_heads = [d for d in departments if d.id not in dept_head_dept_ids]
        
        if depts_without_heads:
            inconsistencies.append({
                "type": "missing_management",
                "description": f"{len(depts_without_heads)} departments without assigned heads",
                "details": [d.name for d in depts_without_heads]
            })
        
        return {
            "database": {
                "status": db_status,
                "lastChecked": datetime.now().isoformat()
            },
            "dataIntegrity": {
                "status": "healthy" if not inconsistencies else "issues_found",
                "inconsistencies": inconsistencies
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_users(
    query: str,
    role: str = None,
    limit: int = 50,
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Search users by name, email, or login"""
    try:
        # Build search conditions
        search_conditions = {
            "OR": [
                {"firstName": {"contains": query}},
                {"lastName": {"contains": query}},
                {"email": {"contains": query}},
                {"login": {"contains": query}}
            ]
        }
        
        if role:
            search_conditions["role"] = role
        
        users = await prisma.user.find_many(
            where=search_conditions,
            select={
                "id": True,
                "firstName": True,
                "lastName": True,
                "email": True,
                "login": True,
                "role": True,
                "createdAt": True
            },
            take=limit,
            order={"createdAt": "desc"}
        )
        
        return {
            "results": users,
            "count": len(users),
            "query": query,
            "role_filter": role
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-actions/delete-users")
async def bulk_delete_users(
    user_ids: List[str],
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_admin)
):
    """Bulk delete users (Admin only)"""
    try:
        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user IDs provided"
            )
        
        # Prevent admin from deleting themselves
        if current_user.id in user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        deleted_count = 0
        errors = []
        
        for user_id in user_ids:
            try:
                # Check if user exists
                user = await prisma.user.find_unique(where={"id": user_id})
                if not user:
                    errors.append(f"User {user_id} not found")
                    continue
                
                # Delete related records based on role
                if user.role == "STUDENT":
                    student = await prisma.student.find_first(where={"userId": user_id})
                    if student:
                        await prisma.student.delete(where={"id": student.id})
                
                elif user.role == "TEACHER":
                    teacher = await prisma.teacher.find_first(where={"userId": user_id})
                    if teacher:
                        await prisma.teacher.delete(where={"id": teacher.id})
                
                elif user.role == "DEPARTMENT_HEAD":
                    dept_head = await prisma.departmenthead.find_first(where={"userId": user_id})
                    if dept_head:
                        await prisma.departmenthead.delete(where={"id": dept_head.id})
                
                # Delete user
                await prisma.user.delete(where={"id": user_id})
                deleted_count += 1
                
            except Exception as e:
                errors.append(f"Error deleting user {user_id}: {str(e)}")
        
        return {
            "message": f"Bulk delete completed",
            "deleted": deleted_count,
            "total_requested": len(user_ids),
            "errors": errors
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))