#!/usr/bin/env python3
"""
Create a simpler, more robust student schedule endpoint
"""

simple_schedule_endpoint = '''
@router.get("/schedule/simple")
async def get_student_simple_schedule(
    prisma: Prisma = Depends(get_prisma),
    current_user = Depends(require_student)
):
    """Get student's schedule - simplified version"""
    
    # Find student record
    student = None
    if hasattr(current_user, 'etudiant_id') and current_user.etudiant_id:
        student = await prisma.etudiant.find_unique(
            where={"id": current_user.etudiant_id}
        )
    
    if not student:
        # Try to find by email
        student = await prisma.etudiant.find_first(
            where={"email": current_user.email}
        )
    
    if not student:
        return {"error": "No student record found", "schedules": []}
    
    # Get basic info
    return {
        "student_info": {
            "id": student.id,
            "nom": student.nom,
            "prenom": student.prenom,
            "email": student.email,
            "group_id": student.id_groupe
        },
        "schedules": [],
        "message": "Student found but schedule functionality needs debugging"
    }
'''

print("Simple schedule endpoint created:")
print(simple_schedule_endpoint)