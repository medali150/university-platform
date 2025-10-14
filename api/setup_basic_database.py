"""
Simple Database Setup Script
Creates basic university database with departments and subjects including coefficients
"""
import asyncio
import sys
import subprocess
from pathlib import Path

def generate_prisma_client():
    """Generate Prisma client"""
    try:
        print("🔄 Generating Prisma client...")
        result = subprocess.run([sys.executable, "-m", "prisma", "generate"], 
                              capture_output=True, text=True, check=True)
        print("✅ Prisma client generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate Prisma client: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error generating Prisma client: {str(e)}")
        return False

def push_schema():
    """Push schema to database"""
    try:
        print("🔄 Pushing schema to database...")
        result = subprocess.run([sys.executable, "-m", "prisma", "db", "push"], 
                              capture_output=True, text=True, check=True)
        print("✅ Schema pushed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push schema: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error pushing schema: {str(e)}")
        return False

async def create_basic_data():
    """Create basic university data"""
    try:
        # Import Prisma after client generation
        from prisma import Prisma
        
        print("🔄 Connecting to database...")
        db = Prisma()
        await db.connect()
        
        print("🔄 Creating basic university data...")
        
        # Create 4 departments
        departments_data = [
            {"nom": "Génie Mécanique", "description": "Département de Génie Mécanique"},
            {"nom": "Génie Électrique", "description": "Département de Génie Électrique"},
            {"nom": "Génie Civil", "description": "Département de Génie Civil"},
            {"nom": "Technologie d'Informatique", "description": "Département de Technologie d'Informatique"}
        ]
        
        departments = []
        for dept_data in departments_data:
            dept = await db.departement.create(data=dept_data)
            departments.append(dept)
            print(f"✅ Created department: {dept.nom}")
        
        # Create some specialities
        specialites_data = [
            {"nom": "Mécanique Générale", "departement_id": departments[0].id},
            {"nom": "Construction Mécanique", "departement_id": departments[0].id},
            {"nom": "Électronique", "departement_id": departments[1].id},
            {"nom": "Électrotechnique", "departement_id": departments[1].id},
            {"nom": "Génie Civil", "departement_id": departments[2].id},
            {"nom": "Travaux Publics", "departement_id": departments[2].id},
            {"nom": "Développement d'Applications", "departement_id": departments[3].id},
            {"nom": "Réseaux et Sécurité", "departement_id": departments[3].id}
        ]
        
        specialites = []
        for spec_data in specialites_data:
            spec = await db.specialite.create(data=spec_data)
            specialites.append(spec)
            print(f"✅ Created speciality: {spec.nom}")
        
        # Create some subjects with coefficients
        matieres_data = [
            {"nom": "Mathématiques", "coefficient": 3.0, "specialite_id": specialites[0].id},
            {"nom": "Physique", "coefficient": 2.5, "specialite_id": specialites[0].id},
            {"nom": "Mécanique des Fluides", "coefficient": 2.0, "specialite_id": specialites[0].id},
            {"nom": "Électricité Générale", "coefficient": 3.0, "specialite_id": specialites[2].id},
            {"nom": "Électronique Analogique", "coefficient": 2.5, "specialite_id": specialites[2].id},
            {"nom": "Résistance des Matériaux", "coefficient": 3.0, "specialite_id": specialites[4].id},
            {"nom": "Construction", "coefficient": 2.5, "specialite_id": specialites[4].id},
            {"nom": "Programmation", "coefficient": 3.0, "specialite_id": specialites[6].id},
            {"nom": "Base de Données", "coefficient": 2.5, "specialite_id": specialites[6].id},
        ]
        
        for matiere_data in matieres_data:
            matiere = await db.matiere.create(data=matiere_data)
            print(f"✅ Created subject: {matiere.nom} (coefficient: {matiere.coefficient})")
        
        print("\n🎉 Basic university database created successfully!")
        print("📊 Summary:")
        print(f"   - {len(departments)} departments created")
        print(f"   - {len(specialites)} specialities created")
        print(f"   - {len(matieres_data)} subjects with coefficients created")
        
        await db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database data: {str(e)}")
        return False

async def main():
    """Main setup function"""
    print("🚀 University Database Basic Setup")
    print("=" * 40)
    
    # Step 1: Generate Prisma client
    if not generate_prisma_client():
        print("❌ Setup failed at Prisma client generation")
        return False
    
    # Step 2: Push schema
    if not push_schema():
        print("❌ Setup failed at schema push")
        return False
    
    # Step 3: Create basic data
    if not await create_basic_data():
        print("❌ Setup failed at data creation")
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("🚀 You can now start the server with: uvicorn app.main:app --reload")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)