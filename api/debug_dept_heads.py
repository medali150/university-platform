#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.prisma_client import get_prisma

async def check_department_heads():
    """Check existing department heads and departments"""
    try:
        prisma = await get_prisma()
        
        print("=== CHECKING DEPARTMENTS ===")
        departments = await prisma.departement.find_many()
        print(f"Total departments: {len(departments)}")
        for dept in departments:
            print(f"- ID: {dept.id}, Name: {dept.nom}")
        
        print("\n=== CHECKING DEPARTMENT HEADS ===")
        dept_heads = await prisma.chefdepartement.find_many(
            include={
                "utilisateur": True,
                "departement": True
            }
        )
        print(f"Total department heads: {len(dept_heads)}")
        for head in dept_heads:
            print(f"- User: {head.utilisateur.prenom} {head.utilisateur.nom}")
            print(f"  Department: {head.departement.nom} (ID: {head.id_departement})")
            print(f"  User ID: {head.id_utilisateur}")
            print()
        
        # Check the specific department ID from the error
        target_dept_id = "cmgf7np350000bmb0jj5odswj"
        target_dept = await prisma.departement.find_unique(where={"id": target_dept_id})
        
        print(f"\n=== CHECKING TARGET DEPARTMENT ===")
        if target_dept:
            print(f"Target department found: {target_dept.nom} (ID: {target_dept.id})")
            
            # Check if this department already has a head
            existing_head = await prisma.chefdepartement.find_unique(
                where={"id_departement": target_dept_id},
                include={"utilisateur": True}
            )
            
            if existing_head:
                print(f"⚠️  This department already has a head: {existing_head.utilisateur.prenom} {existing_head.utilisateur.nom}")
                print("This explains the 500 error - unique constraint violation!")
                return "DUPLICATE_HEAD"
            else:
                print("✅ This department has no head assigned yet")
                return "OK"
        else:
            print(f"❌ Target department ID {target_dept_id} not found!")
            return "DEPT_NOT_FOUND"
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return "ERROR"

if __name__ == "__main__":
    result = asyncio.run(check_department_heads())