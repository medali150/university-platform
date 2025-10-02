#!/usr/bin/env python3
"""
Setup basic data for testing
"""

import asyncio
from app.db.prisma_client import get_prisma

async def setup_basic_data():
    """Create basic departments and test data"""
    print("🔧 Setting up basic test data...")
    
    try:
        # Get prisma client
        prisma = await get_prisma()
        
        # Check current departments
        existing_depts = await prisma.departement.find_many()
        print(f"📊 Current departments: {len(existing_depts)}")
        
        if len(existing_depts) == 0:
            print("➕ Creating default departments...")
            
            # Create some basic departments
            departments = [
                {"nom": "Informatique"},
                {"nom": "Mathématiques"},
                {"nom": "Physique"},
                {"nom": "Chimie"}
            ]
            
            for dept_data in departments:
                dept = await prisma.departement.create(data=dept_data)
                print(f"✅ Created department: {dept.nom} (ID: {dept.id})")
        else:
            print("✅ Departments already exist:")
            for dept in existing_depts:
                print(f"  - {dept.nom} (ID: {dept.id})")
        
        # Check specialties
        existing_specs = await prisma.specialite.find_many()
        print(f"📊 Current specialties: {len(existing_specs)}")
        
        if len(existing_specs) == 0 and len(existing_depts) > 0:
            print("➕ Creating default specialties...")
            
            # Get first department for creating specialties
            first_dept = existing_depts[0] if existing_depts else await prisma.departement.find_first()
            
            if first_dept:
                specialties = [
                    {"nom": "Génie Logiciel", "id_departement": first_dept.id},
                    {"nom": "Réseaux et Sécurité", "id_departement": first_dept.id}
                ]
                
                for spec_data in specialties:
                    spec = await prisma.specialite.create(data=spec_data)
                    print(f"✅ Created specialty: {spec.nom} (ID: {spec.id})")
        
        # Check groups
        existing_groups = await prisma.groupe.find_many()
        print(f"📊 Current groups: {len(existing_groups)}")
        
        print("🎉 Basic data setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up data: {e}")

if __name__ == "__main__":
    asyncio.run(setup_basic_data())