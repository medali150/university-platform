"""
Script to create sample subjects for testing the subjects API.
"""

import asyncio
from prisma import Prisma
import sys
import os

# Add the parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

async def create_sample_subjects():
    """Create sample subjects for testing."""
    
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("🔍 Creating sample subjects...")
        
        # Get teachers and levels
        teachers = await prisma.enseignant.find_many()
        niveaux = await prisma.niveau.find_many()
        
        if not teachers:
            print("❌ No teachers found. Please run fix_user_relationships.py first.")
            return
        
        if not niveaux:
            print("❌ No levels found. Please run fix_user_relationships.py first.")
            return
        
        # Sample subjects to create
        sample_subjects = [
            {
                "nom": "Mathématiques Fondamentales",
                "id_niveau": niveaux[0].id,
                "id_enseignant": teachers[0].id if teachers else None
            },
            {
                "nom": "Algorithmique et Structures de Données",
                "id_niveau": niveaux[0].id,
                "id_enseignant": teachers[0].id if teachers else None
            },
            {
                "nom": "Programmation Orientée Objet",
                "id_niveau": niveaux[0].id,
                "id_enseignant": teachers[0].id if teachers else None
            },
            {
                "nom": "Base de Données",
                "id_niveau": niveaux[0].id,
                "id_enseignant": teachers[0].id if teachers else None
            },
            {
                "nom": "Réseaux Informatiques",
                "id_niveau": niveaux[0].id,
                "id_enseignant": teachers[0].id if teachers else None
            }
        ]
        
        created_count = 0
        
        for subject_data in sample_subjects:
            # Check if subject already exists
            existing = await prisma.matiere.find_first(
                where={"nom": subject_data["nom"]}
            )
            
            if not existing:
                subject = await prisma.matiere.create(subject_data)
                print(f"✅ Created subject: {subject.nom}")
                created_count += 1
            else:
                print(f"ℹ️  Subject already exists: {subject_data['nom']}")
        
        print(f"\n🎉 Created {created_count} new subjects!")
        
        # Verify
        total_subjects = await prisma.matiere.count()
        print(f"📊 Total subjects in database: {total_subjects}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(create_sample_subjects())